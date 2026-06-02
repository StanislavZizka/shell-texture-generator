"""Spatial metrics used for pattern comparisons."""

from __future__ import annotations

import numpy as np


def dominant_orientation_score(field: np.ndarray) -> float:
    """Return a rough score for directional structure in a field."""

    grad_y, grad_x = np.gradient(field.astype(np.float64))
    energy_x = float(np.mean(np.abs(grad_x)))
    energy_y = float(np.mean(np.abs(grad_y)))
    total = energy_x + energy_y
    if total == 0:
        return 0.0
    return abs(energy_x - energy_y) / total

