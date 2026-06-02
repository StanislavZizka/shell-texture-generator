"""Low-frequency spatial modulation helpers for stripe variants."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(slots=True)
class StripeModulationFields:
    """Smooth auxiliary fields used to perturb stripe calibration gently."""

    s_field: np.ndarray
    da_field: np.ndarray
    initial_a_field: np.ndarray
    initial_b_field: np.ndarray


def _smooth_periodic(field: np.ndarray, passes: int) -> np.ndarray:
    """Apply periodic low-pass smoothing using a simple neighbour average."""

    smoothed = np.asarray(field, dtype=np.float64)
    for _ in range(max(0, int(passes))):
        smoothed = (
            smoothed
            + np.roll(smoothed, 1, axis=0)
            + np.roll(smoothed, -1, axis=0)
            + np.roll(smoothed, 1, axis=1)
            + np.roll(smoothed, -1, axis=1)
            + np.roll(np.roll(smoothed, 1, axis=0), 1, axis=1)
            + np.roll(np.roll(smoothed, 1, axis=0), -1, axis=1)
            + np.roll(np.roll(smoothed, -1, axis=0), 1, axis=1)
            + np.roll(np.roll(smoothed, -1, axis=0), -1, axis=1)
        ) / 9.0
    return smoothed


def build_low_frequency_field(
    shape: tuple[int, int],
    seed: int,
    feature_scale: float = 96.0,
    smoothing_passes: int = 8,
) -> np.ndarray:
    """Return a smooth normalized field in the range [-1, 1]."""

    height, width = shape
    rng = np.random.RandomState(int(seed))

    coarse_h = max(4, int(round(height / max(feature_scale, 1.0))))
    coarse_w = max(4, int(round(width / max(feature_scale, 1.0))))
    coarse = rng.normal(0.0, 1.0, (coarse_h, coarse_w)).astype(np.float64)

    repeat_y = max(1, int(np.ceil(height / coarse_h)))
    repeat_x = max(1, int(np.ceil(width / coarse_w)))
    field = np.repeat(np.repeat(coarse, repeat_y, axis=0), repeat_x, axis=1)[:height, :width]
    field = _smooth_periodic(field, smoothing_passes)

    field -= float(field.mean())
    std = float(field.std())
    if std > 1e-12:
        field /= std
    return np.clip(field, -1.0, 1.0)


def build_stripe_modulation_fields(
    shape: tuple[int, int],
    seed: int,
    config: dict | None = None,
) -> StripeModulationFields:
    """Build smooth auxiliary modulation fields from a compact config."""

    cfg = dict(config or {})
    seed_offset = int(cfg.get("seed_offset", 0))
    feature_scale = float(cfg.get("field_scale", 96.0))
    smoothing_passes = int(cfg.get("smoothing_passes", 8))
    orientation = str(cfg.get("orientation", "isotropic")).strip().lower()

    base_seed = int(seed) + seed_offset

    if orientation in {"stripe_x", "x", "x_only", "columns"}:
        height, width = shape

        def _x_only_field(local_seed: int, local_scale: float, local_passes: int) -> np.ndarray:
            rng = np.random.RandomState(local_seed)
            coarse = max(4, int(round(width / max(local_scale, 1.0))))
            anchors = np.linspace(0.0, max(1.0, float(width - 1)), coarse, dtype=np.float64)
            values = rng.normal(0.0, 1.0, coarse)
            x_coords = np.arange(width, dtype=np.float64)
            profile = np.interp(x_coords, anchors, values)
            profile = np.asarray(profile, dtype=np.float64)
            for _ in range(max(0, int(local_passes))):
                padded = np.pad(profile, 1, mode="edge")
                profile = (padded[:-2] + 2.0 * padded[1:-1] + padded[2:]) / 4.0
            profile -= float(profile.mean())
            std = float(profile.std())
            if std > 1e-12:
                profile /= std
            profile = np.clip(profile, -1.0, 1.0)
            return np.repeat(profile[None, :], height, axis=0)

        return StripeModulationFields(
            s_field=_x_only_field(base_seed + 1, feature_scale, smoothing_passes),
            da_field=_x_only_field(base_seed + 2, max(16.0, feature_scale * 0.85), smoothing_passes + 1),
            initial_a_field=_x_only_field(base_seed + 3, feature_scale, smoothing_passes),
            initial_b_field=_x_only_field(base_seed + 4, max(16.0, feature_scale * 1.10), smoothing_passes),
        )

    return StripeModulationFields(
        s_field=build_low_frequency_field(
            shape,
            seed=base_seed + 1,
            feature_scale=feature_scale,
            smoothing_passes=smoothing_passes,
        ),
        da_field=build_low_frequency_field(
            shape,
            seed=base_seed + 2,
            feature_scale=max(16.0, feature_scale * 0.85),
            smoothing_passes=smoothing_passes + 1,
        ),
        initial_a_field=build_low_frequency_field(
            shape,
            seed=base_seed + 3,
            feature_scale=feature_scale,
            smoothing_passes=smoothing_passes,
        ),
        initial_b_field=build_low_frequency_field(
            shape,
            seed=base_seed + 4,
            feature_scale=max(16.0, feature_scale * 1.10),
            smoothing_passes=smoothing_passes,
        ),
    )
