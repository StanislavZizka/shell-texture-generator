import numpy as np

from config_212 import MODEL_212_PARAMS
from core.models import SimulationParams
from simulation.labyrinth import simulate_labyrinth


def _make_labyrinth_params(**overrides):
    base = dict(
        name="labyrinths",
        preset_name="stage_3",
        K=float(MODEL_212_PARAMS["K"]),
        t_max=2.0,
        delta_t=0.5,
        size=24,
        dx=float(MODEL_212_PARAMS["dx"]),
        random_seed=int(MODEL_212_PARAMS["random_seed"]),
        s=float(MODEL_212_PARAMS["s"]),
        r_a=float(MODEL_212_PARAMS["r_a"]),
        r_b=float(MODEL_212_PARAMS["r_b"]),
        b_a=float(MODEL_212_PARAMS["b_a"]),
        b_b=float(MODEL_212_PARAMS["b_b"]),
        D_a=float(MODEL_212_PARAMS["D_a"]),
        D_b=float(MODEL_212_PARAMS["D_b"]),
        A0=0.1,
        B0=1.0,
        initial_noise_a_amplitude=0.05,
        initial_noise_b_amplitude=0.01,
        extras={"color1": "#112233", "color2": "#445566"},
    )
    base.update(overrides)
    return SimulationParams(**base)


def test_labyrinth_simulation_is_reproducible_without_random_error():
    params = _make_labyrinth_params()
    result_a = simulate_labyrinth(params, random_error_params={"enabled": False})
    result_b = simulate_labyrinth(params, random_error_params={"enabled": False})

    assert result_a.A.shape == (24, 24)
    assert result_a.B.shape == (24, 24)
    assert np.all(np.isfinite(result_a.A))
    assert np.all(np.isfinite(result_a.B))
    assert np.allclose(result_a.A, result_b.A)
    assert np.allclose(result_a.B, result_b.B)
