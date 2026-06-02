from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

from rendering.stripe_export import save_stripe_raw_image, save_stripe_space_time_image


def test_save_stripe_raw_image_creates_grayscale_png(tmp_path):
    field = np.array([[0.0, 0.5], [1.0, 0.25]], dtype=np.float64)
    output = tmp_path / "raw.png"

    result = save_stripe_raw_image(field, output)

    assert Path(result).exists()
    with Image.open(result) as img:
        assert img.mode == "L"
        assert img.size == (2, 2)


def test_save_stripe_space_time_image_creates_stack_png(tmp_path):
    snapshots = [
        (0, np.array([[0.0, 0.1], [0.2, 0.3]], dtype=np.float64), np.zeros((2, 2))),
        (1, np.array([[0.2, 0.3], [0.4, 0.5]], dtype=np.float64), np.zeros((2, 2))),
        (2, np.array([[0.4, 0.5], [0.6, 0.7]], dtype=np.float64), np.zeros((2, 2))),
    ]
    output = tmp_path / "space_time.png"

    result = save_stripe_space_time_image(snapshots, output)

    assert Path(result).exists()
    with Image.open(result) as img:
        assert img.mode == "L"
        assert img.size == (3, 3)
