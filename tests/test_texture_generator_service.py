from __future__ import annotations

from pathlib import Path

from PIL import Image

from services.texture_generator import TextureGeneratorService


def test_texture_generator_service_forwards_stripe_variant(monkeypatch, tmp_path):
    service = TextureGeneratorService()
    source_image = tmp_path / "stripe_variant.png"
    Image.new("RGB", (4, 4), color=(128, 128, 128)).save(source_image)

    calls = []

    def fake_generate(*args, **kwargs):
        calls.append(kwargs)
        class _Result:
            image_path = str(source_image)
            heatmap_data = [[0.0]]
        return _Result()

    monkeypatch.setattr(service.mode_service, "generate_stable_periodic_patterns", fake_generate)

    image_path, heatmap = service.generate_stable_periodic_patterns(
        stripe_variant="mild_modulation",
        params_override={"r_b": 0.123},
        spatial_modulation_override={"eps_s": 0.01},
        color1="#f3e7c6",
        color2="#101010",
    )

    assert Path(image_path).exists()
    assert heatmap == [[0.0]]
    assert calls and calls[0]["stripe_variant"] == "mild_modulation"
    assert calls[0]["params_override"] == {"r_b": 0.123}
    assert calls[0]["spatial_modulation_override"] == {"eps_s": 0.01}
