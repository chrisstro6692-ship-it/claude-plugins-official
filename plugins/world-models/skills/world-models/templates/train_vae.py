"""Step 2: train V (ConvVAE) on individual frames.

The full frame set does not fit in memory (10k episodes x 1000 frames), so
episodes are streamed in shuffled chunks and frames are shuffled within a chunk.
"""

import argparse
import glob
import os

import numpy as np
import torch

from config import Paths, add_common_args, load_config
from models import VAE, frames_to_tensor, vae_loss


def frame_batches(files, batch_size, files_per_chunk, rng):
    files = list(files)
    rng.shuffle(files)
    for i in range(0, len(files), files_per_chunk):
        frames = np.concatenate([np.load(f)["obs"] for f in files[i : i + files_per_chunk]])
        rng.shuffle(frames)
        for j in range(0, len(frames) - batch_size + 1, batch_size):
            yield frames[j : j + batch_size]


def main():
    parser = add_common_args(argparse.ArgumentParser(description=__doc__))
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--files-per-chunk", type=int, default=64)
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = parser.parse_args()
    cfg, run_dir = load_config(args)
    paths = Paths(run_dir)

    files = sorted(glob.glob(os.path.join(paths.episodes, "*.npz")))
    if not files:
        raise SystemExit(f"no episodes in {paths.episodes}; run collect.py first")
    vae = VAE(cfg.z_dim).to(args.device)
    opt = torch.optim.Adam(vae.parameters(), lr=args.lr)
    rng = np.random.default_rng(0)

    step = 0
    for epoch in range(args.epochs):
        for frames in frame_batches(files, args.batch_size, args.files_per_chunk, rng):
            x = frames_to_tensor(frames, args.device)
            recon, mu, logvar = vae(x)
            loss, r, kl = vae_loss(recon, x, mu, logvar, cfg.kl_tolerance)
            opt.zero_grad()
            loss.backward()
            opt.step()
            if step % 100 == 0:
                print(f"epoch {epoch} step {step}: loss {loss.item():.1f} (recon {r.item():.1f}, kl {kl.item():.2f})")
            step += 1
        torch.save(vae.state_dict(), paths.vae)
    print(f"saved {paths.vae}")


if __name__ == "__main__":
    main()
