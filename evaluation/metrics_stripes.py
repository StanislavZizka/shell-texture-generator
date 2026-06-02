"""Specialized metrics for stripe-like patterns."""

from __future__ import annotations

import numpy as np

from rendering.colormaps import normalize_field
from evaluation.metrics_spatial import dominant_orientation_score


def _smooth_profile(profile: np.ndarray, window: int = 11) -> np.ndarray:
    """Smooth a 1D profile with a periodic moving average."""

    window = max(3, int(window) | 1)
    kernel = np.ones(window, dtype=np.float64) / float(window)
    padded = np.pad(profile, (window // 2,), mode="wrap")
    return np.convolve(padded, kernel, mode="valid")


def _peak_indices(signal: np.ndarray, threshold_scale: float = 0.15) -> np.ndarray:
    """Find prominent local maxima in a 1D signal."""

    if signal.size < 3:
        return np.array([], dtype=int)

    derivative = np.diff(signal)
    sign = np.sign(derivative)
    sign[sign == 0] = 1.0
    candidates = np.where((sign[:-1] > 0) & (sign[1:] < 0))[0] + 1
    if candidates.size == 0:
        return candidates

    threshold = float(signal.mean() + threshold_scale * signal.std())
    return np.asarray([idx for idx in candidates if signal[idx] >= threshold], dtype=int)


def stripe_continuity_score(field: np.ndarray) -> float:
    """Estimate how continuous the vertical bands are across rows."""

    normalized = normalize_field(field)
    row_delta = np.abs(np.diff(normalized, axis=0))
    score = 1.0 - float(np.mean(row_delta))
    return float(np.clip(score, 0.0, 1.0))


def stripe_count_estimate(field: np.ndarray) -> int:
    """Estimate the number of visible stripe bands."""

    normalized = normalize_field(field)
    profile = _smooth_profile(normalized.mean(axis=0), window=max(9, normalized.shape[1] // 48 * 2 + 1))
    centered = profile - float(profile.mean())
    peaks = _peak_indices(np.abs(centered), threshold_scale=0.10)
    if peaks.size >= 2:
        return int(peaks.size)

    fft = np.fft.rfft(centered)
    amplitudes = np.abs(fft)
    if amplitudes.size <= 1:
        return 0
    dominant_idx = int(np.argmax(amplitudes[1:]) + 1)
    return int(max(dominant_idx, 0))


def stripe_spacing_variance(field: np.ndarray) -> float:
    """Return normalized variance of stripe spacing between detected bands."""

    normalized = normalize_field(field)
    profile = _smooth_profile(normalized.mean(axis=0), window=max(9, normalized.shape[1] // 48 * 2 + 1))
    centered = profile - float(profile.mean())
    peaks = _peak_indices(np.abs(centered), threshold_scale=0.10)
    if peaks.size < 3:
        return 0.0

    spacings = np.diff(peaks.astype(np.float64))
    mean_spacing = float(np.mean(spacings))
    if mean_spacing <= 1e-12:
        return 0.0
    return float(np.var(spacings) / (mean_spacing ** 2))


def stripe_orientation_score(field: np.ndarray) -> float:
    """Alias for the directional anisotropy score used in reports."""

    return dominant_orientation_score(normalize_field(field))


def stripe_blob_penalty(field: np.ndarray) -> float:
    """Estimate how far a field deviates from a clean stripe backbone.

    The penalty is intentionally simple: compare the field against its
    column-wise stripe backbone and measure the mean absolute residual.
    Stripe-consistent perturbations should keep this small, while speckle-
    like or blob-like deviations will push it higher.
    """

    normalized = normalize_field(field)
    stripe_backbone = np.repeat(normalized.mean(axis=0, keepdims=True), normalized.shape[0], axis=0)
    residual = np.abs(normalized - stripe_backbone)
    penalty = float(np.mean(residual))
    return float(np.clip(penalty * 2.0, 0.0, 1.0))


def temporal_stability_score(snapshots: list[np.ndarray]) -> float:
    """Estimate stability as inverse frame-to-frame change."""

    if len(snapshots) < 2:
        return 1.0

    diffs = []
    for previous, current in zip(snapshots[:-1], snapshots[1:]):
        prev_norm = normalize_field(previous)
        curr_norm = normalize_field(current)
        diffs.append(float(np.mean(np.abs(curr_norm - prev_norm))))

    mean_delta = float(np.mean(diffs))
    return float(np.clip(1.0 - mean_delta, 0.0, 1.0))
