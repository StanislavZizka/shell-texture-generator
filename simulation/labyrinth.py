"""Labyrinth mode simulation core."""

from __future__ import annotations

import numpy as np

from core.models import SimulationOutput, SimulationParams
from core.validation import validate_simulation_params
from rendering.colormaps import normalize_field
from simulation.integrators import explicit_euler_step
from simulation.laplacian import periodic_laplacian
from services.random_error_module import (
    RandomErrorModule,
    apply_random_error_step,
    create_random_error_params,
)


def simulate_labyrinth(
    params: SimulationParams,
    random_error_params: dict | None = None,
    export_snapshots: bool = False,
) -> SimulationOutput:
    """Run the labyrinth variant of the activator-inhibitor model."""

    validate_simulation_params(params)

    size = params.size
    steps = int(params.t_max / params.delta_t)
    rng = np.random.RandomState(params.random_seed)

    A = np.full((size, size), params.A0, dtype=np.float64)
    B = np.full((size, size), params.B0, dtype=np.float64)
    A += (rng.rand(size, size) - 0.5) * params.initial_noise_a_amplitude
    B += (rng.rand(size, size) - 0.5) * params.initial_noise_b_amplitude

    re_params = create_random_error_params(enabled=False)
    if random_error_params:
        re_params.update(random_error_params)
    random_error_enabled = bool(re_params.get("enabled", False))
    re_module = (
        RandomErrorModule(size=A.shape, seed=params.random_seed)
        if random_error_enabled
        else None
    )

    snapshots: list[tuple[int, np.ndarray, np.ndarray]] = []
    snapshot_steps = {
        int(steps * frac)
        for frac in (0.25, 0.5, 0.75, 1.0)
        if int(steps * frac) > 0
    } if export_snapshots else set()

    D_a_eff = params.D_a * params.K
    D_b_eff = params.D_b * params.K

    for step in range(steps):
        lap_A = periodic_laplacian(A, params.dx)
        lap_B = periodic_laplacian(B, params.dx)
        B_safe = np.maximum(B, 1e-10)

        dA_dt = (
            params.s * (A ** 2 / B_safe + params.b_a)
            - params.r_a * A
            + D_a_eff * lap_A
        )
        dB_dt = (
            params.s * (A ** 2)
            - params.r_b * B
            + params.b_b
            + D_b_eff * lap_B
        )

        A = np.clip(explicit_euler_step(A, dA_dt, params.delta_t), 0.0, 5.0)
        B = np.clip(explicit_euler_step(B, dB_dt, params.delta_t), 0.0, 5.0)

        if random_error_enabled and re_module is not None:
            t = step * params.delta_t
            A, B, _ = apply_random_error_step(
                re_module,
                A,
                t,
                step,
                re_params,
                B,
            )

        if export_snapshots and step in snapshot_steps:
            snapshots.append((step, A.copy(), B.copy()))

    return SimulationOutput(
        A=A,
        B=B,
        heatmap=normalize_field(A),
        steps=steps,
        snapshots=snapshots,
    )
