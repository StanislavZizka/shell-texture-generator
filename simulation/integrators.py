"""Numerical integrators used by the simulation core."""

from __future__ import annotations

import numpy as np


def explicit_euler_step(field: np.ndarray, derivative: np.ndarray, delta_t: float) -> np.ndarray:
    """Advance a field by one explicit Euler step."""

    return field + delta_t * derivative

