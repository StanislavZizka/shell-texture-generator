"""Color mapping utilities for simulation outputs."""

from __future__ import annotations

import numpy as np

from utils.helpers import hex_to_rgb


def normalize_field(
    field: np.ndarray,
    min_value: float = 0.0,
    max_value: float = 1.0,
) -> np.ndarray:
    """Normalize a field to a target numeric range."""

    field_min = float(np.min(field))
    field_max = float(np.max(field))
    if field_max == field_min:
        return np.full_like(field, min_value, dtype=np.float64)

    return min_value + (field - field_min) * (max_value - min_value) / (field_max - field_min)


def blend_fields_to_rgb(
    A: np.ndarray,
    B: np.ndarray,
    color1: str,
    color2: str,
) -> np.ndarray:
    """Blend two normalized fields into an RGB image array."""

    A_norm = np.clip(normalize_field(A), 0.0, 1.0)
    B_norm = np.clip(normalize_field(B), 0.0, 1.0)
    color1_rgb = np.array(hex_to_rgb(color1), dtype=np.float64)
    color2_rgb = np.array(hex_to_rgb(color2), dtype=np.float64)

    rgb = np.zeros((*A.shape, 3), dtype=np.float64)
    for channel in range(3):
        rgb[:, :, channel] = np.clip(
            color1_rgb[channel] * A_norm + color2_rgb[channel] * B_norm,
            0.0,
            1.0,
        )

    return rgb
