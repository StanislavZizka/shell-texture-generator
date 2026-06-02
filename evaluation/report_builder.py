"""Markdown report builder for experiment runs."""

from __future__ import annotations

from core.models import EvaluationResult, ExperimentRecord


def build_markdown_report(record: ExperimentRecord, evaluation: EvaluationResult) -> str:
    """Create a small reproducible report for an experiment run."""

    lines = [
        f"# Experiment {record.experiment_id}",
        "",
        f"- Name: {record.experiment_name}",
        f"- Preset: {record.preset_name}",
        f"- Seed: {record.seed}",
        f"- Algorithm: {record.algorithm_version}",
        f"- Status: {record.status}",
        f"- Image: {record.image_path}",
    ]

    if record.heatmap_path:
        lines.append(f"- Heatmap: {record.heatmap_path}")

    lines.extend(["", "## Metrics"])
    if evaluation.metrics:
        for key in sorted(evaluation.metrics):
            lines.append(f"- {key}: {evaluation.metrics[key]:.6f}")
    else:
        lines.append("- None")

    if evaluation.summary:
        lines.extend(["", "## Summary", evaluation.summary])

    return "\n".join(lines).strip() + "\n"

