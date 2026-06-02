"""Experiment service for metadata persistence and report generation."""

from __future__ import annotations

from core.models import EvaluationResult, ExperimentRecord, SimulationParams
from experiments.protocol import build_experiment_id, make_experiment_record
from experiments.repository import ExperimentRepository


class ExperimentService:
    """Persist experiment metadata alongside generated artifacts."""

    def __init__(self, repository: ExperimentRepository | None = None):
        self.repository = repository or ExperimentRepository()

    def make_record(
        self,
        params: SimulationParams,
        image_path: str,
        evaluation: EvaluationResult,
        color1: str,
        color2: str,
        heatmap_path: str | None = None,
        notes: str = "",
    ) -> ExperimentRecord:
        experiment_id = build_experiment_id(params, color1, color2)
        return make_experiment_record(
            params=params,
            experiment_id=experiment_id,
            image_path=image_path,
            evaluation=evaluation,
            heatmap_path=heatmap_path,
            notes=notes,
        )

    def persist(self, record: ExperimentRecord, evaluation: EvaluationResult) -> tuple[str, str]:
        record_path = self.repository.save_record(record)
        report_path = self.repository.save_report(record, evaluation)
        return str(record_path), str(report_path)

