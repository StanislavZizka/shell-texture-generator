"""Figure 2.11 helper functions extracted from the API routes module."""

from __future__ import annotations

import hashlib
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image

from config import IMAGES_DIR
from config_211 import FIG211_REFERENCE_DIR, MODEL_211_PARAMS, SPOTS_211_PRESETS, SPOTS_211_RANDOM_ERROR_PRESETS
from core.models import SimulationParams
from rendering.colormaps import normalize_field
from services.random_error_module import run_random_error_disturbance
from utils.helpers import hex_to_rgb

FIG211_STAGE_ORDER = ['stage_1', 'stage_2', 'stage_3', 'stage_4']


def cleanup_fig211_generated_images(preset_key: str) -> None:
    """Remove older generated Figure 2.11 outputs for the same preset."""
    prefix = f"figure_2_11_{preset_key}"
    images_dir = Path(IMAGES_DIR)
    for existing in images_dir.glob(f"{prefix}*.png"):
        if existing.is_file():
            try:
                existing.unlink()
            except FileNotFoundError:
                pass


def save_fig211_generated_image(
    rgb: np.ndarray,
    preset_key: str,
    color1: str,
    color2: str,
    *,
    tag: str | None = None,
) -> str:
    """Save a Figure 2.11 render while keeping only the latest file per preset."""
    cleanup_fig211_generated_images(preset_key)
    tag_suffix = f"_{tag}" if tag else ""
    color_hash = hashlib.sha1(f"{preset_key}|{tag or 'base'}|{color1}|{color2}".encode("utf-8")).hexdigest()[:10]
    output_name = f"figure_2_11_{preset_key}{tag_suffix}_{color_hash}.png"
    output_path = Path(IMAGES_DIR) / output_name
    Image.fromarray((np.clip(rgb, 0.0, 1.0) * 255).astype(np.uint8)).save(output_path)
    return str(output_path)


@lru_cache(maxsize=1)
def fig211_global_normalization_bounds():
    """Compute a shared normalization range across the verified reference stages."""
    samples = []
    for preset_key in FIG211_STAGE_ORDER:
        spec = SPOTS_211_PRESETS[preset_key]
        stage_path = FIG211_REFERENCE_DIR / spec['source_file']
        if not stage_path.exists():
            continue
        with Image.open(stage_path) as img:
            arr = np.asarray(img.convert('L'), dtype=np.float32) / 255.0
            samples.append(arr.reshape(-1))

    if not samples:
        return 0.0, 1.0

    stack = np.concatenate(samples)
    p02 = float(np.percentile(stack, 2))
    p98 = float(np.percentile(stack, 98))
    if not np.isfinite(p02):
        p02 = 0.0
    if not np.isfinite(p98) or p98 <= p02:
        p98 = min(p02 + 1e-6, 1.0)
    return p02, p98


def colorize_fig211_stage(texture_service, preset_key: str, color1: str, color2: str) -> str:
    """Recolor a verified Figure 2.11 stage image using the selected palette."""
    stage_spec = SPOTS_211_PRESETS.get(preset_key, SPOTS_211_PRESETS['stage_2'])
    source_path = FIG211_REFERENCE_DIR / stage_spec['source_file']
    if source_path.exists():
        with Image.open(source_path) as img:
            gray = np.asarray(img.convert('L'), dtype=np.float32) / 255.0
    else:
        base_params = dict(MODEL_211_PARAMS.get("params", {}))
        reference_t = float(stage_spec.get('reference_t', base_params.get('t_max', 1.0)))
        sim_params = SimulationParams(
            name="figure_211_spots",
            preset_name=preset_key,
            K=float(base_params.get("K", 1.0)),
            t_max=max(reference_t, float(base_params.get('dt', 0.1))),
            delta_t=float(base_params.get("dt", 0.1)),
            size=int(base_params.get("size", 256)),
            dx=float(base_params.get("dx", 1.0)),
            random_seed=int(base_params.get("seed", 12345)),
            s=float(base_params.get("s", 0.01)),
            r_a=float(base_params.get("r_a", 0.01)),
            r_b=float(base_params.get("r_b", 0.02)),
            b_a=float(base_params.get("b_a", 0.001)),
            b_b=float(base_params.get("b_b", 0.0)),
            D_a=float(base_params.get("D_a", 0.01)),
            D_b=float(base_params.get("D_b", 0.4)),
            A0=0.1,
            B0=1.0,
            initial_noise_a_amplitude=0.05,
            initial_noise_b_amplitude=0.01,
            extras={
                "color1": color1,
                "color2": color2,
                "mode_key": "spots",
                "stage_key": preset_key,
            },
        )
        output = texture_service.simulation_service.run_activator_inhibitor(sim_params)
        gray = 1.0 - np.clip(normalize_field(output.A), 0.0, 1.0)

    p02, p98 = fig211_global_normalization_bounds()
    normalized = np.clip((gray - p02) / max(p98 - p02, 1e-6), 0.0, 1.0)
    normalized = normalized ** 1.05

    # Use the verified stage as a mask: low grayscale values become stronger spots.
    spot_strength = np.clip(0.15 + 0.70 * (1.0 - normalized), 0.0, 1.0)

    bg_rgb = np.array(hex_to_rgb(color1), dtype=np.float32)
    spot_rgb = np.array(hex_to_rgb(color2), dtype=np.float32)

    rgb = (
        bg_rgb[None, None, :] * (1.0 - spot_strength[..., None]) +
        spot_rgb[None, None, :] * spot_strength[..., None]
    )
    rgb = np.clip(rgb, 0.0, 1.0)

    return save_fig211_generated_image(rgb, preset_key, color1, color2)


def apply_fig211_random_error(
    gray: np.ndarray,
    preset_key: str,
    random_error_params: dict | None,
    *,
    disturbance_fn=None,
) -> np.ndarray:
    """Apply a controlled random-error disturbance to a Figure 2.11 grayscale stage."""
    stage_defaults = dict(SPOTS_211_RANDOM_ERROR_PRESETS.get(preset_key, SPOTS_211_RANDOM_ERROR_PRESETS['stage_2']))
    if random_error_params:
        stage_defaults.update({k: random_error_params[k] for k in stage_defaults.keys() if k in random_error_params})

    enabled = bool(
        random_error_params.get('enabled', stage_defaults.get('enabled', False))
        if random_error_params
        else stage_defaults.get('enabled', False)
    )
    if not enabled:
        return gray
    stage_defaults['enabled'] = True

    if disturbance_fn is None:
        from routes import api as api_module

        disturbance_fn = getattr(api_module, "run_random_error_disturbance", run_random_error_disturbance)

    strength = float(stage_defaults.get('strength', 0.014))
    region_size = max(4, int(stage_defaults.get('region_size', 9)))
    num_regions = max(1, int(stage_defaults.get('num_regions', 3)))
    alpha_var = float(stage_defaults.get('alpha_var', 0.15))
    beta = float(stage_defaults.get('beta', 0.08))

    seed_material = f"{preset_key}|{strength:.4f}|{region_size}|{num_regions}|{alpha_var:.4f}|{beta:.4f}"
    seed = int(hashlib.sha1(seed_material.encode('utf-8')).hexdigest()[:8], 16)
    disturbed_a, disturbed_b = disturbance_fn(
        gray,
        stage_defaults,
        B=np.clip(1.0 - gray, 0.0, 1.0),
        seed=seed,
        steps=max(1, int(stage_defaults.get('duration', 1))),
        delta_t=1.0,
        clamp_min=0.0,
        clamp_max=1.0,
    )
    if disturbed_b is not None:
        # Preserve the coupled disturbance even though the recoloring uses A.
        _ = disturbed_b
    return disturbed_a
