"""Step 1: collect random-policy rollouts.

Each episode is saved as <run>/episodes/ep_XXXXXX.npz containing
  obs:     uint8 (N+1, 64, 64, 3)   frames o_0 .. o_N
  actions: float32 (N, A)           controller-space actions a_0 .. a_{N-1}
  dones:   bool (N,)                dones[t] = episode terminated after a_t

Shard large collections across processes with --start/--episodes.
"""

import argparse
import os

import numpy as np

from config import Paths, add_common_args, load_config
from envs import RandomPolicy, make_env, preprocess, to_env_action


def main():
    parser = add_common_args(argparse.ArgumentParser(description=__doc__))
    parser.add_argument("--episodes", type=int, default=10000)
    parser.add_argument("--start", type=int, default=0, help="first episode index (for sharding)")
    args = parser.parse_args()
    cfg, run_dir = load_config(args)
    out_dir = Paths(run_dir).episodes
    os.makedirs(out_dir, exist_ok=True)

    env = make_env(cfg)
    for i in range(args.start, args.start + args.episodes):
        path = os.path.join(out_dir, f"ep_{i:06d}.npz")
        if os.path.exists(path):
            continue
        rng = np.random.default_rng(i)
        policy = RandomPolicy(cfg, rng)
        obs, _ = env.reset(seed=i)
        frames, actions, dones = [preprocess(obs, cfg)], [], []
        for _ in range(cfg.max_steps):
            a = policy()
            obs, _, terminated, truncated, _ = env.step(to_env_action(a, cfg, env.action_space))
            frames.append(preprocess(obs, cfg))
            actions.append(a)
            dones.append(terminated)
            if terminated or truncated:
                break
        np.savez_compressed(
            path,
            obs=np.stack(frames),
            actions=np.stack(actions).astype(np.float32),
            dones=np.array(dones, dtype=bool),
        )
        print(f"episode {i}: {len(actions)} steps, terminated={dones[-1]}")
    env.close()


if __name__ == "__main__":
    main()
