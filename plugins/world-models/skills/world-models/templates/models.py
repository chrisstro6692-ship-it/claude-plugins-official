"""V (ConvVAE), M (MDN-RNN), and C (linear controller)."""

import math

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

LOG_SQRT_2PI = 0.5 * math.log(2 * math.pi)


# ---------------------------------------------------------------- V ----------


class VAE(nn.Module):
    def __init__(self, z_dim):
        super().__init__()
        self.z_dim = z_dim
        self.encoder = nn.Sequential(
            nn.Conv2d(3, 32, 4, stride=2), nn.ReLU(),
            nn.Conv2d(32, 64, 4, stride=2), nn.ReLU(),
            nn.Conv2d(64, 128, 4, stride=2), nn.ReLU(),
            nn.Conv2d(128, 256, 4, stride=2), nn.ReLU(),
            nn.Flatten(),
        )
        self.fc_mu = nn.Linear(1024, z_dim)
        self.fc_logvar = nn.Linear(1024, z_dim)
        self.fc_dec = nn.Linear(z_dim, 1024)
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(1024, 128, 5, stride=2), nn.ReLU(),
            nn.ConvTranspose2d(128, 64, 5, stride=2), nn.ReLU(),
            nn.ConvTranspose2d(64, 32, 6, stride=2), nn.ReLU(),
            nn.ConvTranspose2d(32, 3, 6, stride=2), nn.Sigmoid(),
        )

    def encode(self, x):
        h = self.encoder(x)
        return self.fc_mu(h), self.fc_logvar(h)

    def decode(self, z):
        return self.decoder(self.fc_dec(z).view(-1, 1024, 1, 1))

    def forward(self, x):
        mu, logvar = self.encode(x)
        z = mu + torch.randn_like(mu) * torch.exp(0.5 * logvar)
        return self.decode(z), mu, logvar


def vae_loss(recon, x, mu, logvar, kl_tolerance):
    recon_loss = (recon - x).pow(2).sum(dim=(1, 2, 3)).mean()
    kl = -0.5 * (1 + logvar - mu.pow(2) - logvar.exp()).sum(dim=1)
    kl = kl.clamp(min=kl_tolerance * mu.shape[1]).mean()
    return recon_loss + kl, recon_loss, kl


def frames_to_tensor(frames, device):
    """uint8 (N, 64, 64, 3) -> float (N, 3, 64, 64) in [0, 1]."""
    x = torch.as_tensor(np.asarray(frames), device=device)
    return x.permute(0, 3, 1, 2).float().div_(255.0)


# ---------------------------------------------------------------- M ----------


class MDNRNN(nn.Module):
    """LSTM with a factorized mixture-density head over the next latent.

    Every latent dimension gets its own K-component 1-D Gaussian mixture, as in
    the original implementation.
    """

    def __init__(self, z_dim, action_dim, hidden, n_mixtures=5, predict_done=False):
        super().__init__()
        self.z_dim, self.k, self.predict_done = z_dim, n_mixtures, predict_done
        self.lstm = nn.LSTM(z_dim + action_dim, hidden, batch_first=True)
        self.head = nn.Linear(hidden, 3 * n_mixtures * z_dim + int(predict_done))

    def forward(self, z, a, state=None):
        """z: (B, T, Z), a: (B, T, A). Returns mixture params for z_{t+1}."""
        out, state = self.lstm(torch.cat([z, a], dim=-1), state)
        p = self.head(out)
        b, t = p.shape[:2]
        mix = p[..., : 3 * self.k * self.z_dim].view(b, t, 3, self.z_dim, self.k)
        logit_pi, mu, logsigma = mix.unbind(dim=2)
        logsigma = logsigma.clamp(-7.0, 3.0)
        done_logit = p[..., -1] if self.predict_done else None
        return (logit_pi, mu, logsigma, done_logit), state


def mdn_nll(logit_pi, mu, logsigma, target):
    """Per-element negative log-likelihood, shape (B, T, Z)."""
    t = target.unsqueeze(-1)
    log_prob = -0.5 * ((t - mu) / logsigma.exp()).pow(2) - logsigma - LOG_SQRT_2PI
    return -torch.logsumexp(F.log_softmax(logit_pi, dim=-1) + log_prob, dim=-1)


def mdn_sample(logit_pi, mu, logsigma, tau=1.0):
    """Sample z from mixture params of shape (B, Z, K) with temperature tau.

    tau scales the mixture logits (1/tau) and the component stds (sqrt(tau)).
    tau < 1 is closer to deterministic and prone to mode collapse. tau > 1
    gives a harder, noisier dream that is harder for C to exploit.
    """
    b, z, k = logit_pi.shape
    pi = F.softmax(logit_pi / tau, dim=-1).reshape(-1, k)
    idx = torch.multinomial(pi, 1).view(b, z, 1)
    mu_k = mu.gather(-1, idx).squeeze(-1)
    sigma_k = logsigma.gather(-1, idx).squeeze(-1).exp()
    return mu_k + sigma_k * math.sqrt(tau) * torch.randn_like(mu_k)


# ---------------------------------------------------------------- C ----------


class Controller:
    """a = tanh(W x + b). Pure numpy so CMA-ES workers stay light."""

    def __init__(self, in_dim, out_dim, params=None):
        self.in_dim, self.out_dim = in_dim, out_dim
        self.set_params(np.zeros(self.n_params(in_dim, out_dim)) if params is None else params)

    @staticmethod
    def n_params(in_dim, out_dim):
        return in_dim * out_dim + out_dim

    def set_params(self, flat):
        flat = np.asarray(flat, dtype=np.float32)
        n = self.in_dim * self.out_dim
        self.w = flat[:n].reshape(self.out_dim, self.in_dim)
        self.b = flat[n:]

    def act(self, x):
        return np.tanh(self.w @ x + self.b)


def controller_features(cfg, z, state):
    """Build C's input from z (Z,) and the LSTM state ((1,1,H), (1,1,H))."""
    h, c = state
    parts = [z]
    if "h" in cfg.controller_inputs:
        parts.append(h.reshape(-1))
    if "c" in cfg.controller_inputs:
        parts.append(c.reshape(-1))
    return torch.cat(parts).numpy()


def zero_state(cfg, batch=1):
    zeros = torch.zeros(1, batch, cfg.rnn_hidden)
    return zeros, zeros.clone()


def load_vae(cfg, path, device="cpu"):
    vae = VAE(cfg.z_dim).to(device)
    vae.load_state_dict(torch.load(path, map_location=device))
    return vae.eval()


def load_rnn(cfg, path, device="cpu"):
    rnn = MDNRNN(cfg.z_dim, cfg.action_dim, cfg.rnn_hidden, cfg.n_mixtures, cfg.predict_done)
    rnn.load_state_dict(torch.load(path, map_location=device))
    return rnn.to(device).eval()
