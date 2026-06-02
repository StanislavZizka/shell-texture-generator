"""Validation helpers for simulation parameters and user-facing inputs."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .models import SimulationParams


class ValidationError(ValueError):
    """Raised when simulation parameters are structurally invalid."""


def validate_hex_color(color: str) -> bool:
    """Return True when color is a valid #RRGGBB or RRGGBB hex string."""

    if not isinstance(color, str):
        return False

    value = color.lstrip("#")
    if len(value) != 6:
        return False

    try:
        int(value, 16)
    except ValueError:
        return False

    return True


def validate_simulation_params(params: SimulationParams) -> SimulationParams:
    """Validate a simulation parameter dataclass and return it unchanged."""

    if params.size <= 0:
        raise ValidationError("size must be positive")
    if params.K <= 0:
        raise ValidationError("K must be positive")
    if params.t_max < 0:
        raise ValidationError("t_max must be non-negative")
    if params.delta_t <= 0:
        raise ValidationError("delta_t must be positive")
    if params.t_max > 0 and params.delta_t > params.t_max:
        raise ValidationError("delta_t cannot be greater than t_max")
    if params.dx <= 0:
        raise ValidationError("dx must be positive")
    if params.D_a < 0 or params.D_b < 0:
        raise ValidationError("diffusion coefficients must be non-negative")
    if not validate_hex_color(params.extras.get("color1", "#000000")):
        raise ValidationError("color1 must be a valid hex color")
    if not validate_hex_color(params.extras.get("color2", "#ffffff")):
        raise ValidationError("color2 must be a valid hex color")

    return params


def as_simulation_dict(params: SimulationParams) -> dict[str, Any]:
    """Return a plain dict representation of a SimulationParams instance."""

    return asdict(params)
