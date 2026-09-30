"""Experiment configuration and shared CLI helpers."""

import argparse
import dataclasses
import json
import os
from dataclasses import dataclass


@dataclass
class Config:
    env_id: str
    z_dim: int
    rnn_hidden: int
    action_dim: int
    max_steps: int
    # Rows to keep from the raw frame before resizing to 64x64, as (top, bottom).
    crop: tuple = (0, None)
    n_mixtures: int = 5
    predict_done: bool = False
    # Controller input: "z" (V only), "zh" (V + M hidden), "zhc" (+ LSTM cell).
    controller_inputs: str = "zh"
    kl_tolerance: float = 0.5
    # Dream-only settings.
    tau: float = 1.0

    @property
    def controller_in_dim(self):
        return {
            "z": self.z_dim,
            "zh": self.z_dim + self.rnn_hidden,
            "zhc": self.z_dim + 2 * self.rnn_hidden,
        }[self.controller_inputs]


PRESETS = {
    "carracing": Config(
        env_id="CarRacing-v3",
        z_dim=32,
        rnn_hidden=256,
        action_dim=3,
        max_steps=1000,
        crop=(0, 84),  # drop the bottom HUD
    ),
    "doom": Config(
        env_id="VizdoomTakeCover-v0",
        z_dim=64,
        rnn_hidden=512,
        action_dim=1,
        max_steps=2100,
        predict_done=True,
        controller_inputs="zhc",
        tau=1.15,
    ),
}


def add_common_args(parser: argparse.ArgumentParser):
    parser.add_argument("--preset", default="carracing", choices=sorted(PRESETS))
    parser.add_argument("--run-dir", default=None, help="defaults to runs/<preset>")
    parser.add_argument(
        "--set",
        nargs="*",
        default=[],
        metavar="KEY=VALUE",
        help="override config fields, e.g. --set controller_inputs=z tau=1.3",
    )
    return parser


def load_config(args):
    cfg = PRESETS[args.preset]
    overrides = {}
    for item in args.set:
        key, value = item.split("=", 1)
        field_type = type(getattr(cfg, key))
        overrides[key] = json.loads(value) if field_type in (bool, tuple) else field_type(value)
    cfg = dataclasses.replace(cfg, **overrides)
    run_dir = args.run_dir or os.path.join("runs", args.preset)
    os.makedirs(run_dir, exist_ok=True)
    return cfg, run_dir


class Paths:
    def __init__(self, run_dir):
        self.episodes = os.path.join(run_dir, "episodes")
        self.series = os.path.join(run_dir, "series")
        self.vae = os.path.join(run_dir, "vae.pt")
        self.rnn = os.path.join(run_dir, "mdnrnn.pt")
        self.controller = os.path.join(run_dir, "controller.npy")
        self.log = os.path.join(run_dir, "controller_log.jsonl")
