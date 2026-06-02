"""Mode registry for first-class texture generation families."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Literal


SolverName = Literal["activator_inhibitor", "labyrinth"]


@dataclass(frozen=True, slots=True)
class ModeDefinition:
    """Describe one first-class generation mode."""

    key: str
    label: str
    solver: SolverName
    preset_bundle: str
    default_preset: str
    stage_based: bool = False


@lru_cache(maxsize=1)
def load_mode_registry() -> dict[str, ModeDefinition]:
    """Return the built-in first-class mode registry."""

    return {
        "activator_inhibitor": ModeDefinition(
            key="activator_inhibitor",
            label="Activator-Inhibitor",
            solver="activator_inhibitor",
            preset_bundle="activator_inhibitor.json",
            default_preset="balanced",
        ),
        "stable_periodic_patterns": ModeDefinition(
            key="stable_periodic_patterns",
            label="Stable Periodic Patterns in Space",
            solver="activator_inhibitor",
            preset_bundle="figure_23.json",
            default_preset="stage_3",
            stage_based=True,
        ),
        "labyrinths": ModeDefinition(
            key="labyrinths",
            label="Labyrinths",
            solver="labyrinth",
            preset_bundle="figure_212.json",
            default_preset="stage_3",
            stage_based=True,
        ),
    }


def get_mode_definition(mode_key: str) -> ModeDefinition:
    """Return a mode definition or raise a KeyError."""

    registry = load_mode_registry()
    return registry[mode_key]

