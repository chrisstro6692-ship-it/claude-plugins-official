"""Environment construction, frame preprocessing, and action mapping.

The controller and the MDN-RNN both work in "controller space": a vector in
[-1, 1]^action_dim. `to_env_action` maps it into whatever the env expects, so
this is the only file to touch when porting to a new environment.
"""

import gymnasium as gym
import numpy as np
from PIL import Image


def make_env(cfg, render_mode=None):
    if cfg.env_id.startswith("Vizdoom"):
        from vizdoom import gymnasium_wrapper  # noqa: F401  (registers the envs)
    return gym.make(cfg.env_id, render_mode=render_mode)


def preprocess(obs, cfg):
    """Raw observation -> uint8 array of shape (64, 64, 3)."""
    frame = obs["screen"] if isinstance(obs, dict) else obs
    top, bottom = cfg.crop
    frame = frame[top:bottom]
    img = Image.fromarray(frame).resize((64, 64), Image.BILINEAR)
    return np.asarray(img, dtype=np.uint8)


def to_env_action(a, cfg, action_space):
    a = np.asarray(a, dtype=np.float32)
    if cfg.env_id.startswith("CarRacing"):
        steer, gas, brake = a
        return np.array([steer, (gas + 1) / 2, np.clip(brake, 0, 1)], dtype=np.float32)
    if isinstance(action_space, gym.spaces.Discrete):
        # Split [-1, 1] into n equal bins, e.g. left / stay / right.
        n = action_space.n
        return int(np.clip((a[0] + 1) / 2 * n, 0, n - 1))
    low, high = action_space.low, action_space.high
    return (low + (a + 1) / 2 * (high - low)).astype(action_space.dtype)


class RandomPolicy:
    """Random actions held for a random number of steps.

    Holding actions explores far better than i.i.d. noise, which mostly jitters
    in place. For CarRacing, brake is biased towards "off" so the car moves.
    """

    def __init__(self, cfg, rng):
        self.cfg, self.rng = cfg, rng
        self.action, self.hold = None, 0

    def __call__(self):
        if self.hold <= 0:
            self.action = self.rng.uniform(-1, 1, self.cfg.action_dim).astype(np.float32)
            if self.cfg.env_id.startswith("CarRacing"):
                self.action[2] = self.rng.uniform(-1, 0.3)
            self.hold = int(self.rng.integers(1, 11))
        self.hold -= 1
        return self.action
