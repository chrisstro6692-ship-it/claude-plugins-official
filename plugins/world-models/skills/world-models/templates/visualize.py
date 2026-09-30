"""Diagnostics: look at V's reconstructions and M's dreams before blaming C.

  python visualize.py --preset doom recon            # originals over reconstructions
  python visualize.py --preset doom dream --set tau=1.15 [--controller runs/doom/controller.npy]
"""

import argparse
import glob
import os

import numpy as np
import torch
from PIL import Image

from config import Paths, add_common_args, load_config
from models import Controller, frames_to_tensor, load_rnn, load_vae
from rollouts import load_initial_latents, rollout_dream


def to_image(x):
    """float (N, 3, 64, 64) -> uint8 (64, N*64, 3) strip."""
    x = (x.clamp(0, 1) * 255).byte().permute(0, 2, 3, 1).numpy()
    return np.concatenate(list(x), axis=1)


@torch.no_grad()
def main():
    parser = add_common_args(argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter))
    parser.add_argument("what", choices=["recon", "dream"])
    parser.add_argument("--n", type=int, default=12, help="frames per strip")
    parser.add_argument("--every", type=int, default=10, help="dream: keep every k-th frame")
    parser.add_argument("--controller", default=None, help="dream: controller .npy (default: zero policy)")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    cfg, run_dir = load_config(args)
    paths = Paths(run_dir)
    vae = load_vae(cfg, paths.vae)
    rng = np.random.default_rng(args.seed)
    torch.manual_seed(args.seed)

    if args.what == "recon":
        files = sorted(glob.glob(os.path.join(paths.episodes, "*.npz")))
        obs = np.load(files[rng.integers(len(files))])["obs"]
        frames = obs[np.sort(rng.choice(len(obs), size=min(args.n, len(obs)), replace=False))]
        x = frames_to_tensor(frames, "cpu")
        mu, _ = vae.encode(x)
        grid = np.concatenate([to_image(x), to_image(vae.decode(mu))], axis=0)
    else:
        params = np.load(args.controller) if args.controller else None
        controller = Controller(cfg.controller_in_dim, cfg.action_dim, params)
        steps, zs = rollout_dream(cfg, load_rnn(cfg, paths.rnn), controller,
                                  load_initial_latents(paths.series), cfg.tau, rng, return_latents=True)
        print(f"dream episode lasted {steps} steps at tau={cfg.tau}")
        grid = to_image(vae.decode(zs[:: args.every][: args.n]))

    out = os.path.join(run_dir, f"{args.what}.png")
    Image.fromarray(grid).save(out)
    print(f"saved {out}")


if __name__ == "__main__":
    main()
