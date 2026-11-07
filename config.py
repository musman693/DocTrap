from __future__ import annotations

import os
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.yaml"


def load_config(path: str | Path | None = None) -> dict:
    target = Path(path) if path else CONFIG_PATH
    if not target.exists():
        return {}
    with target.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def get_config() -> dict:
    return load_config()


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_data_root() -> Path:
    return ensure_dir(BASE_DIR / "data")
