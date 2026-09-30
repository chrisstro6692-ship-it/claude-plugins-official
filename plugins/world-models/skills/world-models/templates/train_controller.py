"""Step 5: evolve C with CMA-ES, in the real env or inside M's dream.

  python train_controller.py --preset carracing --mode real
  python train_controller.py --preset doom --mode dream --set tau=1.15
  python train_controller.py --preset doom --eval 100     # real-env score

Fitness is the mean return over --rollouts episodes that share seeds across
the population (common random numbers), which reduces ranking noise.
"""

import argparse
import json
import multiprocessing as mp
import os

import cma
import numpy as np
import torch

from config import Paths, add_common_args, load_config
from envs import make_env
from models import Controller, load_rnn, load_vae
from rollouts import load_initial_latents, rollout_dream, rollout_real

_W = {}


def _needs_rnn(cfg, mode):
    return mode == "dream" or cfg.controller_inputs != "z"


def _check_inputs(cfg, paths, mode):
    # A worker initializer that raises makes Pool respawn it forever, so fail here instead.
    required = [paths.rnn] if _needs_rnn(cfg, mode) else []
    required.append(paths.vae if mode == "real" else paths.series)
    missing = [p for p in required if not os.path.exists(p)]
    if missing:
        raise SystemExit(f"missing {', '.join(missing)}; run the earlier pipeline steps first")


def _init_worker(cfg, paths, mode):
    torch.set_num_threads(1)
    _W.update(cfg=cfg, mode=mode)
    _W["rnn"] = load_rnn(cfg, paths.rnn) if _needs_rnn(cfg, mode) else None
    if mode == "real":
        _W["env"] = make_env(cfg)
        _W["vae"] = load_vae(cfg, paths.vae)
    else:
        _W["init"] = load_initial_latents(paths.series)


def _evaluate(job):
    params, seed = job
    cfg = _W["cfg"]
    controller = Controller(cfg.controller_in_dim, cfg.action_dim, params)
    torch.manual_seed(seed)
    if _W["mode"] == "real":
        return rollout_real(cfg, _W["env"], _W["vae"], _W["rnn"], controller, seed)
    return rollout_dream(cfg, _W["rnn"], controller, _W["init"], cfg.tau, np.random.default_rng(seed))


def main():
    parser = add_common_args(argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter))
    parser.add_argument("--mode", choices=["real", "dream"], default="real")
    parser.add_argument("--generations", type=int, default=300)
    parser.add_argument("--popsize", type=int, default=64)
    parser.add_argument("--rollouts", type=int, default=16)
    parser.add_argument("--sigma0", type=float, default=0.1)
    parser.add_argument("--workers", type=int, default=os.cpu_count())
    parser.add_argument("--eval", type=int, default=0, metavar="N",
                        help="skip training; score the saved controller over N real-env rollouts")
    parser.add_argument("--params", default=None, help="controller .npy for --eval (default: run's controller.npy)")
    args = parser.parse_args()
    cfg, run_dir = load_config(args)
    paths = Paths(run_dir)
    n_params = Controller.n_params(cfg.controller_in_dim, cfg.action_dim)
    ctx = mp.get_context("spawn")

    _check_inputs(cfg, paths, "real" if args.eval else args.mode)
    if args.eval:
        params = np.load(args.params or paths.controller)
        with ctx.Pool(args.workers, _init_worker, (cfg, paths, "real")) as pool:
            returns = np.array(pool.map(_evaluate, [(params, 10**6 + i) for i in range(args.eval)]))
        print(f"real env, {args.eval} rollouts: {returns.mean():.1f} ± {returns.std():.1f}")
        return

    if args.mode == "dream" and not cfg.predict_done:
        raise SystemExit("dream training needs M to predict done; use --set predict_done=true and retrain M")

    print(f"C has {n_params} parameters ({cfg.controller_inputs} -> {cfg.action_dim}), mode={args.mode}"
          + (f", tau={cfg.tau}" if args.mode == "dream" else ""))
    es = cma.CMAEvolutionStrategy(np.zeros(n_params), args.sigma0, {"popsize": args.popsize, "seed": 1, "verbose": -9})
    rng = np.random.default_rng(1)
    best = -np.inf
    with ctx.Pool(args.workers, _init_worker, (cfg, paths, args.mode)) as pool, open(paths.log, "a") as log:
        for gen in range(args.generations):
            solutions = es.ask()
            seeds = rng.integers(2**31 - 1, size=args.rollouts)
            jobs = [(s, int(seed)) for s in solutions for seed in seeds]
            fitness = np.array(pool.map(_evaluate, jobs)).reshape(len(solutions), args.rollouts).mean(axis=1)
            es.tell(solutions, (-fitness).tolist())  # cma minimizes
            # The distribution mean is usually a more robust policy than the
            # luckiest candidate, so save it as the main controller.
            np.save(paths.controller, es.result.xfavorite)
            if fitness.max() > best:
                best = fitness.max()
                np.save(paths.controller.replace(".npy", "_best.npy"), solutions[int(fitness.argmax())])
            record = {"gen": gen, "mean": float(fitness.mean()), "max": float(fitness.max()), "best_ever": float(best)}
            log.write(json.dumps(record) + "\n")
            log.flush()
            print(record)


if __name__ == "__main__":
    main()
