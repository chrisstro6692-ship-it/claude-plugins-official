---
name: scaffold-world-model
description: Scaffold a runnable PyTorch World Models project (VAE + MDN-RNN + CMA-ES controller) into a directory, preconfigured for CarRacing, VizDoom Take Cover, or a user-specified Gymnasium environment.
argument-hint: "[carracing|doom|<gymnasium-env-id>] [target-dir]"
allowed-tools: [Read, Write, Edit, Glob, Bash]
---

# Scaffold a World Models project

The user invoked this with: $ARGUMENTS

## Steps

1. **Parse arguments.** The first argument is the environment: `carracing`
   (default), `doom`, or any Gymnasium env id. The second is the target
   directory (default `./world_models`). If the target already contains files,
   list them and ask before overwriting anything.

2. **Copy the templates.** They live in this plugin at
   `${CLAUDE_PLUGIN_ROOT}/skills/world-models/templates/`. If that variable
   isn't expanded, find the directory by globbing for
   `**/skills/world-models/templates/models.py`. Copy every file in it into
   the target directory unchanged.

3. **For a custom Gymnasium env,** inspect it before editing anything. Run
   `python -c "import gymnasium as gym; e = gym.make('<id>'); print(e.observation_space, e.action_space, e.spec.max_episode_steps)"`
   if gymnasium is installed. Otherwise ask the user for the observation shape,
   action space, and episode length. Then:
   - Add a preset to `PRESETS` in `config.py` with `env_id`, `action_dim`
     (1 for Discrete, `shape[0]` for Box), `max_steps`, and a `crop` that
     removes any HUD or score bar. `--preset` choices come from `PRESETS`, so
     no other change is needed.
   - If the observation isn't an RGB image (for example a state vector), stop
     and tell the user. V assumes 64×64 RGB frames, so pixels are needed. Offer
     to render frames with `render_mode="rgb_array"` instead.
   - Decide whether C should train in the real env (the default) or in the
     dream. Dream training requires `predict_done=True` and, unless the reward
     is survival time, a reward head on M. Tell the user if that's needed and
     don't add it silently.

4. **Smoke-test if the dependencies are available.** Do a two-episode collect
   with `--episodes 2 --run-dir runs/smoke`, then one `train_vae.py` epoch,
   `encode.py`, `train_mdnrnn.py --steps 20 --seq-len 50 --batch-size 4`, and
   `train_controller.py --generations 1 --popsize 4 --rollouts 1 --workers 2`.
   For a real-mode smoke run, also pass `--set max_steps=50`. Report anything
   that fails with its error. Delete `runs/smoke` afterwards.

5. **Report back.** Give the target directory, the preset used, the controller's
   parameter count (`Controller.n_params(cfg.controller_in_dim, cfg.action_dim)`),
   and the pipeline commands from the scaffold's `README.md` with the chosen
   preset filled in. Mention that the full run collects about 10,000 episodes,
   and that V and M train best on a GPU.

For architecture questions, tuning temperature, or debugging a trained agent,
use the `world-models` skill.
