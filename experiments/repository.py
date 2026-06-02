"""Persistence helpers for experiment runs and reports."""

from __future__ import annotations

import json
from pathlib import Path

from core.models import EvaluationResult, ExperimentRecord
from core.paths import REPORTS_DIR, RUNS_DIR
from evaluation.report_builder import build_markdown_report


class ExperimentRepository:
    """Persist experiment metadata and generated reports to disk."""

    def __init__(self, runs_dir: Path | None = None, reports_dir: Path | None = None):
        self.runs_dir = runs_dir or RUNS_DIR
        self.reports_dir = reports_dir or REPORTS_DIR
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def save_record(self, record: ExperimentRecord) -> Path:
        path = self.runs_dir / f"{record.experiment_id}.json"
        with path.open("w", encoding="utf-8") as handle:
            json.dump(record.to_dict(), handle, indent=2, ensure_ascii=False)
        return path

    def save_report(self, record: ExperimentRecord, evaluation: EvaluationResult) -> Path:
        path = self.reports_dir / f"{record.experiment_id}.md"
        report = build_markdown_report(record, evaluation)
        path.write_text(report, encoding="utf-8")
        return path

