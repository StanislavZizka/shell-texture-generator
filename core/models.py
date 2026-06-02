"""Shared dataclasses for simulation, evaluation, and experiment records."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

import numpy as np


@dataclass(slots=True)
class SimulationParams:
    """Parameters for a single activator-inhibitor simulation run."""

    name: str
    preset_name: str
    K: float
    t_max: float
    delta_t: float
    size: int = 512
    dx: float = 1.0
    random_seed: int = 42
    s: float = 1.0
    r_a: float = 1.0
    r_b: float = 2.0
    b_a: float = 0.1
    b_b: float = 0.1
    D_a: float = 0.01
    D_b: float = 0.5
    A0: float = 0.1
    B0: float = 1.0
    initial_noise_a_amplitude: float = 0.05
    initial_noise_b_amplitude: float = 0.01
    algorithm_version: str = "gm-activator-inhibitor-v1"
    extras: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class SimulationOutput:
    """Numerical output of a simulation step."""

    A: np.ndarray
    B: np.ndarray
    heatmap: np.ndarray
    steps: int
    snapshots: list[tuple[int, np.ndarray, np.ndarray]] = field(default_factory=list)


@dataclass(slots=True)
class EvaluationResult:
    """Computed metrics and a short textual summary."""

    metrics: dict[str, float] = field(default_factory=dict)
    summary: str = ""
    reference_name: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ExperimentRecord:
    """Metadata recorded for each experiment run."""

    experiment_id: str
    experiment_name: str
    created_at: str
    preset_name: str
    seed: int
    parameters: dict[str, Any]
    image_path: str
    heatmap_path: str | None = None
    metrics: dict[str, float] = field(default_factory=dict)
    algorithm_version: str = ""
    status: str = "completed"
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

