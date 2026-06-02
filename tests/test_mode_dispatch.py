import pytest
import numpy as np
from types import SimpleNamespace

from core.modes import get_mode_definition, load_mode_registry
from services.mode_service import ModeService
import services.mode_service as mode_service_module


def test_mode_registry_exposes_three_first_class_modes():
    registry = load_mode_registry()
    assert set(registry) == {
        "activator_inhibitor",
        "stable_periodic_patterns",
        "labyrinths",
    }
    assert registry["activator_inhibitor"].solver == "activator_inhibitor"
    assert registry["stable_periodic_patterns"].solver == "activator_inhibitor"
    assert registry["labyrinths"].solver == "labyrinth"


def test_mode_registry_lookup_returns_definition():
    mode = get_mode_definition("labyrinths")
    assert mode.label == "Labyrinths"
    assert mode.stage_based is True


@pytest.mark.parametrize(
    ("mode_key", "method_name"),
    [
        ("activator_inhibitor", "generate_activator_inhibitor"),
        ("stable_periodic_patterns", "generate_stable_periodic_patterns"),
        ("labyrinths", "generate_labyrinths"),
    ],
)
def test_mode_service_generate_mode_dispatches_to_expected_handler(
    monkeypatch,
    mode_key,
    method_name,
):
    service = ModeService()
    calls = []

    def fake_handler(**kwargs):
        calls.append(kwargs)
        return f"{method_name}-result"

    monkeypatch.setattr(service, method_name, fake_handler)

    result = service.generate_mode(mode_key, sample="value")

    assert result == f"{method_name}-result"
    assert calls == [{"sample": "value"}]


def test_mode_service_dispatches_stripe_variant(monkeypatch):
    service = ModeService()
    calls = []

    def fake_handler(**kwargs):
        calls.append(kwargs)
        return "stripe-variant-result"

    monkeypatch.setattr(service, "generate_stable_periodic_patterns", fake_handler)

    result = service.generate_mode("stable_periodic_patterns", stripe_variant="mild_modulation")

    assert result == "stripe-variant-result"
    assert calls == [{"stripe_variant": "mild_modulation"}]


def test_mode_service_merges_progression_overrides_and_spatial_modulation(monkeypatch, tmp_path):
    service = ModeService()

    bundle = {
        "default_stage": "stage_3",
        "development_presets": {
            "dev_10": {
                "label": "Development 10%",
                "progress_percent": 10,
                "t_max": 8.0,
                "snapshot_count": 72,
                "params_override": {
                    "s": 0.0144,
                    "r_a": 0.02,
                    "r_b": 0.049,
                    "D_a": 0.00456,
                    "D_b": 0.276,
                    "b_a": 0.00068,
                    "b_b": 0.01,
                    "B0": 1.0,
                    "dx": 1.0,
                    "random_seed": 42,
                    "initial_noise_a_amplitude": 0.058,
                    "initial_noise_b_amplitude": 0.0115,
                },
                "spatial_modulation": {
                    "enabled": True,
                    "eps_s": 0.012,
                    "eps_Da": 0.0035,
                    "eps_initial_a": 0.018,
                    "eps_initial_b": 0.009,
                    "field_scale": 88.0,
                    "smoothing_passes": 8,
                    "seed_offset": 5,
                },
            }
        },
    }

    captured = {}

    def fake_finalize(mode_key, preset_key, params, image_path, heatmap_data, stage_label="", notes=""):
        captured["params"] = params
        captured["image_path"] = image_path
        captured["heatmap_data"] = heatmap_data
        captured["stage_label"] = stage_label
        captured["notes"] = notes
        return SimpleNamespace()

    class FakeOutput:
        A = np.array([[0.0, 0.1], [0.2, 0.3]], dtype=np.float64)
        B = np.zeros((2, 2), dtype=np.float64)
        heatmap = np.array([[0.0, 0.1], [0.2, 0.3]], dtype=np.float64)
        snapshots = [(0, A, B)]

    def fake_run(params, export_snapshots=False, random_error_params=None):
        captured["export_snapshots"] = export_snapshots
        captured["random_error_params"] = random_error_params
        return FakeOutput()

    monkeypatch.setattr(mode_service_module, "load_figure_23_presets", lambda: bundle)
    monkeypatch.setattr(service.simulation_service, "run_activator_inhibitor", fake_run)
    monkeypatch.setattr(mode_service_module, "save_stripe_texture_image", lambda *args, **kwargs: str(tmp_path / "texture.png"))
    monkeypatch.setattr(service, "_finalize", fake_finalize)

    service.generate_stable_periodic_patterns(
        development_percent=10,
        params_override={"r_b": 0.123},
        spatial_modulation_override={"eps_s": 0.01},
        color1="#f3e7c6",
        color2="#101010",
    )

    assert captured["export_snapshots"] is False
    assert captured["random_error_params"] is None
    assert captured["params"].r_b == 0.123
    assert captured["params"].extras["snapshot_count"] == 72
    assert captured["params"].extras["spatial_modulation"]["eps_s"] == 0.01


def test_mode_service_uses_progression_snapshot_for_texture_export(monkeypatch, tmp_path):
    service = ModeService()

    bundle = {
        "default_stage": "stage_3",
        "development_presets": {
            "dev_60": {
                "label": "Development 60%",
                "progress_percent": 60,
                "t_max": 54.0,
                "snapshot_count": 3,
                "params_override": {
                    "s": 0.0144,
                    "r_a": 0.02,
                    "r_b": 0.0496,
                    "D_a": 0.00456,
                    "D_b": 0.330,
                    "b_a": 0.00068,
                    "b_b": 0.01,
                    "B0": 1.0,
                    "dx": 1.0,
                    "random_seed": 42,
                    "initial_noise_a_amplitude": 0.050,
                    "initial_noise_b_amplitude": 0.0100,
                },
                "spatial_modulation": {
                    "enabled": True,
                    "eps_s": 0.025,
                    "eps_Da": 0.0068,
                    "eps_initial_a": 0.024,
                    "eps_initial_b": 0.012,
                    "field_scale": 68.0,
                    "smoothing_passes": 8,
                    "seed_offset": 17,
                },
            }
        },
    }

    captured = {}

    class FakeOutput:
        A = np.array([[0.0, 0.1], [0.2, 0.3]], dtype=np.float64)
        B = np.zeros((2, 2), dtype=np.float64)
        heatmap = np.array([[0.9, 0.9], [0.9, 0.9]], dtype=np.float64)
        snapshots = [
            (0, np.array([[0.1, 0.1], [0.1, 0.1]], dtype=np.float64), np.zeros((2, 2))),
            (1, np.array([[0.5, 0.5], [0.5, 0.5]], dtype=np.float64), np.zeros((2, 2))),
            (2, np.array([[0.9, 0.9], [0.9, 0.9]], dtype=np.float64), np.zeros((2, 2))),
        ]

    def fake_run(params, export_snapshots=False, random_error_params=None):
        captured["export_snapshots"] = export_snapshots
        return FakeOutput()

    def fake_save_stripe_texture_image(field, color1, color2, output_path, **kwargs):
        captured["field"] = np.asarray(field)
        captured["texture_kwargs"] = kwargs
        return str(tmp_path / "texture.png")

    monkeypatch.setattr(mode_service_module, "load_figure_23_presets", lambda: bundle)
    monkeypatch.setattr(service.simulation_service, "run_activator_inhibitor", fake_run)
    monkeypatch.setattr(mode_service_module, "save_stripe_texture_image", fake_save_stripe_texture_image)
    monkeypatch.setattr(service, "_finalize", lambda *args, **kwargs: SimpleNamespace())

    service.generate_stable_periodic_patterns(
        development_percent=60,
        color1="#f3e7c6",
        color2="#101010",
    )

    assert captured["export_snapshots"] is False
    assert np.allclose(captured["field"], FakeOutput.snapshots[1][1])
    assert captured["texture_kwargs"]["texture_mix"] < 0.65
    assert captured["texture_kwargs"]["phase_strength"] < 0.28
