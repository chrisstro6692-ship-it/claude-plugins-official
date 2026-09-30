# world-models

Build reinforcement learning agents in the style of Ha & Schmidhuber's
[*World Models*](https://worldmodels.github.io/) (2018).

## The idea

The agent is split into a large world model and a tiny controller:

- **V** is a convolutional VAE that compresses each 64×64 frame into a latent
  `z`.
- **M** is an MDN-RNN that predicts the distribution of the next `z` (and
  whether the episode ends) from the current `z`, the action, and its hidden
  state `h`.
- **C** is a linear map from `[z, h]` to an action, with about 1k parameters,
  evolved with CMA-ES.

V and M train without any reward. C is small enough for evolution strategies
to handle credit assignment directly. Because M is a generative model, C can
also train entirely **inside M's dream** and then transfer to the real
environment. Sampling the dream at a temperature `τ > 1` keeps C from
exploiting M's imperfections.

## What's included

| Skill | Type | Purpose |
|---|---|---|
| `world-models` | Auto-triggered | Architecture, training procedure, temperature and exploitation, iterative training, diagnostics, and exact paper hyperparameters |
| `scaffold-world-model` | `/world-models:scaffold-world-model [env] [dir]` | Copies a runnable PyTorch implementation and configures it for CarRacing, Doom Take Cover, or your Gymnasium env |

The scaffold covers random-rollout collection, VAE training, latent encoding,
MDN-RNN training with temperature sampling, CMA-ES controller training (real
env or dream, parallelized), evaluation, and diagnostic visualizations.

## Install

```
/plugin install world-models@claude-plugins-official
```

## Use

```
> /world-models:scaffold-world-model carracing ./wm
> Why does my dream-trained agent score 2000 in the dream but 200 in the real env?
> Adapt this world model to LunarLander from pixels
```
