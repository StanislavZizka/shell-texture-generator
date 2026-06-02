"""Snapshot export helper extracted from the texture generator service."""

from __future__ import annotations

import os

import numpy as np
from PIL import Image

from config import IMAGES_DIR
from utils.helpers import hex_to_rgb


def export_snapshots(snapshots, color1: str, color2: str, size: int):
    """Export intermediate simulation snapshots to the static images directory."""

    color1_rgb = np.array(hex_to_rgb(color1))
    color2_rgb = np.array(hex_to_rgb(color2))

    for step, A, B in snapshots:
        A_norm = (A - np.min(A)) / max(np.max(A) - np.min(A), 1e-12)
        B_norm = (B - np.min(B)) / max(np.max(B) - np.min(B), 1e-12)

        img_data = np.zeros((size, size, 3))
        for i in range(3):
            img_data[:, :, i] = np.clip(color1_rgb[i] * A_norm + color2_rgb[i] * B_norm, 0, 1)

        filename = f"snapshot_step{step:04d}.png"
        output_path = os.path.join(IMAGES_DIR, filename)
        img_pil = Image.fromarray((img_data * 255).astype('uint8'))
        img_pil.save(output_path)

    print(f"Exported {len(snapshots)} snapshots to {IMAGES_DIR}")
