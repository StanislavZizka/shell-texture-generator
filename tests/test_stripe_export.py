from pathlib import Path

import numpy as np
from PIL import Image

from rendering.stripe_export import save_stripe_texture_image


def test_save_stripe_texture_image_emphasizes_vertical_bands(tmp_path):
    x = np.linspace(0.0, 4.0 * np.pi, 128, dtype=np.float64)
    heatmap = np.tile(0.5 + 0.5 * np.sin(x), (128, 1))
    output_path = tmp_path / "stripe.png"

    saved = save_stripe_texture_image(heatmap, "#f3e7c6", "#101010", output_path)
    assert Path(saved).exists()

    image = np.asarray(Image.open(saved).convert("RGB"), dtype=np.float64)
    column_profile = image.mean(axis=(0, 2))
    row_profile = image.mean(axis=(1, 2))

    assert column_profile.std() > row_profile.std()
    assert image.std() > 0.0


def test_save_stripe_texture_image_random_error_breaks_continuity_without_losing_stripes(tmp_path):
    x = np.linspace(0.0, 4.0 * np.pi, 128, dtype=np.float64)
    base_heatmap = np.tile(0.5 + 0.5 * np.sin(x), (128, 1))
    output_clean = tmp_path / "stripe_clean.png"
    output_error = tmp_path / "stripe_error.png"

    clean = np.asarray(
        Image.open(save_stripe_texture_image(base_heatmap, "#f3e7c6", "#101010", output_clean)).convert("RGB"),
        dtype=np.float64,
    )
    error = np.asarray(
        Image.open(
            save_stripe_texture_image(
                base_heatmap,
                "#f3e7c6",
                "#101010",
                output_error,
                random_error_params={
                    "enabled": True,
                    "strength": 0.024,
                    "duration": 14,
                    "frequency": 0.050,
                    "probability": 0.035,
                    "num_regions": 2,
                    "region_size": 12,
                    "jitter": 0.12,
                    "micro_noise": 0.06,
                    "alpha_var": 0.24,
                    "beta": 0.09,
                    "drift_x": 1.10,
                    "drift_y": 1.00,
                    "drift_frequency": 0.0022,
                },
            )
        ).convert("RGB"),
        dtype=np.float64,
    )

    clean_row_profile = clean.mean(axis=(1, 2))
    error_row_profile = error.mean(axis=(1, 2))
    clean_column_profile = clean.mean(axis=(0, 2))
    error_column_profile = error.mean(axis=(0, 2))
    column_diff = np.abs(clean - error).mean(axis=(0, 2))

    assert np.mean(np.abs(clean - error)) > 0.18
    assert error_column_profile.std() > error_row_profile.std()
    assert error_column_profile.std() >= clean_column_profile.std() * 0.80
    assert error_column_profile.std() > 0.0
    assert column_diff.max() > column_diff.mean() * 1.8
    assert np.mean(column_diff > column_diff.mean() + 0.5 * column_diff.std()) < 0.45


def test_save_stripe_texture_image_local_y_segment_error_is_vertical_and_localized(tmp_path):
    x = np.linspace(0.0, 4.0 * np.pi, 160, dtype=np.float64)
    base_heatmap = np.tile(0.5 + 0.5 * np.sin(x), (160, 1))
    output_clean = tmp_path / "stripe_clean_y.png"
    output_error = tmp_path / "stripe_error_y.png"

    clean = np.asarray(
        Image.open(save_stripe_texture_image(base_heatmap, "#f3e7c6", "#101010", output_clean)).convert("RGB"),
        dtype=np.float64,
    )
    error = np.asarray(
        Image.open(
            save_stripe_texture_image(
                base_heatmap,
                "#f3e7c6",
                "#101010",
                output_error,
                random_error_params={
                    "enabled": True,
                    "local_y_segments": True,
                    "strength": 0.03,
                    "duration": 11,
                    "frequency": 0.048,
                    "probability": 0.028,
                    "num_regions": 3,
                    "region_size": 10,
                    "jitter": 0.11,
                    "micro_noise": 0.04,
                    "alpha_var": 0.22,
                    "beta": 0.085,
                    "drift_x": 0.98,
                    "drift_y": 0.88,
                    "drift_frequency": 0.002,
                },
            )
        ).convert("RGB"),
        dtype=np.float64,
    )

    row_diff = np.abs(clean - error).mean(axis=(1, 2))
    column_diff = np.abs(clean - error).mean(axis=(0, 2))

    assert np.mean(np.abs(clean - error)) > 0.10
    assert column_diff.max() > column_diff.mean() * 1.25
    assert column_diff.std() > 0.35
    assert np.mean(column_diff > column_diff.mean() + 0.5 * column_diff.std()) < 0.50
    assert row_diff.std() > 0.05
