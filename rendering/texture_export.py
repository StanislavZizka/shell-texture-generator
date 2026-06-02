"""Image export helpers for simulation results."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

from rendering.colormaps import blend_fields_to_rgb


def save_texture_image(
    A: np.ndarray,
    B: np.ndarray,
    color1: str,
    color2: str,
    output_path: str | Path,
) -> str:
    """Save a blended texture image and return the filesystem path."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    rgb = blend_fields_to_rgb(A, B, color1, color2)
    Image.fromarray((rgb * 255).astype(np.uint8)).save(path)
    return str(path)

