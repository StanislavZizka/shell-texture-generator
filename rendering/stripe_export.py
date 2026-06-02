"""Stripe-focused export helpers for Figure 2.3."""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
from PIL import Image

from rendering.colormaps import normalize_field
from utils.helpers import hex_to_rgb


def _dominant_vertical_phase(field: np.ndarray) -> tuple[float, float]:
    """Estimate the dominant horizontal stripe frequency and phase."""

    profile = np.asarray(field, dtype=np.float64).mean(axis=0)
    profile = profile - float(profile.mean())
    fft = np.fft.rfft(profile)
    amplitudes = np.abs(fft)
    if amplitudes.size <= 1:
        return 1.0 / max(profile.shape[0], 1), 0.0

    dominant_idx = int(np.argmax(amplitudes[1:]) + 1)
    if amplitudes[dominant_idx] <= 1e-12:
        dominant_idx = max(1, profile.shape[0] // 12)
        dominant_idx = min(dominant_idx, amplitudes.size - 1)

    frequency = dominant_idx / max(profile.shape[0], 1)
    phase = float(np.angle(fft[dominant_idx])) if dominant_idx < fft.size else 0.0
    return frequency, phase


def _resample_square(field: np.ndarray, size: int) -> np.ndarray:
    """Resample a 2D field to a square low-frequency canvas."""

    normalized = np.clip(normalize_field(field), 0.0, 1.0)
    image = Image.fromarray((normalized * 255).astype(np.uint8), mode="L")
    resampling = getattr(Image, "Resampling", Image)
    resized = image.resize((size, size), resample=resampling.BILINEAR)
    return np.asarray(resized, dtype=np.float64) / 255.0


def _smooth_1d_profile(profile: np.ndarray, passes: int) -> np.ndarray:
    """Smooth a 1D profile with a compact symmetric kernel."""

    kernel = np.array([1.0, 2.0, 1.0], dtype=np.float64)
    kernel /= float(kernel.sum())
    smoothed = np.asarray(profile, dtype=np.float64)
    for _ in range(max(1, int(passes))):
        padded = np.pad(smoothed, 1, mode="edge")
        smoothed = (
            kernel[0] * padded[:-2] +
            kernel[1] * padded[1:-1] +
            kernel[2] * padded[2:]
        )
    return smoothed


def _low_frequency_column_profile(
    rng: np.random.RandomState,
    size: int,
    *,
    control_points: int,
    smoothing_passes: int,
) -> np.ndarray:
    """Build a smooth 1D profile that varies only along the stripe axis."""

    knot_count = max(4, int(control_points))
    anchors = np.linspace(0.0, max(1.0, float(size - 1)), knot_count, dtype=np.float64)
    samples = rng.rand(knot_count)
    x_coords = np.arange(size, dtype=np.float64)
    profile = np.interp(x_coords, anchors, samples)
    profile = _smooth_1d_profile(profile, smoothing_passes)
    profile = profile - float(profile.min())
    peak_to_peak = float(np.ptp(profile))
    if peak_to_peak > 1e-12:
        profile /= peak_to_peak
    return np.clip(profile, 0.0, 1.0)


def _broadcast_column_profile(profile: np.ndarray, size: int) -> np.ndarray:
    """Expand a 1D profile to a square field without introducing y variation."""

    return np.repeat(np.asarray(profile, dtype=np.float64)[None, :], size, axis=0)


def _low_frequency_axis_profile(
    rng: np.random.RandomState,
    size: int,
    *,
    control_points: int,
    smoothing_passes: int,
) -> np.ndarray:
    """Build a smooth 1D profile in [-1, 1] along a single axis."""

    knot_count = max(4, int(control_points))
    anchors = np.linspace(0.0, max(1.0, float(size - 1)), knot_count, dtype=np.float64)
    samples = rng.normal(0.0, 1.0, knot_count)
    x_coords = np.arange(size, dtype=np.float64)
    profile = np.interp(x_coords, anchors, samples)
    profile = _smooth_1d_profile(profile, smoothing_passes)
    profile -= float(profile.mean())
    std = float(profile.std())
    if std > 1e-12:
        profile /= std
    return np.clip(profile, -1.0, 1.0)


def _build_stripe_segment_random_error_maps(
    size: int,
    random_error_params: dict,
    *,
    local_y_segments: bool,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Create stripe-aligned disturbance masks with short vertical interruptions."""

    strength = float(random_error_params.get("strength", 0.02))
    probability = float(random_error_params.get("probability", 0.02))
    num_regions = max(1, int(random_error_params.get("num_regions", 1)))
    region_size = max(4, int(random_error_params.get("region_size", 8)))
    jitter = float(random_error_params.get("jitter", 0.10))
    micro_noise = float(random_error_params.get("micro_noise", 0.04))
    alpha_var = float(random_error_params.get("alpha_var", 0.20))
    beta = float(random_error_params.get("beta", 0.08))
    drift_x = float(random_error_params.get("drift_x", 0.8))
    drift_y = float(random_error_params.get("drift_y", 0.7))
    drift_frequency = float(random_error_params.get("drift_frequency", 0.002))

    seed = _stripe_random_error_seed(random_error_params, size)
    rng = np.random.RandomState(seed)

    x = np.linspace(0.0, 1.0, size, dtype=np.float64)
    y = np.linspace(0.0, 1.0, size, dtype=np.float64)[:, None]
    gap_mask = np.zeros((size, size), dtype=np.float64)
    phase_shift = np.zeros((size, size), dtype=np.float64)
    attenuation = np.ones((size, size), dtype=np.float64)

    center_slots = np.linspace(0.12, 0.88, num_regions, dtype=np.float64)
    center_jitter = (rng.rand(num_regions) - 0.5) * (
        0.08 + 0.05 * float(probability) + 0.04 * float(jitter)
    )
    centers = np.clip(center_slots + center_jitter, 0.06, 0.94)

    base_width_px = max(
        3.0,
        float(region_size) * (0.34 + 0.08 * float(jitter) + 0.04 * float(alpha_var)),
    )
    base_height_px = max(
        5.0,
        float(region_size) * (0.82 + 0.22 * float(jitter) + 0.12 * float(alpha_var)),
    )
    base_width = base_width_px / max(float(size), 1.0)
    base_height = base_height_px / max(float(size), 1.0)
    wobble_scale = np.pi * (0.010 + 0.040 * float(strength))
    attenuation_scale = np.clip(
        0.16 + 0.22 * float(strength) + 0.08 * float(probability),
        0.10,
        0.42,
    )

    x_micro = _low_frequency_axis_profile(
        np.random.RandomState(int(rng.randint(0, 2**31 - 1))),
        size,
        control_points=max(4, int(round(size / max(22.0 + 8.0 * float(strength), 1.0)))),
        smoothing_passes=max(2, int(round(1 + 2 * float(micro_noise) + 2 * float(alpha_var)))),
    )
    x_micro = np.clip(0.5 + 0.5 * x_micro, 0.0, 1.0)
    x_micro = np.power(x_micro, 1.0 + 0.12 * float(micro_noise))

    y_micro = _low_frequency_axis_profile(
        np.random.RandomState(int(rng.randint(0, 2**31 - 1))),
        size,
        control_points=max(4, int(round(size / max(26.0 + 10.0 * float(strength), 1.0)))),
        smoothing_passes=max(2, int(round(1 + float(micro_noise) + float(alpha_var)))),
    )
    y_micro = np.clip(0.5 + 0.5 * y_micro, 0.0, 1.0)

    segments_per_region = 1 if not local_y_segments else 2
    if local_y_segments and rng.rand() < 0.45:
        segments_per_region += 1

    for idx, center_x in enumerate(centers):
        width = np.clip(
            base_width * (0.86 + 0.22 * rng.rand()),
            0.008,
            0.060,
        )
        x_window = np.exp(-0.5 * ((x - center_x) / max(width, 1e-6)) ** 2)
        x_window *= 0.60 + 0.40 * np.roll(x_micro, int(rng.randint(0, max(1, size))))

        for seg_idx in range(max(1, segments_per_region)):
            center_y = np.clip(
                0.16 + 0.68 * rng.rand() + 0.08 * np.sin((idx + seg_idx + 1) * 1.5 + float(drift_y)),
                0.06,
                0.94,
            )
            height = np.clip(
                base_height * (0.72 + 0.28 * rng.rand()),
                0.018,
                0.16 if local_y_segments else 0.22,
            )
            if local_y_segments:
                height *= 0.82 + 0.12 * rng.rand()
            y_window = np.exp(-0.5 * ((y - center_y) / max(height, 1e-6)) ** 2)
            y_window = np.power(y_window, 1.0 + 0.25 * float(jitter))
            y_window *= 0.82 + 0.18 * np.roll(y_micro, int(rng.randint(0, max(1, size))))[:, None]

            patch = np.outer(y_window[:, 0], x_window)
            patch = np.clip(patch, 0.0, 1.0)

            local_strength = np.clip(
                float(strength) * (0.88 + 0.18 * float(probability) + 0.10 * rng.rand()),
                0.0,
                0.16,
            )
            gap_mask = np.maximum(gap_mask, patch * local_strength)

            local_attenuation = 1.0 - attenuation_scale * patch
            attenuation = np.minimum(attenuation, np.clip(local_attenuation, 0.38, 1.0))

            phase_shift = np.maximum(
                phase_shift,
                np.clip(patch * wobble_scale, 0.0, 0.07),
            )

    gap_mask = np.clip(gap_mask, 0.0, 1.0)
    phase_shift = np.clip(phase_shift, 0.0, 1.0)
    attenuation = np.clip(attenuation, 0.30, 1.0)
    return gap_mask, phase_shift, attenuation


def _build_vertical_segmented_random_error_maps(
    size: int,
    random_error_params: dict,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Create stripe-consistent error masks localized in vertical segments."""

    return _build_stripe_segment_random_error_maps(
        size,
        random_error_params,
        local_y_segments=True,
    )

    strength = float(random_error_params.get("strength", 0.02))
    probability = float(random_error_params.get("probability", 0.02))
    num_regions = max(1, int(random_error_params.get("num_regions", 1)))
    region_size = max(4, int(random_error_params.get("region_size", 8)))
    jitter = float(random_error_params.get("jitter", 0.10))
    micro_noise = float(random_error_params.get("micro_noise", 0.04))
    alpha_var = float(random_error_params.get("alpha_var", 0.20))
    beta = float(random_error_params.get("beta", 0.08))
    drift_x = float(random_error_params.get("drift_x", 0.8))
    drift_y = float(random_error_params.get("drift_y", 0.7))
    drift_frequency = float(random_error_params.get("drift_frequency", 0.002))

    seed = _stripe_random_error_seed(random_error_params, size)
    rng = np.random.RandomState(seed)

    x = np.linspace(0.0, 1.0, size, dtype=np.float64)
    y = np.linspace(0.0, 1.0, size, dtype=np.float64)
    gap_mask = np.zeros((size, size), dtype=np.float64)
    phase_shift = np.zeros((size, size), dtype=np.float64)
    attenuation = np.ones((size, size), dtype=np.float64)

    center_slots = np.linspace(0.16, 0.84, num_regions, dtype=np.float64)
    center_jitter = (rng.rand(num_regions) - 0.5) * (
        0.10 + 0.06 * float(probability) + 0.04 * float(jitter)
    )
    centers = np.clip(center_slots + center_jitter, 0.08, 0.92)

    base_width_px = max(
        4.0,
        float(region_size) * (0.58 + 0.10 * float(jitter) + 0.05 * float(alpha_var)),
    )
    base_width = base_width_px / max(float(size), 1.0)
    base_height_px = max(
        6.0,
        float(region_size) * (1.6 + 0.5 * float(jitter) + 0.25 * float(alpha_var)),
    )
    base_height = base_height_px / max(float(size), 1.0)
    wobble_scale = np.pi * (0.012 + 0.05 * float(strength))
    attenuation_scale = np.clip(
        0.18 + 0.26 * float(strength) + 0.10 * float(probability),
        0.12,
        0.48,
    )

    for idx, center_x in enumerate(centers):
        width = np.clip(
            base_width * (0.84 + 0.26 * rng.rand()),
            0.012,
            0.090,
        )
        center_y = np.clip(
            0.18 + 0.64 * rng.rand() + 0.10 * np.sin((idx + 1) * 1.7 + float(drift_y)),
            0.10,
            0.90,
        )
        height = np.clip(
            base_height * (0.90 + 0.30 * rng.rand()),
            0.040,
            0.34,
        )

        x_offset = (x - center_x) / max(width, 1e-6)
        y_offset = (y - center_y) / max(height, 1e-6)
        x_window = np.exp(-0.5 * x_offset**2)
        y_window = np.exp(-0.5 * y_offset**2)
        y_window = np.power(y_window, 1.0 + 0.35 * float(jitter))

        x_profile = _low_frequency_axis_profile(
            np.random.RandomState(int(rng.randint(0, 2**31 - 1))),
            size,
            control_points=max(4, int(round(size / max(18.0 + 10.0 * float(strength), 1.0)))),
            smoothing_passes=max(2, int(round(1 + 2 * float(micro_noise) + 2 * float(alpha_var)))),
        )
        x_profile = np.clip(0.5 + 0.5 * x_profile, 0.0, 1.0)
        x_profile = np.power(x_profile, 1.0 + 0.18 * float(micro_noise))

        wobble = 0.5 + 0.5 * np.sin(
            2.0 * np.pi * (x * (0.45 + 0.20 * float(drift_x)) + idx * 0.13 + drift_frequency * float(size))
        )
        wobble = np.clip(wobble, 0.0, 1.0)

        patch = np.outer(y_window, x_window * (0.78 + 0.22 * x_profile) * (0.90 + 0.10 * wobble))
        patch = np.clip(patch, 0.0, 1.0)

        local_strength = np.clip(
            float(strength) * (0.82 + 0.22 * float(probability) + 0.14 * rng.rand()),
            0.0,
            0.14,
        )
        gap_mask = np.maximum(gap_mask, patch * local_strength)

        local_attenuation = 1.0 - attenuation_scale * patch
        attenuation = np.minimum(attenuation, np.clip(local_attenuation, 0.40, 1.0))

        phase_shift = np.maximum(
            phase_shift,
            np.clip(patch * wobble_scale, 0.0, 0.08),
        )

    gap_mask = np.clip(gap_mask, 0.0, 1.0)
    phase_shift = np.clip(phase_shift, 0.0, 1.0)
    attenuation = np.clip(attenuation, 0.32, 1.0)
    return gap_mask, phase_shift, attenuation


def _build_stripe_random_error_maps(
    size: int,
    random_error_params: dict,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Create stripe-consistent error masks aligned to the x-axis only."""

    return _build_stripe_segment_random_error_maps(
        size,
        random_error_params,
        local_y_segments=bool(random_error_params.get("local_y_segments", False)),
    )

    strength = float(random_error_params.get("strength", 0.02))
    probability = float(random_error_params.get("probability", 0.02))
    num_regions = max(1, int(random_error_params.get("num_regions", 1)))
    region_size = max(4, int(random_error_params.get("region_size", 8)))
    jitter = float(random_error_params.get("jitter", 0.10))
    micro_noise = float(random_error_params.get("micro_noise", 0.04))
    alpha_var = float(random_error_params.get("alpha_var", 0.20))
    beta = float(random_error_params.get("beta", 0.08))
    drift_x = float(random_error_params.get("drift_x", 0.8))
    drift_y = float(random_error_params.get("drift_y", 0.7))
    drift_frequency = float(random_error_params.get("drift_frequency", 0.002))

    seed = _stripe_random_error_seed(random_error_params, size)
    rng = np.random.RandomState(seed)

    x = np.linspace(0.0, 1.0, size, dtype=np.float64)
    gap_mask_1d = np.zeros(size, dtype=np.float64)
    phase_shift_1d = np.zeros(size, dtype=np.float64)
    attenuation_1d = np.ones(size, dtype=np.float64)

    center_slots = np.linspace(0.14, 0.86, num_regions, dtype=np.float64)
    center_jitter = (rng.rand(num_regions) - 0.5) * (
        0.12 + 0.08 * float(probability) + 0.04 * float(jitter)
    )
    centers = np.clip(center_slots + center_jitter, 0.06, 0.94)

    base_width_px = max(
        3.5,
        float(region_size) * (0.62 + 0.18 * float(jitter) + 0.08 * float(alpha_var)),
    )
    base_width = base_width_px / max(float(size), 1.0)
    phase_scale = np.pi * (0.035 + 0.18 * float(strength) + 0.05 * float(beta))
    attenuation_scale = np.clip(
        0.22 + 0.34 * float(strength) + 0.10 * float(probability),
        0.18,
        0.56,
    )

    for idx, center in enumerate(centers):
        width = np.clip(
            base_width * (0.82 + 0.30 * rng.rand()),
            0.010,
            0.120,
        )
        offset = (x - center) / max(width, 1e-6)
        core = np.exp(-0.5 * offset**2)
        shoulder = np.exp(-0.5 * (offset / (1.75 + 0.20 * float(beta))) ** 2)
        window = np.clip(0.78 * core + 0.22 * shoulder, 0.0, 1.0)
        window = np.power(window, 1.0 + 0.55 * float(jitter))

        local_scale = np.clip(
            float(strength) * (0.82 + 0.22 * float(probability) + 0.10 * rng.rand()),
            0.0,
            0.12,
        )
        local_strength = np.clip(window * (0.72 + local_scale), 0.0, 1.0)
        gap_mask_1d = np.maximum(gap_mask_1d, local_strength)

        sign = -1.0 if idx % 2 == 0 else 1.0
        sign *= 0.60 + 0.35 * rng.rand()
        local_phase = sign * phase_scale * (0.80 * core - 0.24 * shoulder)
        local_phase += np.sin(
            2.0 * np.pi * (x * drift_x + drift_frequency * float(size) + idx * 0.17)
        ) * (0.015 + 0.055 * float(strength))
        phase_shift_1d += local_phase * window

        local_attenuation = 1.0 - attenuation_scale * (0.58 * core + 0.42 * shoulder)
        local_attenuation -= 0.05 * float(micro_noise) * window
        attenuation_1d = np.minimum(attenuation_1d, np.clip(local_attenuation, 0.34, 1.0))

    gap_mask_1d = _smooth_1d_profile(gap_mask_1d, max(1, int(round(1 + 2 * float(jitter)))))
    gap_mask_1d = np.clip(gap_mask_1d, 0.0, 1.0)

    phase_shift_1d = _smooth_1d_profile(phase_shift_1d, max(1, int(round(1 + 2 * float(micro_noise)))))
    phase_shift_1d -= float(phase_shift_1d.mean())
    phase_scale_max = max(float(np.max(np.abs(phase_shift_1d))), 1e-8)
    phase_shift_1d = np.clip(phase_shift_1d / phase_scale_max, -1.0, 1.0)
    phase_shift_1d *= np.pi * (0.045 + 0.14 * float(strength))

    attenuation_1d = _smooth_1d_profile(
        attenuation_1d,
        max(1, int(round(1 + 2 * float(alpha_var)))),
    )
    attenuation_1d = np.clip(attenuation_1d, 0.32, 1.0)

    gap_mask = _broadcast_column_profile(gap_mask_1d, size)
    phase_shift = _broadcast_column_profile(phase_shift_1d, size)
    attenuation = _broadcast_column_profile(attenuation_1d, size)
    return gap_mask, phase_shift, attenuation


def _stripe_random_error_seed(params: dict, size: int) -> int:
    """Derive a deterministic seed for stripe interruptions."""

    keys = (
        "enabled",
        "strength",
        "duration",
        "frequency",
        "probability",
        "num_regions",
        "region_size",
        "jitter",
        "micro_noise",
        "alpha_var",
        "beta",
        "drift_x",
        "drift_y",
        "drift_frequency",
    )
    material = "|".join(f"{key}={params.get(key)}" for key in keys)
    material += f"|size={size}"
    return int(hashlib.sha1(material.encode("utf-8")).hexdigest()[:8], 16)


def _apply_stripe_random_error(
    combined: np.ndarray,
    stripe_wave: np.ndarray,
    frequency: float,
    phase: float,
    random_error_params: dict | None,
) -> np.ndarray:
    """Apply stripe-specific interruptions without converting the pattern into spots."""

    if not random_error_params or not bool(random_error_params.get("enabled", False)):
        return combined

    gap_mask, phase_shift, attenuation = _build_stripe_random_error_maps(
        int(combined.shape[0]),
        random_error_params,
    )
    softened = np.clip(combined * attenuation, 0.0, 1.0)
    softened = np.clip(softened * (1.0 - 0.18 * gap_mask), 0.0, 1.0)
    softened = np.clip(
        softened + 0.035 * phase_shift * (stripe_wave - 0.5),
        0.0,
        1.0,
    )
    return softened


def save_stripe_texture_image(
    heatmap: np.ndarray,
    color1: str,
    color2: str,
    output_path: str | Path,
    *,
    texture_mix: float = 0.58,
    phase_strength: float = 0.24,
    amplitude_floor: float = 0.68,
    amplitude_span: float = 0.22,
    gamma: float = 0.94,
    random_error_params: dict | None = None,
) -> str:
    """Save a stripe-enhanced texture image derived from a 2D heatmap."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    field = np.asarray(heatmap, dtype=np.float64)
    if field.ndim != 2:
        raise ValueError("heatmap must be a 2D array")

    normalized = np.clip(normalize_field(field), 0.0, 1.0)
    size = int(max(normalized.shape))
    square = _resample_square(normalized, size)
    frequency, phase = _dominant_vertical_phase(square)

    x = np.linspace(0.0, 1.0, size, dtype=np.float64)[None, :]
    random_error_enabled = bool(random_error_params and random_error_params.get("enabled", False))
    if not random_error_enabled:
        low_freq = _resample_square(square, max(12, size // 16))
        low_freq = _resample_square(low_freq, size)
        phase_mod = float(phase_strength) * (low_freq - float(low_freq.mean()))
        amplitude_mod = np.clip(
            float(amplitude_floor) + float(amplitude_span) * (low_freq - 0.5),
            0.42,
            0.98,
        )
        stripe_wave = 0.5 + 0.5 * np.sin(
            2.0 * np.pi * (frequency * size) * x + phase + phase_mod
        )
        stripe_component = np.clip(0.5 + amplitude_mod * (stripe_wave - 0.5), 0.0, 1.0)
        irregular = np.clip(0.54 * square + 0.46 * low_freq, 0.0, 1.0)
        combined = np.clip(
            float(texture_mix) * irregular + (1.0 - float(texture_mix)) * stripe_component,
            0.0,
            1.0,
        )
    else:
        column_profile_1d = np.asarray(square, dtype=np.float64).mean(axis=0)
        column_profile_1d = _smooth_1d_profile(column_profile_1d, max(4, size // 32))
        profile_min = float(column_profile_1d.min())
        profile_span = float(np.ptp(column_profile_1d))
        if profile_span > 1e-12:
            column_profile_1d = (column_profile_1d - profile_min) / profile_span
        else:
            column_profile_1d = np.zeros_like(column_profile_1d)
        column_profile = _broadcast_column_profile(column_profile_1d, size)
        phase_mod = float(phase_strength) * (column_profile - float(column_profile.mean()))
        envelope_mix = np.clip(0.06 + 0.18 * float(texture_mix), 0.08, 0.22)
        gap_mask = None
        gap_mask, phase_shift, attenuation = _build_stripe_random_error_maps(size, random_error_params)
        phase_mod = np.clip(0.58 * phase_mod + phase_shift, -np.pi, np.pi)
        amplitude_mod = np.clip(
            (float(amplitude_floor) + float(amplitude_span) * (column_profile - 0.5))
            * (0.90 + 0.10 * attenuation),
            0.30,
            0.98,
        )
        envelope_mix = np.clip(envelope_mix * 0.82, 0.05, 0.18)
        stripe_wave = 0.5 + 0.5 * np.sin(
            2.0 * np.pi * (frequency * size) * x + phase + phase_mod
        )
        stripe_component = np.clip(0.5 + amplitude_mod * (stripe_wave - 0.5), 0.0, 1.0)
        stripe_component = np.clip(
            stripe_component * (1.0 - 0.18 * gap_mask),
            0.0,
            1.0,
        )
        stripe_envelope = np.clip(1.0 - envelope_mix * (1.0 - column_profile), 0.72, 1.0)
        stripe_envelope = np.clip(
            stripe_envelope * (1.0 - 0.04 * gap_mask),
            0.66,
            1.0,
        )
        if bool(random_error_params.get("local_y_segments", False)):
            local_mask = np.clip(0.72 * gap_mask + 0.28 * (1.0 - attenuation), 0.0, 0.22)
            combined = np.clip((stripe_component * stripe_envelope) * (1.0 - local_mask), 0.0, 1.0)
        else:
            combined = np.clip(stripe_component * stripe_envelope, 0.0, 1.0)
    combined = np.power(combined, float(gamma))

    bg_rgb = np.array(hex_to_rgb(color1), dtype=np.float64)
    fg_rgb = np.array(hex_to_rgb(color2), dtype=np.float64)
    rgb = (
        bg_rgb[None, None, :] * (1.0 - combined[..., None]) +
        fg_rgb[None, None, :] * combined[..., None]
    )
    rgb = np.clip(rgb, 0.0, 1.0)

    Image.fromarray((rgb * 255).astype(np.uint8)).save(path)
    return str(path)


def save_stripe_raw_image(
    field: np.ndarray,
    output_path: str | Path,
) -> str:
    """Save the final activator field as a grayscale raw-value image."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    array = np.asarray(field, dtype=np.float64)
    if array.ndim != 2:
        raise ValueError("field must be a 2D array")

    normalized = np.clip(normalize_field(array), 0.0, 1.0)
    Image.fromarray((normalized * 255).astype(np.uint8), mode="L").save(path)
    return str(path)


def save_stripe_space_time_image(
    snapshots: list[tuple[int, np.ndarray, np.ndarray]],
    output_path: str | Path,
) -> str:
    """Save a grayscale space-time diagram from activator snapshots."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if not snapshots:
        raise ValueError("snapshots must not be empty")

    profiles: list[np.ndarray] = []
    for _step, activator, _inhibitor in snapshots:
        field = np.asarray(activator, dtype=np.float64)
        if field.ndim != 2:
            raise ValueError("snapshot activator field must be 2D")
        center = field.shape[0] // 2
        half_band = max(0, field.shape[0] // 128)
        row0 = max(0, center - half_band)
        row1 = min(field.shape[0], center + half_band + 1)
        profile = field[row0:row1, :].mean(axis=0)
        profiles.append(profile)

    matrix = np.stack(profiles, axis=0)
    normalized = np.clip(normalize_field(matrix), 0.0, 1.0)
    square_size = int(max(normalized.shape))
    if normalized.shape[0] != square_size or normalized.shape[1] != square_size:
        normalized = _resample_square(normalized, square_size)
    normalized = np.power(normalized, 0.92)
    Image.fromarray((normalized * 255).astype(np.uint8), mode="L").save(path)
    return str(path)
