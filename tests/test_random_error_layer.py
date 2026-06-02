import numpy as np

from services.random_error_module import (
    RandomErrorModule,
    apply_random_error_step,
    create_random_error_params,
    run_random_error_disturbance,
)


def test_run_random_error_disturbance_is_identity_when_disabled():
    A = np.full((16, 16), 0.5, dtype=np.float64)
    B = np.full((16, 16), 0.25, dtype=np.float64)
    params = create_random_error_params(enabled=False)

    disturbed_A, disturbed_B = run_random_error_disturbance(A, params, B=B, seed=123, steps=5)

    assert np.allclose(disturbed_A, A)
    assert np.allclose(disturbed_B, B)


def test_apply_random_error_step_changes_fields_when_enabled():
    A = np.full((24, 24), 0.5, dtype=np.float64)
    B = np.full((24, 24), 0.25, dtype=np.float64)
    module = RandomErrorModule(A.shape, seed=42)
    params = create_random_error_params(
        enabled=True,
        strength=0.04,
        duration=12,
        frequency=0.05,
        probability=1.0,
        num_regions=2,
        region_size=8,
        jitter=0.10,
        micro_noise=0.03,
        alpha_var=0.20,
        beta=0.08,
        drift_x=0.8,
        drift_y=0.8,
        drift_frequency=0.002,
    )

    A_next, B_next, perturbation = apply_random_error_step(
        module,
        A,
        0.0,
        0,
        params,
        B,
    )

    assert perturbation.shape == A.shape
    assert not np.allclose(A_next, A)
    assert not np.allclose(B_next, B)
    assert np.all((A_next >= 0.0) & (A_next <= 5.0))
    assert np.all((B_next >= 0.0) & (B_next <= 5.0))


def test_random_error_kinds_produce_distinct_masks():
    spot_module = RandomErrorModule((32, 32), seed=7)
    labyrinth_module = RandomErrorModule((32, 32), seed=7)
    stripe_module = RandomErrorModule((32, 32), seed=7)

    spot_mask = spot_module.generate_perturbation_mask(
        num_regions=3,
        region_size=8,
        jitter=0.10,
        micro_noise=0.03,
        disturbance_kind="spots",
    )
    labyrinth_mask = labyrinth_module.generate_perturbation_mask(
        num_regions=3,
        region_size=8,
        jitter=0.10,
        micro_noise=0.03,
        disturbance_kind="labyrinth",
    )
    stripe_mask = stripe_module.generate_perturbation_mask(
        num_regions=3,
        region_size=8,
        jitter=0.10,
        micro_noise=0.03,
        disturbance_kind="stripe",
        local_y_segments=True,
    )

    assert spot_mask.shape == labyrinth_mask.shape == stripe_mask.shape == (32, 32)
    assert not np.allclose(spot_mask, labyrinth_mask)
    assert not np.allclose(spot_mask, stripe_mask)
    assert not np.allclose(labyrinth_mask, stripe_mask)


def test_labyrinth_random_error_prefers_edges_over_flat_regions():
    A = np.zeros((32, 32), dtype=np.float64)
    A[10:22, 10:22] = 1.0
    B = np.full((32, 32), 0.5, dtype=np.float64)
    module = RandomErrorModule(A.shape, seed=11)
    module.active_perturbations = [{
        "id": 0,
        "start_step": 0,
        "duration": 5,
        "strength": 0.08,
        "frequency": 0.05,
        "remaining_steps": 5,
        "alpha_var": 0.0,
        "disturbance_kind": "labyrinth",
        "local_y_segments": False,
        "drift_x": 0.0,
        "drift_y": 0.0,
        "drift_frequency": 0.0,
        "decaying": False,
    }]
    module.perturbation_masks = [np.ones_like(A)]
    module.perturbation_phases = [np.pi / 2.0]
    module._drift_phases = [(0.0, 0.0)]

    params = create_random_error_params(
        enabled=True,
        strength=0.08,
        duration=5,
        frequency=0.05,
        probability=0.0,
        num_regions=1,
        region_size=8,
        jitter=0.05,
        micro_noise=0.0,
        alpha_var=0.0,
        beta=0.0,
        drift_x=0.0,
        drift_y=0.0,
        drift_frequency=0.0,
        disturbance_kind="labyrinth",
    )

    _, _, perturbation = apply_random_error_step(
        module,
        A,
        0.0,
        0,
        params,
        B,
    )

    interior = np.abs(perturbation[13:19, 13:19]).mean()
    edge_band = np.abs(
        np.concatenate([
            perturbation[9:13, 10:22].ravel(),
            perturbation[19:23, 10:22].ravel(),
            perturbation[10:22, 9:13].ravel(),
            perturbation[10:22, 19:23].ravel(),
        ])
    ).mean()

    assert edge_band > interior
