"""Comparison helpers for candidate textures versus references."""

from __future__ import annotations

import numpy as np


def compare_arrays(candidate: np.ndarray, reference: np.ndarray) -> dict[str, float]:
    """Compare two arrays using simple numeric distances."""

    candidate = candidate.astype(np.float64)
    reference = reference.astype(np.float64)
    diff = candidate - reference
    mse = float(np.mean(diff ** 2))
    mae = float(np.mean(np.abs(diff)))

    candidate_flat = candidate.reshape(-1)
    reference_flat = reference.reshape(-1)
    if np.std(candidate_flat) == 0 or np.std(reference_flat) == 0:
        correlation = 0.0
    else:
        correlation = float(np.corrcoef(candidate_flat, reference_flat)[0, 1])

    return {
        "mse": mse,
        "rmse": float(np.sqrt(mse)),
        "mae": mae,
        "correlation": correlation,
    }

