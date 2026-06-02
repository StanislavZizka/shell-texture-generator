"""Discrete Laplacian operators used by the simulation core."""

from __future__ import annotations

import numpy as np


def periodic_laplacian(grid: np.ndarray, dx: float = 1.0) -> np.ndarray:
    """Compute a 2D periodic Laplacian with finite differences."""

    return (
        np.roll(grid, 1, axis=0)
        + np.roll(grid, -1, axis=0)
        + np.roll(grid, 1, axis=1)
        + np.roll(grid, -1, axis=1)
        - 4.0 * grid
    ) / (dx * dx)

