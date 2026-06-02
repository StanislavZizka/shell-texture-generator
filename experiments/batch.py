"""Batch orchestration for reproducible first-class mode runs."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from PIL import Image

from config import DEFAULT_TEXTURE_SIZE
from core.modes import get_mode_definition
from core.paths import OUTPUTS_DIR
from evaluation.compare_reference import compare_arrays
from experiments.repository import ExperimentRepository
from services.experiment_service import ExperimentService
from services.export_service import ExportService
from services.mode_service import ModeService
from services.simulation_service import SimulationService


ACTIVATOR_INHIBITOR_COLORS = ("#0000ff", "#ff0000")
SOFT_NEUTRAL_COLORS = ("#f3e7c6", "#101010")


@dataclass(slots=True)
class BatchTarget:
    """A single batch run specification."""

    mode_key: str
    kwargs: dict[str, Any]
    label: str = ""
    reference_image_path: str | None = None
    reference_metrics: dict[str, float] = field(default_factory=dict)


@dataclass(slots=True)
class BatchRunResult:
    """Result of one batch run."""

    mode_key: str
    label: str
    preset_key: str
    experiment_id: str
    image_path: str
    record_path: str
    report_path: str
    metrics: dict[str, float]
    stage_label: str = ""
    reference_image_path: str | None = None
    image_comparison: dict[str, float] = field(default_factory=dict)
    metric_deltas: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_default_reproducibility_targets(size: int = DEFAULT_TEXTURE_SIZE) -> list[BatchTarget]:
    """Return the default three-mode batch suite."""

    return [
        BatchTarget(
            mode_key="activator_inhibitor",
            label="Activator-Inhibitor",
            kwargs={
                "K": 1.0,
                "t_max": 400.0,
                "delta_t": 0.1,
                "color1": ACTIVATOR_INHIBITOR_COLORS[0],
                "color2": ACTIVATOR_INHIBITOR_COLORS[1],
                "size": size,
                "preset_key": "balanced",
                "export_snapshots": False,
            },
        ),
        BatchTarget(
            mode_key="stable_periodic_patterns",
            label="Stable Periodic Patterns in Space",
            kwargs={
                "stage": 3,
                "color1": SOFT_NEUTRAL_COLORS[0],
                "color2": SOFT_NEUTRAL_COLORS[1],
                "size": size,
                "export_snapshots": False,
            },
        ),
        BatchTarget(
            mode_key="labyrinths",
            label="Labyrinths",
            kwargs={
                "stage": 3,
                "color1": SOFT_NEUTRAL_COLORS[0],
                "color2": SOFT_NEUTRAL_COLORS[1],
                "size": size,
                "export_snapshots": False,
            },
        ),
    ]


class BatchRunner:
    """Run a reproducible sweep of first-class modes."""

    def __init__(
        self,
        mode_service: ModeService | None = None,
        output_dir: Path | None = None,
    ) -> None:
        self.output_dir = output_dir or (OUTPUTS_DIR / "batches")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        if mode_service is None:
            repository = ExperimentRepository(
                runs_dir=self.output_dir / "runs",
                reports_dir=self.output_dir / "reports",
            )
            mode_service = ModeService(
                simulation_service=SimulationService(),
                export_service=ExportService(output_dir=self.output_dir / "images"),
                experiment_service=ExperimentService(repository=repository),
            )
        self.mode_service = mode_service

    def run(self, targets: Iterable[BatchTarget]) -> list[BatchRunResult]:
        """Execute the supplied batch targets."""

        results: list[BatchRunResult] = []
        for target in targets:
            mode_definition = get_mode_definition(target.mode_key)
            mode_result = self.mode_service.generate_mode(target.mode_key, **target.kwargs)
            comparison = self._compare_metrics(
                mode_result.metrics,
                target.reference_metrics,
            )
            image_comparison = self._compare_reference_image(
                mode_result.image_path,
                target.reference_image_path,
            )
            results.append(
                BatchRunResult(
                    mode_key=mode_result.mode_key,
                    label=target.label or mode_definition.label,
                    preset_key=mode_result.preset_key,
                    experiment_id=mode_result.record.experiment_id if mode_result.record else "",
                    image_path=mode_result.image_path,
                    record_path=mode_result.record_path,
                    report_path=mode_result.report_path,
                    metrics=dict(mode_result.evaluation.metrics),
                    stage_label=mode_result.stage_label,
                    reference_image_path=target.reference_image_path,
                    image_comparison=image_comparison,
                    metric_deltas=comparison,
                )
            )
        return results

    def write_summary(
        self,
        results: list[BatchRunResult],
        filename: str | None = None,
    ) -> Path:
        """Write a JSON summary for a completed batch."""

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output_name = filename or f"batch_summary_{timestamp}.json"
        output_path = self.output_dir / output_name
        payload = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "results": [result.to_dict() for result in results],
        }
        output_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return output_path

    def _compare_metrics(
        self,
        metrics: dict[str, float],
        reference_metrics: dict[str, float],
    ) -> dict[str, float]:
        if not reference_metrics:
            return {}

        deltas: dict[str, float] = {}
        for key, expected in reference_metrics.items():
            if key in metrics:
                deltas[key] = float(metrics[key] - expected)
        return deltas

    def _compare_reference_image(
        self,
        candidate_image_path: str,
        reference_image_path: str | None,
    ) -> dict[str, float]:
        if not reference_image_path:
            return {}

        candidate = self._load_grayscale_image(candidate_image_path)
        reference = self._load_grayscale_image(reference_image_path)
        if candidate.shape != reference.shape:
            raise ValueError(
                "Reference image shape does not match candidate image "
                f"({candidate.shape} != {reference.shape})"
            )
        return compare_arrays(candidate, reference)

    def _load_grayscale_image(self, path: str) -> np.ndarray:
        with Image.open(path) as img:
            return np.asarray(img.convert("L"), dtype=np.float64) / 255.0
