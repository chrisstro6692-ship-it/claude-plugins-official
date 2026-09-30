"""Step 3: encode every episode with V into latent series for training M.

Stores mu and logvar (float16), not a sampled z. train_mdnrnn.py resamples
z = mu + sigma * eps each time a sequence is drawn, as the paper does.
"""

import argparse
import glob
import os

import numpy as np
import torch

from config import Paths, add_common_args, load_config
from models import frames_to_tensor, load_vae


@torch.no_grad()
def main():
    parser = add_common_args(argparse.ArgumentParser(description=__doc__))
    parser.add_argument("--batch-size", type=int, default=1000)
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = parser.parse_args()
    cfg, run_dir = load_config(args)
    paths = Paths(run_dir)
    os.makedirs(paths.series, exist_ok=True)
    vae = load_vae(cfg, paths.vae, args.device)

    for f in sorted(glob.glob(os.path.join(paths.episodes, "*.npz"))):
        out = os.path.join(paths.series, os.path.basename(f))
        if os.path.exists(out):
            continue
        ep = np.load(f)
        mus, logvars = [], []
        for i in range(0, len(ep["obs"]), args.batch_size):
            mu, logvar = vae.encode(frames_to_tensor(ep["obs"][i : i + args.batch_size], args.device))
            mus.append(mu.cpu())
            logvars.append(logvar.cpu())
        np.savez_compressed(
            out,
            mu=torch.cat(mus).numpy().astype(np.float16),
            logvar=torch.cat(logvars).numpy().astype(np.float16),
            actions=ep["actions"],
            dones=ep["dones"],
        )
    print(f"wrote latent series to {paths.series}")


if __name__ == "__main__":
    main()
