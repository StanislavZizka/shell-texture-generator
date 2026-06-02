"""Small numerical helpers used by the texture generator service."""

from __future__ import annotations

import numpy as np


def calculate_laplacian(grid: np.ndarray, dx: float = 1.0) -> np.ndarray:
    """Return the discrete Laplacian of a 2D grid."""

    return (
        np.roll(grid, 1, axis=0)
        + np.roll(grid, -1, axis=0)
        + np.roll(grid, 1, axis=1)
        + np.roll(grid, -1, axis=1)
        - 4 * grid
    ) / (dx * dx)
