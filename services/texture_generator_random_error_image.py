"""Random error image helper extracted from the texture generator service."""

from __future__ import annotations

import os

import numpy as np
from PIL import Image

from config import IMAGES_DIR
from utils.helpers import hex_to_rgb


def create_random_error_image(
    A: np.ndarray,
    B: np.ndarray,
    color1: str,
    color2: str,
    size: int,
    noise_target: str,
    noise_type: str,
) -> str:
    """Create and save the random error texture."""

    a_min, a_max = np.min(A), np.max(A)
    b_min, b_max = np.min(B), np.max(B)
    A_norm = np.clip((A - a_min) / max(a_max - a_min, 1e-12), 0, 1)
    B_norm = np.clip((B - b_min) / max(b_max - b_min, 1e-12), 0, 1)

    color1_rgb = np.array(hex_to_rgb(color1))
    color2_rgb = np.array(hex_to_rgb(color2))

    img_data = np.zeros((size, size, 3))
    for i in range(3):
        img_data[:, :, i] = np.clip(color1_rgb[i] * A_norm + color2_rgb[i] * B_norm, 0, 1)

    filename = f"random_error_{noise_target}_{noise_type}.png"
    output_path = os.path.join(IMAGES_DIR, filename)

    img_pil = Image.fromarray((img_data * 255).astype('uint8'))
    img_pil.save(output_path)
    return output_path
