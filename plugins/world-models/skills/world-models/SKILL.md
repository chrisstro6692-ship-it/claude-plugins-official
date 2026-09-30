---
name: world-models
description: This skill should be used when the user wants to build, train, debug, or explain a "world model" reinforcement learning agent in the style of Ha & Schmidhuber's "World Models" (2018) — a VAE vision model (V), an MDN-RNN memory model (M), and a small controller (C) trained with CMA-ES or another evolution strategy. Triggers include "world models", "VAE + MDN-RNN", "train an agent in its dream", "learning inside a dream", "latent-space simulator", "model-based RL from pixels", "CarRacing from pixels", "VizDoom take cover", "temperature tau for the dream environment", and "my agent exploits the learned model".
version: 1.0.0
---

# World Models (V + M + C)

Guidance for building agents that learn a compressed model of their environment
and act on its features, following Ha & Schmidhuber, *World Models* (2018,
arXiv:1803.10122). A runnable PyTorch scaffold lives in `templates/`. Copy it
with the `scaffold-world-model` skill rather than writing it from scratch.

## The architecture in one paragraph

The agent is split in three. **V** is a VAE that compresses each 64×64 RGB frame
into a latent vector `z_t` (32 dims for CarRacing, 64 for Doom). **M** is an LSTM
with a Mixture Density Network head that models `P(z_{t+1} | a_t, z_t, h_t)` as
a mixture of diagonal Gaussians, and optionally predicts `done`. **C** is a
single linear layer: `a_t = W_c [z_t, h_t] + b_c`. Nearly all parameters sit in
V and M, which are trained with backprop and never see the reward. C has around
10³ parameters and is the only part that sees the reward, so a gradient-free
optimizer (CMA-ES) can train it directly on the cumulative reward.

## Decide which variant the user needs

| Situation | Variant | C trains in |
|---|---|---|
| Real env is cheap and the goal is performance (CarRacing) | **Feature extraction** | Real env, using V and M as a frozen feature extractor |
| Real env is expensive or slow, or the user wants a learned simulator (Doom Take Cover) | **Dream training** | M's sampled latent environment, then deployed to the real env |
| A random policy never reaches the interesting states (pendulum swing-up, harder tasks) | **Iterative** | Alternate: collect with the current C, retrain M, retrain C |

Dream training needs M to also predict `done` (and the reward, if the reward is
not simply "survival time"). Otherwise the dream has no termination signal.

## Standard procedure

1. **Collect** about 10,000 rollouts with a random (or lightly biased random)
   policy. Store frames resized to 64×64 uint8, actions, and done flags.
2. **Train V** on individual frames. One pass over the data is typically
   enough. Use a KL tolerance (free bits, e.g. 0.5 nats per dim) so the KL term
   doesn't collapse the latent.
3. **Encode** every episode with V. Store `mu` and `logvar`, not a sampled `z`.
   Sample `z = mu + exp(logvar/2) * eps` fresh each epoch when training M. This
   acts as data augmentation and matches the paper.
4. **Train M** on sequences of `(z_t, a_t) -> z_{t+1}` (plus `done_{t+1}`) with
   the MDN negative log-likelihood. Images aren't needed at this stage, so long
   sequences and large batches fit on one GPU.
5. **Evolve C** with CMA-ES: population ~64, each candidate averaged over ~16
   rollouts, and fitness equal to the mean cumulative reward. Run rollouts in
   parallel across CPU cores.
6. **Evaluate** the best C over 100 fresh rollouts in the *real* environment.
   Report mean ± std, which is the convention in the paper and on the Gym
   leaderboards.

## Temperature and model exploitation

This is the part people get wrong. When C trains inside M it has access to M's
hidden state, which amounts to reading the game engine's memory. It will find
adversarial policies, such as moving so the monsters never fire, that work only
in the dream.

The fix is to sample the dream with temperature `τ`:

- Divide the mixture logits by `τ` before the softmax.
- Multiply each component's std by `sqrt(τ)`.

Low `τ` (≤ 0.5) collapses M onto one mode. The fireballs never appear, C scores
a perfect 2100 in the dream, and C does worse than random in reality. Somewhat
above 1 makes the dream harder than reality, so the policy transfers. The paper's
Doom sweep:

| τ | Dream score | Real score |
|---|---|---|
| 0.10 | 2086 ± 140 | 193 ± 58 |
| 0.50 | 2060 ± 277 | 196 ± 50 |
| 1.00 | 1145 ± 690 | 868 ± 511 |
| 1.15 | 918 ± 546 | **1092 ± 556** |
| 1.30 | 732 ± 269 | 753 ± 139 |

Treat `τ` as a hyperparameter. Always sweep it and pick it by **real-env** score,
never dream score. If dream score is far above real score, C is exploiting M.

## Diagnosing a failing agent

Check the components in this order. Each stage depends on the ones before it.

1. **V reconstructions.** Decode `mu` for held-out frames and look at them. If
   task-critical details are missing (the paper's CarRacing VAE dropped road
   tiles), no controller can fix it. Raise `z_dim`, train longer, or accept that
   V is task-agnostic by design.
2. **M rollouts.** Feed a real `z_0` and real actions to M in open loop at τ=1
   and decode the result. Objects should move plausibly, walls should block, and
   `done` should fire when the agent is hit. A flat, blurry dream means M
   underfit. An immediately "frozen" dream means mode collapse or a too-low τ.
3. **C with V only** (`a = W z + b`). This is a useful baseline. In the paper it
   drives, but wobbles (632 ± 251 on CarRacing). Adding `h_t` should clearly
   help (906 ± 21). If it doesn't, M isn't adding predictive information.
4. **Dream vs real gap.** See the temperature section above.
5. **Coverage.** If M is bad exactly where a good policy goes, the random data
   never visited those states. Switch to the iterative procedure.

## Iterative training and curiosity

For environments a random policy can't explore, run this loop:

1. Initialize M and C randomly.
2. Roll out in the real environment with the current C and store everything.
3. Retrain M (optionally predicting reward and C's own action too) and retrain
   C inside M.
4. Repeat until the task is solved.

To encourage exploration, add M's prediction loss on real transitions as an
intrinsic reward, which flips the sign of M's loss. C is then rewarded for
visiting states that M models poorly, and the new data improves M.

## Adapting to a new environment

- **Observation:** crop the HUD, resize to 64×64, and scale to [0, 1]. Keep V's
  conv stack as it is, since it assumes 64×64.
- **Action:** C outputs `tanh(...)`, which you then map to the env's action
  space. For a continuous box, rescale each dimension (for CarRacing, map gas and
  brake from [-1, 1] to [0, 1]). For discrete actions, threshold the output, for
  example into left / none / right.
- **Reward in dream:** if the task reward isn't "steps survived", give M a
  reward head, or dream training has nothing to optimize.
- **Parameter budget:** CMA-ES scales roughly quadratically in memory with the
  parameter count. Keep C under a few thousand parameters. For a larger C,
  switch to a diagonal or separable ES (e.g. OpenAI-ES or PEPG).

## References in this skill

- `references/hyperparameters.md` covers exact architectures, sizes, and
  parameter counts from the paper for CarRacing and Doom.
- `templates/` is the PyTorch scaffold. Its `README.md` lists the commands in
  pipeline order.
