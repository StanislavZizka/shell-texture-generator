"""Preset loaders backed by versioned JSON files."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from .paths import PRESETS_DIR


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing preset file: {path}")

    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if not isinstance(payload, dict):
        raise ValueError(f"Preset file must contain a JSON object: {path}")

    return payload


@lru_cache(maxsize=None)
def load_preset_bundle(filename: str) -> dict[str, Any]:
    """Load a preset bundle from configs/presets."""

    return _load_json(PRESETS_DIR / filename)


def load_activator_inhibitor_presets() -> dict[str, Any]:
    return load_preset_bundle("activator_inhibitor.json")


def load_figure_23_presets() -> dict[str, Any]:
    return load_preset_bundle("figure_23.json")


def load_figure_211_presets() -> dict[str, Any]:
    return load_preset_bundle("figure_211.json")


def load_figure_212_presets() -> dict[str, Any]:
    return load_preset_bundle("figure_212.json")
