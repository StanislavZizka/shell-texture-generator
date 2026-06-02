"""Figure 2.12 generation helper extracted from the texture generator service."""

from __future__ import annotations

import os

import numpy as np
from PIL import Image

from config import DEFAULT_TEXTURE_SIZE, IMAGES_DIR
from config_models import MODEL_212_PARAMS, RANDOM_ERROR_212_STAGES
from services.random_error_module import RandomErrorModule, create_random_error_params
from utils.helpers import hex_to_rgb


def generate_activator_inhibitor_212(
    service,
    stage: int,
    color1: str,
    color2: str,
    size: int = DEFAULT_TEXTURE_SIZE,
    random_error_params: dict | None = None,
) -> str:
    """Generate Figure 2.12 activator-inhibitor labyrinth texture for a selected stage."""

    if stage not in (1, 2, 3, 4, 5):
        raise ValueError("stage must be an integer in [1, 5]")

    p = dict(MODEL_212_PARAMS)
    t_max = float(p["stage_tmax_map"][int(stage)])
    delta_t = float(p["delta_t"])
    dx = float(p.get("dx", 1.0))

    np.random.seed(int(p.get("random_seed", 42)))
    A = np.ones((size, size), dtype=float) * 0.1
    B = np.ones((size, size), dtype=float) * 1.0
    A += (np.random.rand(size, size) - 0.5) * 0.05
    B += (np.random.rand(size, size) - 0.5) * 0.01

    D_a_eff = float(p["K"]) * float(p["D_a"])
    D_b_eff = float(p["K"]) * float(p["D_b"])
    s = float(p["s"])
    r_a = float(p["r_a"])
    r_b = float(p["r_b"])
    b_a = float(p["b_a"])
    b_b = float(p["b_b"])

    steps = int(t_max / delta_t)
    stage_re_defaults = dict(RANDOM_ERROR_212_STAGES.get(f"stage{int(stage)}", {}))
    re_defaults = create_random_error_params(
        enabled=False,
        strength=float(stage_re_defaults.get("strength", 0.01)),
        duration=int(stage_re_defaults.get("duration", 10)),
        frequency=float(stage_re_defaults.get("frequency", 0.05)),
        probability=float(stage_re_defaults.get("probability", 0.05)),
        num_regions=int(stage_re_defaults.get("num_regions", 3)),
        region_size=int(stage_re_defaults.get("region_size", 15)),
    )
    re_params = dict(re_defaults)
    if random_error_params:
        re_params.update(random_error_params)
    random_error_enabled = bool(re_params.get("enabled", False))
    re_module = RandomErrorModule(size=A.shape, seed=int(p.get("random_seed", 42))) if random_error_enabled else None

    for step in range(steps):
        lap_A = service._calculate_laplacian(A, dx)
        lap_B = service._calculate_laplacian(B, dx)
        B_safe = np.maximum(B, 1e-10)

        dA_dt = s * (A**2 / B_safe + b_a) - r_a * A + D_a_eff * lap_A
        dB_dt = s * (A**2) - r_b * B + b_b + D_b_eff * lap_B

        A += delta_t * dA_dt
        B += delta_t * dB_dt

        if random_error_enabled and re_module is not None:
            t = step * delta_t
            R = re_module.apply_random_error(A, t, step, re_params)
            A += R
            B += re_params.get("beta", 0.10) * R

        np.clip(A, 0.0, 5.0, out=A)
        np.clip(B, 0.0, 5.0, out=B)

    A_display = A / (1.0 + A + 1e-12)
    color1_rgb = np.array(hex_to_rgb(color1), dtype=float)
    color2_rgb = np.array(hex_to_rgb(color2), dtype=float)

    img_data = np.zeros((size, size, 3), dtype=float)
    for i in range(3):
        img_data[:, :, i] = np.clip(
            color1_rgb[i] * A_display + color2_rgb[i] * (1.0 - A_display),
            0.0,
            1.0,
        )

    suffix = "_re" if random_error_enabled else ""
    filename = f"activator_inhibitor_212_stage{stage}{suffix}.png"
    output_path = os.path.join(IMAGES_DIR, filename)

    img_pil = Image.fromarray((img_data * 255).astype("uint8"))
    img_pil.save(output_path)
    return output_path
