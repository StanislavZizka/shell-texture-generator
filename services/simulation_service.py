"""Simulation service that wraps the numerical core."""

from __future__ import annotations

from core.models import SimulationOutput, SimulationParams
from simulation.activator_inhibitor import simulate_activator_inhibitor
from simulation.labyrinth import simulate_labyrinth


class SimulationService:
    """Thin service around the simulation core."""

    def run_activator_inhibitor(
        self,
        params: SimulationParams,
        export_snapshots: bool = False,
        random_error_params: dict | None = None,
    ) -> SimulationOutput:
        return simulate_activator_inhibitor(
            params,
            export_snapshots=export_snapshots,
            random_error_params=random_error_params,
        )

    def run_labyrinth(
        self,
        params: SimulationParams,
        random_error_params: dict | None = None,
        export_snapshots: bool = False,
    ) -> SimulationOutput:
        return simulate_labyrinth(
            params,
            random_error_params=random_error_params,
            export_snapshots=export_snapshots,
        )
