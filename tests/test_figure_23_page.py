from __future__ import annotations

import numpy as np
import pytest
from PIL import Image

import routes.api as api_module
from app import create_app
from config_23 import FIG23_PROGRESSION_LEVELS


@pytest.fixture()
def app_client():
    app = create_app("testing")
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_figure_23_page_renders_dropdown_and_viewer(app_client):
    response = app_client.get("/figure_23")
    assert response.status_code == 200

    data = response.data
    assert b'figure23-page-title' in data
    assert b'figure23-page-subtitle' in data
    assert b'stage-tooltip-info' in data
    assert b'random-error-tooltip-info' in data
    assert b'3d-visualization' in data
    assert b'select-shell-type' in data
    assert b"Select an option" in data
    assert b"progression_level" in data
    assert b"fig23RandomErrorGroup" in data
    assert b"fig23RandomErrorPreview" in data
    assert b"fig23RandomErrorAccordion" in data
    assert b'role="switch"' in data
    assert b"textureHeatmapSection" in data
    assert b"textureHeatmapCanvas" in data
    assert b"textureHeatmapView" in data
    assert b"textureHeatmapDownload" in data
    assert b"textureHeatmapToggleLabel" in data
    assert b"Please select a stage first." in data
    assert b"texture-heatmap.js" in data
    assert b"Raw activator grayscale" not in data
    assert b"progressionImage-malo" not in data
    assert b"threejs-container" in data
    assert b"shell-viewer.js" in data
    assert b"Figure 2.3" in data
    assert b"Generate texture" in data


def test_generate_23_returns_single_progression_level(app_client, monkeypatch, tmp_path):
    source_image = tmp_path / "figure23_source.png"
    Image.new("RGB", (4, 4), color=(170, 170, 170)).save(source_image)

    calls = []

    class FakeModeResult:
        def __init__(self) -> None:
            self.snapshots = [
                (0, np.array([[0.0, 0.1], [0.2, 0.3]], dtype=np.float64), np.zeros((2, 2))),
                (1, np.array([[0.2, 0.3], [0.4, 0.5]], dtype=np.float64), np.zeros((2, 2))),
            ]

    def fake_generate(*args, **kwargs):
        calls.append(kwargs)
        api_module.texture_service.last_mode_result = FakeModeResult()
        return str(source_image), [[0.0]]

    def fake_save_stripe_space_time_image(snapshots, output_path):
        Image.new("L", (4, 4), color=128).save(output_path)
        return str(output_path)

    monkeypatch.setattr(
        api_module.texture_service,
        "generate_stable_periodic_patterns",
        fake_generate,
    )
    monkeypatch.setattr(api_module, "save_stripe_space_time_image", fake_save_stripe_space_time_image)

    response = app_client.post(
        "/api/generate-23",
        json={
            "progression_level": "vice",
            "color1": "#f3e7c6",
            "color2": "#101010",
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["mode"] == "stable_periodic_patterns"
    assert payload["progression_level"] == "vice"
    assert payload["label"] == FIG23_PROGRESSION_LEVELS["vice"]["label"]
    assert payload["image_url"]
    assert payload["space_time_url"]
    assert payload["progression_spec"]["progress_percent"] == FIG23_PROGRESSION_LEVELS["vice"]["progress_percent"]
    assert calls and len(calls) == 1
    assert calls[0]["development_percent"] == FIG23_PROGRESSION_LEVELS["vice"]["progress_percent"]
    assert calls[0]["params_override"] == FIG23_PROGRESSION_LEVELS["vice"]["params_override"]
    assert calls[0]["spatial_modulation_override"] == FIG23_PROGRESSION_LEVELS["vice"]["spatial_modulation"]
    assert payload["image_url"].split("?")[0].endswith("figure23_source.png")


def test_generate_23_supports_random_error_switch_and_defaults(app_client, monkeypatch, tmp_path):
    source_image = tmp_path / "figure23_random_error.png"
    Image.new("RGB", (4, 4), color=(170, 170, 170)).save(source_image)

    captured = {}

    class FakeModeResult:
        def __init__(self) -> None:
            self.snapshots = [
                (0, np.array([[0.0, 0.1], [0.2, 0.3]], dtype=np.float64), np.zeros((2, 2))),
            ]

    def fake_generate(*args, **kwargs):
        captured["kwargs"] = kwargs
        api_module.texture_service.last_mode_result = FakeModeResult()
        return str(source_image), [[0.0]]

    def fake_save_stripe_space_time_image(snapshots, output_path):
        Image.new("L", (4, 4), color=128).save(output_path)
        return str(output_path)

    monkeypatch.setattr(
        api_module.texture_service,
        "generate_stable_periodic_patterns",
        fake_generate,
    )
    monkeypatch.setattr(api_module, "save_stripe_space_time_image", fake_save_stripe_space_time_image)

    response = app_client.post(
        "/api/generate-23",
        json={
            "progression_level": "malo",
            "enable_random_error": True,
            "re_strength": 0.02,
            "re_duration": 12,
            "re_frequency": 0.05,
            "re_probability": 0.03,
            "re_num_regions": 2,
            "re_region_size": 8,
            "re_jitter": 0.10,
            "re_micro_noise": 0.04,
            "re_alpha_var": 0.20,
            "re_beta": 0.08,
            "re_drift_x": 0.8,
            "re_drift_y": 0.8,
            "re_drift_frequency": 0.002,
            "color1": "#f3e7c6",
            "color2": "#101010",
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["progression_level"] == "malo"
    assert payload["random_error_enabled"] is True
    assert payload["random_error_profile"]["enabled"] is True
    assert payload["space_time_url"]
    assert captured["kwargs"]["random_error_params"]["enabled"] is True
    assert captured["kwargs"]["random_error_params"]["strength"] == 0.02
    assert captured["kwargs"]["random_error_params"]["disturbance_kind"] == "stripe"


def test_generate_23_merges_progression_random_error_override(app_client, monkeypatch, tmp_path):
    source_image = tmp_path / "figure23_progression_override.png"
    Image.new("RGB", (4, 4), color=(170, 170, 170)).save(source_image)

    captured = {}

    class FakeModeResult:
        def __init__(self) -> None:
            self.snapshots = [
                (0, np.array([[0.0, 0.1], [0.2, 0.3]], dtype=np.float64), np.zeros((2, 2))),
            ]

    progression_levels = {
        "malo": {
            "label": "Malo",
            "development_key": "dev_10",
            "progress_percent": 10,
            "reference_report": "override test",
            "snapshot_count": 72,
            "random_error_override": {
                "strength": 0.031,
                "duration": 17,
                "frequency": 0.053,
                "probability": 0.044,
                "num_regions": 2,
                "region_size": 13,
                "jitter": 0.13,
                "micro_noise": 0.07,
                "alpha_var": 0.28,
                "beta": 0.10,
                "drift_x": 1.15,
                "drift_y": 0.91,
                "drift_frequency": 0.0024,
            },
            "params_override": {},
        }
    }
    development_defaults = {
        "dev_10": {
            "strength": 0.012,
            "duration": 10,
            "frequency": 0.045,
            "probability": 0.020,
            "num_regions": 1,
            "region_size": 8,
            "jitter": 0.09,
            "micro_noise": 0.04,
            "alpha_var": 0.18,
            "beta": 0.06,
            "drift_x": 0.75,
            "drift_y": 0.70,
            "drift_frequency": 0.0018,
        }
    }

    def fake_generate(*args, **kwargs):
        captured["kwargs"] = kwargs
        api_module.texture_service.last_mode_result = FakeModeResult()
        return str(source_image), [[0.0]]

    def fake_save_stripe_space_time_image(snapshots, output_path):
        Image.new("L", (4, 4), color=128).save(output_path)
        return str(output_path)

    monkeypatch.setattr(api_module, "FIG23_PROGRESSION_LEVELS", progression_levels)
    monkeypatch.setattr(api_module, "FIG23_DEVELOPMENT_RANDOM_ERROR_PRESETS", development_defaults)
    monkeypatch.setattr(
        api_module.texture_service,
        "generate_stable_periodic_patterns",
        fake_generate,
    )
    monkeypatch.setattr(api_module, "save_stripe_space_time_image", fake_save_stripe_space_time_image)

    response = app_client.post(
        "/api/generate-23",
        json={
            "progression_level": "malo",
            "enable_random_error": True,
            "color1": "#f3e7c6",
            "color2": "#101010",
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["random_error_enabled"] is True
    assert captured["kwargs"]["random_error_params"]["strength"] == 0.031
    assert captured["kwargs"]["random_error_params"]["probability"] == 0.044
    assert captured["kwargs"]["random_error_params"]["num_regions"] == 2
    assert captured["kwargs"]["random_error_params"]["region_size"] == 13
    assert payload["random_error_profile"]["strength"] == 0.031
    assert captured["kwargs"]["random_error_params"]["disturbance_kind"] == "stripe"
    assert captured["kwargs"]["random_error_params"]["local_y_segments"] is True


def test_generate_23_stripe_variant_supports_random_error_switch(app_client, monkeypatch, tmp_path):
    source_image = tmp_path / "figure23_variant_random_error.png"
    Image.new("RGB", (4, 4), color=(170, 170, 170)).save(source_image)

    captured = {}

    def fake_generate(*args, **kwargs):
        captured["kwargs"] = kwargs
        return str(source_image), [[0.0]]

    monkeypatch.setattr(
        api_module.texture_service,
        "generate_stable_periodic_patterns",
        fake_generate,
    )

    response = app_client.post(
        "/api/generate-23",
        json={
            "stripe_variant": "mild_modulation",
            "enable_random_error": True,
            "re_strength": 0.024,
            "re_duration": 18,
            "re_frequency": 0.051,
            "re_probability": 0.036,
            "re_num_regions": 2,
            "re_region_size": 14,
            "re_jitter": 0.12,
            "re_micro_noise": 0.03,
            "re_alpha_var": 0.22,
            "re_beta": 0.09,
            "re_drift_x": 1.10,
            "re_drift_y": 0.92,
            "re_drift_frequency": 0.0021,
            "color1": "#f3e7c6",
            "color2": "#101010",
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["stripe_variant"] == "mild_modulation"
    assert payload["random_error_enabled"] is True
    assert payload["random_error_profile"]["enabled"] is True
    assert captured["kwargs"]["stripe_variant"] == "mild_modulation"
    assert captured["kwargs"]["random_error_params"]["enabled"] is True
    assert captured["kwargs"]["random_error_params"]["strength"] == 0.024
    assert captured["kwargs"]["random_error_params"]["disturbance_kind"] == "stripe"
