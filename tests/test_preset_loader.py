from pathlib import Path

import numpy as np

import routes.api_fig211_helpers as fig211_helpers
from config_211 import FIG211_REFERENCE_DIR
from core.presets import (
    load_activator_inhibitor_presets,
    load_figure_211_presets,
    load_figure_212_presets,
    load_figure_23_presets,
)


def test_activator_inhibitor_presets_load_from_json():
    presets = load_activator_inhibitor_presets()
    assert "balanced" in presets
    assert presets["balanced"]["D_b"] == 0.5
    assert presets["low_diffusion"]["re_num_regions"] > presets["high_diffusion"]["re_num_regions"]
    assert presets["high_diffusion"]["re_drift_x"] < presets["low_diffusion"]["re_drift_x"]


def test_figure_23_bundle_loads():
    bundle = load_figure_23_presets()
    assert bundle["default_stage"] == "stage_3"
    assert bundle["stages"]["stage_3"]["params_override"]["D_b"] == 0.345
    assert "stripe_variants" in bundle
    assert bundle["stripe_variants"]["mild_modulation"]["spatial_modulation"]["enabled"] is True
    assert "progression_levels" in bundle
    assert bundle["progression_levels"]["malo"]["label"] == "Málo"
    assert bundle["progression_levels"]["malo"]["spatial_modulation"]["enabled"] is True
    assert bundle["development_presets"]["dev_10"]["snapshot_count"] == 72
    assert bundle["random_error_presets"]["dev_10"]["strength"] < bundle["random_error_presets"]["dev_90"]["strength"]
    assert bundle["random_error_presets"]["dev_60"]["num_regions"] == 2
    assert "beta" in bundle["random_error_presets"]["dev_30"]


def test_figure_211_bundle_loads_with_development_presets():
    bundle = load_figure_211_presets()
    assert bundle["default_development"] == "dev_60"
    assert bundle["development_presets"]["dev_60"]["stage_key"] == "stage_3"
    assert bundle["development_random_error_presets"]["dev_90"]["strength"] == 0.075
    assert bundle["spots_presets"]["stage_1"]["params_override"]["initial_noise_a_amplitude"] == 0.052
    assert bundle["spots_presets"]["stage_4"]["params_override"]["early_smoothing_strength"] == 0.11
    assert bundle["spots_presets"]["stage_1"]["params_override"]["D_b"] > bundle["spots_presets"]["stage_4"]["params_override"]["D_b"]
    assert bundle["random_error_presets"]["stage_1"]["strength"] < bundle["random_error_presets"]["stage_4"]["strength"]
    assert bundle["random_error_presets"]["stage_4"]["drift_x"] > bundle["random_error_presets"]["stage_1"]["drift_x"]


def test_figure_212_bundle_loads_with_development_presets():
    bundle = load_figure_212_presets()
    assert bundle["default_development"] == "dev_60"
    assert bundle["development_presets"]["dev_60"]["stage_key"] == "stage_3"
    assert bundle["stage_presets"]["stage_1"]["params_override"]["initial_noise_a_amplitude"] == 0.0375
    assert bundle["stage_presets"]["stage_2"]["params_override"]["initial_noise_b_amplitude"] == 0.0074
    assert bundle["stage_presets"]["stage_3"]["params_override"]["initial_noise_smoothing_passes"] == 2
    assert bundle["stage_presets"]["stage_4"]["params_override"]["early_smoothing_fraction"] == 0.16
    assert bundle["stage_presets"]["stage_5"]["params_override"]["early_smoothing_strength"] == 0.075
    assert bundle["random_error_presets"]["stage_1"]["strength"] == 0.0045
    assert bundle["random_error_presets"]["stage_2"]["strength"] == 0.0070
    assert bundle["random_error_presets"]["stage_3"]["micro_noise"] == 0.0024
    assert bundle["random_error_presets"]["stage_4"]["alpha_var"] == 0.15
    assert bundle["random_error_presets"]["stage_5"]["probability"] == 0.024
    assert bundle["development_random_error_presets"]["dev_90"]["strength"] == 0.017
    assert bundle["random_error_presets"]["stage_1"]["jitter"] == 0.08
    assert bundle["development_random_error_presets"]["dev_90"]["drift_frequency"] == 0.0015


def test_figure_211_reference_assets_exist():
    bundle = load_figure_211_presets()
    assert FIG211_REFERENCE_DIR.exists()
    for preset_key in ("stage_1", "stage_2", "stage_3", "stage_4"):
        source_file = bundle["spots_presets"][preset_key]["source_file"]
        assert (FIG211_REFERENCE_DIR / source_file).exists()


def test_fig211_generated_image_cleanup_replaces_previous_file(tmp_path, monkeypatch):
    monkeypatch.setattr(fig211_helpers, "IMAGES_DIR", tmp_path)
    rgb = np.zeros((2, 2, 3), dtype=np.float32)

    first_path = fig211_helpers.save_fig211_generated_image(rgb, "stage_1", "#111111", "#222222")
    assert (tmp_path / "figure_2_11_stage_1_base_").exists() is False

    second_path = fig211_helpers.save_fig211_generated_image(rgb, "stage_1", "#111111", "#333333")
    assert first_path != second_path
    assert not (tmp_path / Path(first_path).name).exists()
    assert (tmp_path / Path(second_path).name).exists()
    assert len(list(tmp_path.glob("figure_2_11_stage_1*.png"))) == 1
