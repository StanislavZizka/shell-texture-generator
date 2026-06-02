from __future__ import annotations

import numpy as np

from simulation.stripe_modulation import build_stripe_modulation_fields


def test_stripe_modulation_x_only_fields_are_constant_over_y():
    fields = build_stripe_modulation_fields(
        (32, 48),
        seed=123,
        config={
            "orientation": "stripe_x",
            "field_scale": 64.0,
            "smoothing_passes": 4,
            "seed_offset": 7,
        },
    )

    for field in (
        fields.s_field,
        fields.da_field,
        fields.initial_a_field,
        fields.initial_b_field,
    ):
        assert field.shape == (32, 48)
        assert np.allclose(field[0], field[-1])
        assert np.allclose(field.min(axis=0), field.max(axis=0))
        assert np.std(field[0]) > 0.0
