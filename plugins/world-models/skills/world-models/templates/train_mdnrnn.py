"""Step 4: train M (MDN-RNN) to model P(z_{t+1}, done_t | a_t, z_t, h_t).

Training draws random windows of --seq-len transitions. Episodes shorter than
the window are zero-padded and masked out of the loss.
"""

import argparse
import glob
import os

import numpy as np
import torch
import torch.nn.functional as F

from config import Paths, add_common_args, load_config
from models import MDNRNN, mdn_nll


def load_series(series_dir):
    episodes = []
    for f in sorted(glob.glob(os.path.join(series_dir, "*.npz"))):
        d = np.load(f)
        episodes.append({k: d[k] for k in ("mu", "logvar", "actions", "dones")})
    if not episodes:
        raise SystemExit(f"no latent series in {series_dir}; run encode.py first")
    return episodes


def sample_batch(episodes, batch_size, seq_len, cfg, rng):
    z_in = np.zeros((batch_size, seq_len, cfg.z_dim), np.float32)
    z_out = np.zeros_like(z_in)
    a_in = np.zeros((batch_size, seq_len, cfg.action_dim), np.float32)
    done = np.zeros((batch_size, seq_len), np.float32)
    mask = np.zeros((batch_size, seq_len), np.float32)
    for i in range(batch_size):
        ep = episodes[rng.integers(len(episodes))]
        n = len(ep["actions"])
        s = int(rng.integers(max(1, n - seq_len + 1)))
        t = min(seq_len, n - s)
        mu = ep["mu"][s : s + t + 1].astype(np.float32)
        sigma = np.exp(0.5 * ep["logvar"][s : s + t + 1].astype(np.float32))
        z = mu + sigma * rng.standard_normal(mu.shape).astype(np.float32)
        z_in[i, :t], z_out[i, :t] = z[:-1], z[1:]
        a_in[i, :t] = ep["actions"][s : s + t]
        done[i, :t] = ep["dones"][s : s + t]
        mask[i, :t] = 1
    return [torch.from_numpy(x) for x in (z_in, a_in, z_out, done, mask)]


def main():
    parser = add_common_args(argparse.ArgumentParser(description=__doc__))
    parser.add_argument("--steps", type=int, default=4000)
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument("--seq-len", type=int, default=500)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--grad-clip", type=float, default=1.0)
    parser.add_argument("--done-pos-weight", type=float, default=1.0,
                        help="upweight rare terminal steps if M never predicts done")
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = parser.parse_args()
    cfg, run_dir = load_config(args)
    paths = Paths(run_dir)

    episodes = load_series(paths.series)
    rnn = MDNRNN(cfg.z_dim, cfg.action_dim, cfg.rnn_hidden, cfg.n_mixtures, cfg.predict_done).to(args.device)
    opt = torch.optim.Adam(rnn.parameters(), lr=args.lr)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, args.steps, eta_min=args.lr * 0.1)
    rng = np.random.default_rng(0)
    pos_weight = torch.tensor(args.done_pos_weight, device=args.device)

    for step in range(args.steps):
        z_in, a_in, z_out, done, mask = (
            x.to(args.device) for x in sample_batch(episodes, args.batch_size, args.seq_len, cfg, rng)
        )
        (logit_pi, mu, logsigma, done_logit), _ = rnn(z_in, a_in)
        n_valid = mask.sum()
        z_loss = (mdn_nll(logit_pi, mu, logsigma, z_out).mean(-1) * mask).sum() / n_valid
        loss = z_loss
        if cfg.predict_done:
            d_loss = F.binary_cross_entropy_with_logits(done_logit, done, pos_weight=pos_weight, reduction="none")
            d_loss = (d_loss * mask).sum() / n_valid
            loss = loss + d_loss
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(rnn.parameters(), args.grad_clip)
        opt.step()
        sched.step()
        if step % 50 == 0:
            msg = f"step {step}: z_nll {z_loss.item():.4f}"
            if cfg.predict_done:
                msg += f" done_bce {d_loss.item():.4f}"
            print(msg)
        if step % 1000 == 999:
            torch.save(rnn.state_dict(), paths.rnn)
    torch.save(rnn.state_dict(), paths.rnn)
    print(f"saved {paths.rnn}")


if __name__ == "__main__":
    main()
