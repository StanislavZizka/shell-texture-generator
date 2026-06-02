"""Activator-inhibitor reaction diffusion simulator."""

from __future__ import annotations

import numpy as np

from core.models import SimulationOutput
from core.models import SimulationParams
from core.validation import validate_simulation_params
from rendering.colormaps import normalize_field
from simulation.integrators import explicit_euler_step
from simulation.laplacian import periodic_laplacian
from simulation.stripe_modulation import build_stripe_modulation_fields
from services.random_error_module import (
    RandomErrorModule,
    apply_random_error_step,
    create_random_error_params,
)


def simulate_activator_inhibitor(
    params: SimulationParams,
    export_snapshots: bool = False,
    random_error_params: dict | None = None,
) -> SimulationOutput:
    """Run the activator-inhibitor model using a deterministic random seed."""

    validate_simulation_params(params)

    rng = np.random.RandomState(params.random_seed)
    size = params.size
    steps = int(params.t_max / params.delta_t)

    A = np.full((size, size), params.A0, dtype=np.float64)
    B = np.full((size, size), params.B0, dtype=np.float64)

    stripe_modulation_cfg = {}
    if params.extras.get("mode_key") == "stable_periodic_patterns":
        stripe_modulation_cfg = dict(params.extras.get("spatial_modulation", {}))

    modulation_fields = None
    if stripe_modulation_cfg.get("enabled"):
        modulation_fields = build_stripe_modulation_fields(
            (size, size),
            seed=params.random_seed,
            config=stripe_modulation_cfg,
        )

    initial_noise_a_amplitude = float(params.initial_noise_a_amplitude)
    initial_noise_b_amplitude = float(params.initial_noise_b_amplitude)
    if modulation_fields is not None:
        initial_noise_a_amplitude *= 1.0 + float(stripe_modulation_cfg.get("eps_initial_a", 0.0)) * modulation_fields.initial_a_field
        initial_noise_b_amplitude *= 1.0 + float(stripe_modulation_cfg.get("eps_initial_b", 0.0)) * modulation_fields.initial_b_field

    A += (rng.rand(size, size) - 0.5) * initial_noise_a_amplitude
    B += (rng.rand(size, size) - 0.5) * initial_noise_b_amplitude

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
    snapshot_count = int(params.extras.get("snapshot_count", 0)) if export_snapshots else 0
    if snapshot_count > 1:
        snapshot_steps = {
            int(round(value))
            for value in np.linspace(0, steps, snapshot_count)
        }
    elif export_snapshots:
        snapshot_steps = {
            int(steps * frac)
            for frac in (0.25, 0.5, 0.75, 1.0)
            if int(steps * frac) >= 0
        }
    else:
        snapshot_steps = set()

    D_a = params.D_a * params.K
    D_b = params.D_b * params.K
    s_field = None
    D_a_field = None
    if modulation_fields is not None:
        eps_s = float(stripe_modulation_cfg.get("eps_s", 0.0))
        eps_Da = float(stripe_modulation_cfg.get("eps_Da", 0.0))
        s_field = params.s * (1.0 + eps_s * modulation_fields.s_field)
        D_a_field = params.D_a * params.K * (1.0 + eps_Da * modulation_fields.da_field)
        np.clip(s_field, params.s * 0.85, params.s * 1.15, out=s_field)
        np.clip(
            D_a_field,
            params.D_a * params.K * 0.85,
            params.D_a * params.K * 1.15,
            out=D_a_field,
        )

    if export_snapshots and 0 in snapshot_steps:
        snapshots.append((0, A.copy(), B.copy()))

    for step in range(steps):
        lap_A = periodic_laplacian(A, params.dx)
        lap_B = periodic_laplacian(B, params.dx)
        B_safe = np.maximum(B, 1e-10)

        local_s = s_field if s_field is not None else params.s
        local_D_a = D_a_field if D_a_field is not None else D_a
        dA_dt = (
            local_D_a * lap_A
            + local_s * (A ** 2 / B_safe)
            - params.r_a * A
            + (local_s * params.b_a)
        )
        dB_dt = D_b * lap_B + local_s * (A ** 2) - params.r_b * B + params.b_b

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

        current_step = step + 1
        if export_snapshots and current_step in snapshot_steps:
            snapshots.append((current_step, A.copy(), B.copy()))

    heatmap = normalize_field(A)
    return SimulationOutput(A=A, B=B, heatmap=heatmap, steps=steps, snapshots=snapshots)
