"""Basic image metrics used in experiment reports."""

from __future__ import annotations

import numpy as np


def image_mean(field: np.ndarray) -> float:
    return float(np.mean(field))


def image_std(field: np.ndarray) -> float:
    return float(np.std(field))


def image_contrast(field: np.ndarray) -> float:
    p95 = float(np.percentile(field, 95))
    p05 = float(np.percentile(field, 5))
    return p95 - p05


def active_area_ratio(field: np.ndarray, threshold: float = 0.5) -> float:
    return float(np.mean(field >= threshold))

