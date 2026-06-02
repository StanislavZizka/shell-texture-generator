"""Parameter builders extracted from the texture generator service."""

from __future__ import annotations

from config import SIMULATION_PARAMS
from core.models import SimulationParams


def build_activator_inhibitor_params(
    K: float,
    t_max: float,
    delta_t: float,
    size: int,
    params_override: dict | None,
    preset_name: str,
    color1: str,
    color2: str,
) -> SimulationParams:
    """Merge legacy config values into the activator-inhibitor simulation dataclass."""

    merged = dict(SIMULATION_PARAMS)
    if params_override:
        merged.update(params_override)

    return SimulationParams(
        name="Activator-Inhibitor",
        preset_name=preset_name or str(merged.get("preset_name", "custom")),
        K=float(K),
        t_max=float(t_max),
        delta_t=float(delta_t),
        size=int(size),
        dx=float(merged.get("dx", 1.0)),
        random_seed=int(merged.get("random_seed", 42)),
        s=float(merged.get("s", 1.0)),
        r_a=float(merged.get("r_a", 1.0)),
        r_b=float(merged.get("r_b", 2.0)),
        b_a=float(merged.get("b_a", 0.1)),
        b_b=float(merged.get("b_b", 0.1)),
        D_a=float(merged.get("D_a", 0.01)),
        D_b=float(merged.get("D_b", 0.5)),
        A0=float(merged.get("A0", 0.1)),
        B0=float(merged.get("B0", 1.0)),
        initial_noise_a_amplitude=float(merged.get("initial_noise_a_amplitude", 0.05)),
        initial_noise_b_amplitude=float(merged.get("initial_noise_b_amplitude", 0.01)),
        extras={
            "color1": color1,
            "color2": color2,
            "params_override": dict(params_override or {}),
        },
    )
