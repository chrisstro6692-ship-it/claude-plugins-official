"""Rollouts of V + M + C in the real environment and inside M's dream."""

import glob
import os

import numpy as np
import torch

from envs import preprocess, to_env_action
from models import controller_features, frames_to_tensor, mdn_sample, zero_state


@torch.no_grad()
def rollout_real(cfg, env, vae, rnn, controller, seed):
    """Cumulative reward of one real episode. V encodes, M remembers, C acts."""
    obs, _ = env.reset(seed=seed)
    state = zero_state(cfg)
    total = 0.0
    for _ in range(cfg.max_steps):
        mu, _ = vae.encode(frames_to_tensor(preprocess(obs, cfg)[None], "cpu"))
        z = mu[0]
        a = controller.act(controller_features(cfg, z, state))
        obs, reward, terminated, truncated, _ = env.step(to_env_action(a, cfg, env.action_space))
        total += float(reward)
        if terminated or truncated:
            break
        if rnn is not None:
            _, state = rnn.lstm(torch.cat([z, torch.from_numpy(a)]).view(1, 1, -1), state)
    return total


def load_initial_latents(series_dir, limit=2000):
    """(mu, logvar) of first frames, used to start dream episodes."""
    mus, logvars = [], []
    for f in sorted(glob.glob(os.path.join(series_dir, "*.npz")))[:limit]:
        d = np.load(f)
        mus.append(d["mu"][0])
        logvars.append(d["logvar"][0])
    if not mus:
        raise SystemExit(f"no latent series in {series_dir}; run encode.py first")
    return np.stack(mus).astype(np.float32), np.stack(logvars).astype(np.float32)


@torch.no_grad()
def rollout_dream(cfg, rnn, controller, initial_latents, tau, rng, return_latents=False):
    """Steps survived inside M's sampled environment (survival reward).

    The dream sees no pixels: z_{t+1} is sampled from M at temperature tau and
    the episode ends when M's done head fires or max_steps is reached.
    """
    mus, logvars = initial_latents
    i = rng.integers(len(mus))
    z = torch.from_numpy(mus[i] + np.exp(0.5 * logvars[i]) * rng.standard_normal(mus[i].shape).astype(np.float32))
    state = zero_state(cfg)
    zs = [z]
    steps = 0
    for steps in range(1, cfg.max_steps + 1):
        a = controller.act(controller_features(cfg, z, state))
        (logit_pi, mu, logsigma, done_logit), state = rnn(z.view(1, 1, -1), torch.from_numpy(a).view(1, 1, -1), state)
        z = mdn_sample(logit_pi[:, 0], mu[:, 0], logsigma[:, 0], tau)[0]
        zs.append(z)
        if done_logit is not None and torch.sigmoid(done_logit[0, 0]) > 0.5:
            break
    return (steps, torch.stack(zs)) if return_latents else steps
