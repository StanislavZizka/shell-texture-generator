"""Shared result objects for mode-based generation."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from core.models import EvaluationResult, ExperimentRecord


@dataclass(slots=True)
class ModeGenerationResult:
    """Return value for a mode-dispatched generation run."""

    mode_key: str
    preset_key: str
    image_path: str
    raw_image_path: str = ""
    space_time_path: str = ""
    heatmap_data: list[list[float]] | None = None
    evaluation: EvaluationResult = field(default_factory=EvaluationResult)
    record: ExperimentRecord | None = None
    record_path: str = ""
    report_path: str = ""
    stage_label: str = ""
    snapshots: list[tuple[int, np.ndarray, np.ndarray]] = field(default_factory=list)

    @property
    def metrics(self) -> dict[str, float]:
        """Shortcut access to the computed metrics."""

        return self.evaluation.metrics
