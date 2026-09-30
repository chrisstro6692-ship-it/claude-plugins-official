# World Models scaffold (PyTorch)

A compact reimplementation of Ha & Schmidhuber's *World Models* (2018):
V (ConvVAE) → M (MDN-RNN) → C (linear, CMA-ES).

```
pip install -r requirements.txt
```

## Pipeline

Every script takes `--preset {carracing,doom}`, `--run-dir` (defaults to
`runs/<preset>`), and `--set key=value` to override config fields.

| Step | Command | Output |
|---|---|---|
| 1. Collect random rollouts | `python collect.py --preset carracing --episodes 10000` | `episodes/*.npz` |
| 2. Train V | `python train_vae.py --preset carracing` | `vae.pt` |
| 3. Encode episodes | `python encode.py --preset carracing` | `series/*.npz` |
| 4. Train M | `python train_mdnrnn.py --preset carracing` | `mdnrnn.pt` |
| 5. Evolve C | `python train_controller.py --preset carracing --mode real` | `controller.npy`, `controller_log.jsonl` |
| 6. Evaluate | `python train_controller.py --preset carracing --eval 100` | mean ± std |

Doom (learning inside the dream) swaps step 5 for:

```
python train_controller.py --preset doom --mode dream --set tau=1.15
python train_controller.py --preset doom --eval 100
```

Shard step 1 across processes with `--start 0 --episodes 2500`,
`--start 2500 --episodes 2500`, and so on.

## Useful variations

- V-only baseline: `--set controller_inputs=z` (you can skip steps 3–4).
- Temperature sweep: train C at several `tau` values and compare **real-env**
  scores from `--eval`.
- Look before tuning: `python visualize.py recon` and
  `python visualize.py dream --set tau=1.15`.
- M never ends dream episodes: retrain with `--done-pos-weight 10`.

## Porting to a new environment

1. Add a preset in `config.py` (`env_id`, `action_dim`, `max_steps`, `crop`).
2. Adjust `to_env_action` in `envs.py` if the default mapping doesn't fit the
   action space.
3. For dream training, set `predict_done=True`. If the task reward is not
   "steps survived", also give M a reward head and use it in `rollout_dream`.

## Files

- `config.py` defines the presets and CLI helpers.
- `envs.py` holds env creation, 64×64 preprocessing, action mapping, and the
  random policy.
- `models.py` contains the VAE, the MDN-RNN (with temperature sampling), and
  the controller.
- `rollouts.py` runs rollouts in the real env and in the dream.
- `collect.py`, `train_vae.py`, `encode.py`, `train_mdnrnn.py`, and
  `train_controller.py` are the pipeline scripts.
- `visualize.py` renders reconstruction and dream strips.
