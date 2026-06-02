"""Heatmap helper extracted from the texture generator service."""

from __future__ import annotations

import os

import numpy as np

from config import IMAGES_DIR

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
except Exception:  # pragma: no cover
    plt = None


def create_biological_heatmap(A: np.ndarray, B: np.ndarray, size: int) -> str:
    """Create biological heatmap visualization showing activator concentration."""

    A_norm = (A - np.min(A)) / max(np.max(A) - np.min(A), 1e-12)

    if plt is None:
        raise RuntimeError("matplotlib is not available; cannot create heatmap.")

    fig, ax = plt.subplots(figsize=(size / 100, size / 100), dpi=100)
    cmap = plt.cm.jet
    ax.imshow(A_norm, cmap=cmap, interpolation='bilinear', origin='lower')
    ax.axis('off')
    plt.tight_layout(pad=0)

    output_path = os.path.join(IMAGES_DIR, "biological_heatmap.png")
    plt.savefig(output_path, bbox_inches='tight', pad_inches=0, dpi=100)
    plt.close(fig)

    return output_path
