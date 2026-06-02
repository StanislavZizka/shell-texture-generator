from __future__ import annotations

import json
from pathlib import Path

from experiments.batch import BatchRunner, build_default_reproducibility_targets
from experiments.repository import ExperimentRepository
from services.experiment_service import ExperimentService
from services.export_service import ExportService
from services.mode_service import ModeService
from services.simulation_service import SimulationService


def test_batch_runner_matches_reference_snapshot(tmp_path):
    repository = ExperimentRepository(
        runs_dir=tmp_path / "runs",
        reports_dir=tmp_path / "reports",
    )
    mode_service = ModeService(
        simulation_service=SimulationService(),
        export_service=ExportService(output_dir=tmp_path / "images"),
        experiment_service=ExperimentService(repository=repository),
    )
    runner = BatchRunner(mode_service=mode_service, output_dir=tmp_path / "batch")

    targets = build_default_reproducibility_targets(size=32)
    results = runner.run(targets)
    summary_path = runner.write_summary(results, filename="summary.json")

    assert summary_path.exists()
    assert len(results) == 3

    snapshot_path = (
        Path(__file__).resolve().parents[1]
        / "experiments"
        / "references"
        / "three_core_modes_smoke.json"
    )
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    tolerance = float(snapshot["metric_tolerance"])
    expected_cases = {case["mode_key"]: case for case in snapshot["cases"]}
    actual_cases = {result.mode_key: result for result in results}

    assert set(actual_cases) == set(expected_cases)

    for mode_key, expected in expected_cases.items():
        result = actual_cases[mode_key]
        assert result.preset_key == expected["preset_key"]
        assert result.label == expected["label"]
        assert result.stage_label == expected["stage_label"]

        for metric_name, expected_value in expected["metrics"].items():
            assert metric_name in result.metrics
            assert abs(result.metrics[metric_name] - expected_value) <= tolerance
