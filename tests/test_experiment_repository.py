from core.models import EvaluationResult, ExperimentRecord
from experiments.repository import ExperimentRepository


def test_experiment_repository_saves_record_and_report(tmp_path):
    repository = ExperimentRepository(runs_dir=tmp_path / "runs", reports_dir=tmp_path / "reports")
    record = ExperimentRecord(
        experiment_id="20260326T120000Z_balanced_123_abcd",
        experiment_name="balanced:Activator-Inhibitor",
        created_at="2026-03-26T12:00:00+00:00",
        preset_name="balanced",
        seed=123,
        parameters={"K": 0.5},
        image_path=str(tmp_path / "image.png"),
        metrics={"contrast": 0.42},
        algorithm_version="gm-activator-inhibitor-v1",
    )
    evaluation = EvaluationResult(metrics={"contrast": 0.42}, summary="ok")

    record_path = repository.save_record(record)
    report_path = repository.save_report(record, evaluation)

    assert record_path.exists()
    assert report_path.exists()
    assert "balanced" in record_path.read_text(encoding="utf-8")
    assert "contrast" in report_path.read_text(encoding="utf-8")

