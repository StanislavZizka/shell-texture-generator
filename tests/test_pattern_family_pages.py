import numpy as np
import pytest
from PIL import Image

import routes.api as api_module
from app import create_app


@pytest.fixture()
def app_client():
    app = create_app("testing")
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.mark.parametrize(
    "path, title",
    [
        ("/spots_211", b"Figure 2.11 - Spots"),
        ("/activator_212", b"Figure 2.12 - Labyrinths"),
    ],
)
def test_pattern_family_pages_render(app_client, path, title):
    response = app_client.get(path)
    assert response.status_code == 200

    data = response.data
    assert title in data
    assert b"parameter_mode" in data
    assert b"patternParameterAccordion" in data
    assert b"patternParameterEmpty" in data
    assert b"enable_random_error" in data
    assert b"patternRandomErrorGroup" in data
    assert b"patternRandomErrorPreview" in data
    assert b"patternDynamicModeHint" in data
    assert b"patternRandomErrorPanel" not in data
    assert b"figure-panel--form" in data
    assert b"figure-panel--result" in data
    assert b"figure-panel--viewer" in data
    assert b"textureHeatmapSection" in data
    assert b"textureHeatmapCanvas" in data
    assert b"textureHeatmapView" in data
    assert b"textureHeatmapDownload" in data
    assert b"textureHeatmapToggleLabel" in data
    assert b"Please select a stage first." in data
    assert b"texture-heatmap.js" in data
    assert b"shellSelect" in data
    assert b"threejs-container" in data
    assert b"modelLoading" in data
    assert b"modelActions" in data
    assert b"vendor/three/three.min.js" in data
    assert b"vendor/three/examples/js/controls/OrbitControls.js" in data
    assert b"vendor/three/examples/js/loaders/OBJLoader.js" in data
    assert b"vendor/three/examples/js/loaders/MTLLoader.js" in data
    assert b"js/components/shell-viewer.js" in data
    assert b"js/components/appearance-switcher.js" in data
    assert b"unpkg.com/three" not in data
    assert b"Generate texture" in data or b"Generate Texture" in data
    assert b'nav-home' in data
    assert b'nav-activator-inhibitor' in data
    assert b'nav-figure23' in data
    assert b'nav-figure211' in data
    assert b'nav-figure212' in data

    if path == "/spots_211":
        assert b"patternRandomErrorPreview" in data
        assert b"patternRandomErrorEditHint" in data
        assert b"figure-panel--form" in data
        assert b"figure-panel--result" in data
        assert b"figure-panel--viewer" in data
        assert b"figure211-page-title" in data
        assert b"figure211-page-subtitle" in data
    elif path == "/activator_212":
        assert b"patternRandomErrorPreview" in data
        assert b"patternRandomErrorEditHint" in data
        assert b"figure-panel--form" in data
        assert b"figure-panel--result" in data
        assert b"figure-panel--viewer" in data
        assert b"figure212-page-title" in data
        assert b"figure212-page-subtitle" in data
        assert b"0.0395" in data
        assert b"0.075" in data
    else:
        assert b"pattern_stage" in data
        assert b"fig23RandomErrorEditHint" in data
        assert b'role="switch"' in data
        assert b"Select an option" in data
        assert b"figure23-page-title" in data
        assert b"figure23-page-subtitle" in data
        assert b"3d-visualization" in data
        assert b"select-shell-type" in data
        assert b"textureHeatmapSection" in data
        assert b"textureHeatmapNote" in data


def test_generate_211_supports_development_percent_and_random_error(app_client, tmp_path, monkeypatch):
    source_image = tmp_path / "spots_source.png"
    Image.new("RGB", (4, 4), color=(200, 200, 200)).save(source_image)

    monkeypatch.setattr(api_module, "IMAGES_DIR", str(tmp_path))
    monkeypatch.setattr(
        api_module,
        "_colorize_fig211_stage",
        lambda *args, **kwargs: str(source_image),
    )

    captured = {}

    def fake_apply(gray, preset_key, random_error_params):
        captured["preset_key"] = preset_key
        captured["params"] = random_error_params
        return gray

    monkeypatch.setattr(api_module, "_apply_fig211_random_error", fake_apply)

    response = app_client.post(
        "/api/generate-211",
        json={
            "development_percent": 60,
            "enable_random_error": True,
            "re_strength": 0.02,
            "re_duration": 16,
            "re_frequency": 0.05,
            "re_probability": 0.03,
            "re_num_regions": 2,
            "re_region_size": 12,
            "re_jitter": 0.12,
            "re_micro_noise": 0.05,
            "re_alpha_var": 0.24,
            "re_beta": 0.10,
            "re_drift_x": 1.1,
            "re_drift_y": 1.0,
            "re_drift_frequency": 0.002,
            "color1": "#d9d9d9",
            "color2": "#2b2b2b",
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["preset"] == "dev_60"
    assert payload["development_percent"] == 60
    assert payload["random_error_enabled"] is True
    assert payload["development_spec"]["stage_key"] == "stage_3"
    assert captured["preset_key"] == "stage_3"
    assert captured["params"]["enabled"] is True
    assert captured["params"]["disturbance_kind"] == "spots"


def test_generate_211_uses_shared_random_error_disturbance(app_client, tmp_path, monkeypatch):
    source_image = tmp_path / "spots_disturbance.png"
    Image.new("RGB", (4, 4), color=(180, 180, 180)).save(source_image)

    captured = {}

    def fake_generate(*args, **kwargs):
        captured["kwargs"] = kwargs
        return str(source_image), None

    monkeypatch.setattr(api_module.texture_service, "generate_activator_inhibitor", fake_generate)

    response = app_client.post(
        "/api/generate-211",
        json={
            "stage": 3,
            "enable_random_error": True,
            "re_strength": 0.025,
            "re_duration": 14,
            "re_frequency": 0.05,
            "re_probability": 0.03,
            "re_num_regions": 2,
            "re_region_size": 10,
            "re_jitter": 0.11,
            "re_micro_noise": 0.04,
            "re_alpha_var": 0.20,
            "re_beta": 0.08,
            "re_drift_x": 0.9,
            "re_drift_y": 0.8,
            "re_drift_frequency": 0.002,
            "color1": "#d9d9d9",
            "color2": "#2b2b2b",
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["random_error_enabled"] is True
    assert captured["kwargs"]["preset_name"] == "stage_3"
    assert captured["kwargs"]["t_max"] == 1050.0
    assert captured["kwargs"]["random_error_params"]["enabled"] is True
    assert captured["kwargs"]["random_error_params"]["duration"] == 14
    assert captured["kwargs"]["random_error_params"]["strength"] == 0.025


def test_generate_211_supports_stage_and_default_aliases(app_client, tmp_path, monkeypatch):
    source_image = tmp_path / "spots_stage.png"
    Image.new("RGB", (4, 4), color=(190, 190, 190)).save(source_image)

    captured = {}

    def fake_generate(*args, **kwargs):
        captured["kwargs"] = kwargs
        return str(source_image), None

    monkeypatch.setattr(api_module.texture_service, "generate_activator_inhibitor", fake_generate)

    response = app_client.post(
        "/api/generate-211",
        json={
            "stage": 2,
            "color1": "#d9d9d9",
            "color2": "#2b2b2b",
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["preset"] == "stage_2"
    assert payload["stage_label"]
    assert captured["kwargs"]["preset_name"] == "stage_2"
    assert captured["kwargs"]["t_max"] == 510.0
    assert captured["kwargs"]["params_override"]["initial_noise_a_amplitude"] == 0.048
    assert captured["kwargs"]["params_override"]["D_b"] == 0.403


def test_generate_211_defaults_to_stage_3_when_no_preset_is_given(app_client, tmp_path, monkeypatch):
    source_image = tmp_path / "spots_default.png"
    Image.new("RGB", (4, 4), color=(195, 195, 195)).save(source_image)

    captured = {}

    def fake_generate(*args, **kwargs):
        captured["kwargs"] = kwargs
        return str(source_image), None

    monkeypatch.setattr(api_module.texture_service, "generate_activator_inhibitor", fake_generate)

    response = app_client.post(
        "/api/generate-211",
        json={
            "color1": "#d9d9d9",
            "color2": "#2b2b2b",
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["preset"] == "stage_3"
    assert payload["stage_label"]
    assert captured["kwargs"]["preset_name"] == "stage_3"
    assert captured["kwargs"]["t_max"] == 1050.0
    assert captured["kwargs"]["params_override"]["initial_noise_a_amplitude"] == 0.045
    assert captured["kwargs"]["params_override"]["D_b"] == 0.399


def test_generate_211_balanced_alias_maps_to_stage_3(app_client, tmp_path, monkeypatch):
    source_image = tmp_path / "spots_balanced.png"
    Image.new("RGB", (4, 4), color=(205, 205, 205)).save(source_image)

    captured = {}

    def fake_generate(*args, **kwargs):
        captured["kwargs"] = kwargs
        return str(source_image), None

    monkeypatch.setattr(api_module.texture_service, "generate_activator_inhibitor", fake_generate)

    response = app_client.post(
        "/api/generate-211",
        json={
            "preset": "balanced",
            "color1": "#d9d9d9",
            "color2": "#2b2b2b",
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["preset"] == "stage_3"
    assert payload["stage_label"]
    assert captured["kwargs"]["preset_name"] == "stage_3"
    assert captured["kwargs"]["t_max"] == 1050.0


def test_generate_212_supports_development_percent_and_random_error(app_client, tmp_path, monkeypatch):
    source_image = tmp_path / "labyrinth_source.png"
    Image.new("RGB", (4, 4), color=(140, 140, 140)).save(source_image)

    calls = []

    def fake_generate(*args, **kwargs):
        calls.append(kwargs)
        return str(source_image)

    monkeypatch.setattr(api_module.texture_service, "generate_labyrinths", fake_generate)

    response = app_client.post(
        "/api/generate-212",
        json={
            "development_percent": 90,
            "enable_random_error": True,
            "re_strength": 0.005,
            "re_duration": 10,
            "re_frequency": 0.05,
            "re_probability": 0.08,
            "re_num_regions": 3,
            "re_region_size": 20,
            "re_jitter": 0.10,
            "re_micro_noise": 0.05,
            "re_alpha_var": 0.20,
            "re_beta": 0.10,
            "re_drift_x": 1.0,
            "re_drift_y": 1.0,
            "re_drift_frequency": 0.002,
            "color1": "#ffffff",
            "color2": "#000000",
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["preset"] == "dev_90"
    assert payload["development_percent"] == 90
    assert payload["random_error_enabled"] is True
    assert payload["stage"] == 5
    assert calls and calls[0]["random_error_params"]["enabled"] is True
    assert calls[0]["random_error_params"]["disturbance_kind"] == "labyrinth"
    assert calls[0]["stage"] == 5
