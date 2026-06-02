import numpy as np
import pytest

from core.models import SimulationParams
from core.validation import ValidationError, validate_simulation_params
from simulation.activator_inhibitor import simulate_activator_inhibitor
from simulation.laplacian import periodic_laplacian


def _make_params(**overrides):
    base = dict(
        name="test-run",
        preset_name="balanced",
        K=0.5,
        t_max=3.0,
        delta_t=0.5,
        size=32,
        dx=1.0,
        random_seed=123,
        s=1.0,
        r_a=1.0,
        r_b=2.0,
        b_a=0.1,
        b_b=0.1,
        D_a=0.01,
        D_b=0.5,
        A0=0.1,
        B0=1.0,
        initial_noise_a_amplitude=0.05,
        initial_noise_b_amplitude=0.01,
        extras={"color1": "#112233", "color2": "#445566"},
    )
    base.update(overrides)
    return SimulationParams(**base)


def test_periodic_laplacian_of_constant_field_is_zero():
    grid = np.full((4, 4), 3.14)
    lap = periodic_laplacian(grid)
    assert np.allclose(lap, 0.0)


def test_simulation_is_reproducible_for_same_seed():
    params = _make_params()
    result_a = simulate_activator_inhibitor(params)
    result_b = simulate_activator_inhibitor(params)

    assert result_a.A.shape == (32, 32)
    assert result_a.B.shape == (32, 32)
    assert np.all(np.isfinite(result_a.A))
    assert np.all(np.isfinite(result_a.B))
    assert np.allclose(result_a.A, result_b.A)
    assert np.allclose(result_a.B, result_b.B)
    assert result_a.steps == result_b.steps == 6


def test_validate_simulation_params_rejects_invalid_color():
    params = _make_params(extras={"color1": "not-a-color", "color2": "#445566"})
    with pytest.raises(ValidationError):
        validate_simulation_params(params)

