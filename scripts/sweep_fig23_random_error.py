"""Sweep and score Figure 2.3 stripe random-error candidates."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import numpy as np
from PIL import Image

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config_23 import FIG23_PROGRESSION_LEVELS, FIG23_PROGRESSION_ORDER
from core.paths import OUTPUTS_DIR
from evaluation.metrics_spatial import dominant_orientation_score
from evaluation.metrics_stripes import (
    stripe_blob_penalty,
    stripe_continuity_score,
    stripe_spacing_variance,
    temporal_stability_score,
)
from routes.api import texture_service
from web.app_factory import create_app


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STAGES = list(FIG23_PROGRESSION_ORDER or FIG23_PROGRESSION_LEVELS.keys())


@dataclass(slots=True)
class Fig23StageCandidateReport:
    """Structured report for one Figure 2.3 candidate."""

    stage_key: str
    stage_label: str
    candidate_key: str
    image_path: str
    space_time_path: str
    continuity: float
    anisotropy: float
    spacing_variance: float
    blob_penalty: float
    temporal_stability: float
    score: float
    random_error_profile: dict

    def to_dict(self) -> dict:
        return asdict(self)


def _candidate_profiles(base_profile: dict) -> dict[str, dict]:
    """Return three stripe-consistent candidate profiles around a base profile."""

    profile = dict(base_profile)
    clean = dict(profile)
    clean["strength"] = max(0.004, float(profile.get("strength", 0.02)) * 0.88)
    clean["probability"] = max(0.002, float(profile.get("probability", 0.02)) * 0.86)
    clean["micro_noise"] = max(0.002, float(profile.get("micro_noise", 0.02)) * 0.72)
    clean["jitter"] = max(0.02, float(profile.get("jitter", 0.10)) * 0.94)
    clean["region_size"] = max(4, int(round(float(profile.get("region_size", 8)) * 1.18)))
    clean["duration"] = max(4, int(round(float(profile.get("duration", 12)) * 1.10)))
    clean["num_regions"] = max(1, int(profile.get("num_regions", 1)) - 1)
    clean["drift_frequency"] = float(profile.get("drift_frequency", 0.002)) * 0.94

    balanced = dict(profile)

    interrupted = dict(profile)
    interrupted["strength"] = max(0.004, float(profile.get("strength", 0.02)) * 1.08)
    interrupted["probability"] = max(0.002, float(profile.get("probability", 0.02)) * 1.12)
    interrupted["micro_noise"] = max(0.002, float(profile.get("micro_noise", 0.02)) * 0.84)
    interrupted["jitter"] = max(0.02, float(profile.get("jitter", 0.10)) * 1.03)
    interrupted["region_size"] = max(4, int(round(float(profile.get("region_size", 8)) * 0.92)))
    interrupted["duration"] = max(4, int(round(float(profile.get("duration", 12)) * 0.92)))
    interrupted["num_regions"] = int(profile.get("num_regions", 1)) + 1
    interrupted["drift_frequency"] = float(profile.get("drift_frequency", 0.002)) * 1.05

    return {
        "clean": clean,
        "balanced": balanced,
        "interrupted": interrupted,
    }


def _candidate_score(
    heatmap: np.ndarray,
    snapshots: list[np.ndarray],
) -> tuple[float, dict[str, float]]:
    """Score a candidate using stripe continuity, anisotropy and blob penalty."""

    continuity = stripe_continuity_score(heatmap)
    anisotropy = dominant_orientation_score(np.asarray(heatmap, dtype=np.float64))
    spacing_variance = stripe_spacing_variance(heatmap)
    blob = stripe_blob_penalty(heatmap)
    temporal = temporal_stability_score(snapshots[-2:]) if len(snapshots) >= 2 else 1.0
    regularity = 1.0 / (1.0 + max(0.0, float(spacing_variance)))
    score = (
        0.36 * continuity
        + 0.28 * anisotropy
        + 0.18 * temporal
        + 0.10 * regularity
        + 0.08 * (1.0 - blob)
    )
    metrics = {
        "continuity": float(continuity),
        "anisotropy": float(anisotropy),
        "spacing_variance": float(spacing_variance),
        "blob_penalty": float(blob),
        "temporal_stability": float(temporal),
        "regularity": float(regularity),
    }
    return float(score), metrics


def _extract_snapshots(mode_result) -> list[np.ndarray]:
    snapshots = []
    for _step, activator, _inhibitor in mode_result.snapshots:
        snapshots.append(np.asarray(activator, dtype=np.float64))
    return snapshots


def _image_path_from_url(image_url: str) -> Path:
    path = urlparse(image_url).path
    return REPO_ROOT / path.lstrip("/")


def run_stage_sweep(
    stages: list[str],
    *,
    size: int = 512,
    color1: str = "#f3e7c6",
    color2: str = "#101010",
    write_back: bool = False,
) -> tuple[list[Fig23StageCandidateReport], Path]:
    """Generate candidate profiles for Figure 2.3 stages and score them."""

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_dir = OUTPUTS_DIR / "fig23_random_error_sweep" / timestamp
    image_dir = output_dir / "images"
    image_dir.mkdir(parents=True, exist_ok=True)

    app = create_app()
    reports: list[Fig23StageCandidateReport] = []
    selected_profiles: dict[str, dict] = {}

    with app.test_client() as client:
        for stage_key in stages:
            stage_spec = dict(FIG23_PROGRESSION_LEVELS[stage_key])
            base_profile = dict(stage_spec.get("random_error_override", {}))
            candidates = _candidate_profiles(base_profile)
            best_report: Fig23StageCandidateReport | None = None
            best_score = -np.inf

            for candidate_key, candidate_profile in candidates.items():
                payload = {
                    "progression_level": stage_key,
                    "color1": color1,
                    "color2": color2,
                    "enable_random_error": True,
                    "re_strength": candidate_profile.get("strength"),
                    "re_duration": candidate_profile.get("duration"),
                    "re_frequency": candidate_profile.get("frequency"),
                    "re_probability": candidate_profile.get("probability"),
                    "re_num_regions": candidate_profile.get("num_regions"),
                    "re_region_size": candidate_profile.get("region_size"),
                    "re_jitter": candidate_profile.get("jitter"),
                    "re_micro_noise": candidate_profile.get("micro_noise"),
                    "re_alpha_var": candidate_profile.get("alpha_var"),
                    "re_beta": candidate_profile.get("beta"),
                    "re_drift_x": candidate_profile.get("drift_x"),
                    "re_drift_y": candidate_profile.get("drift_y"),
                    "re_drift_frequency": candidate_profile.get("drift_frequency"),
                }
                response = client.post("/api/generate-23", json=payload)
                if response.status_code != 200:
                    raise RuntimeError(f"Figure 2.3 sweep failed for {stage_key}/{candidate_key}: {response.get_data(as_text=True)}")

                data = response.get_json(force=True)
                image_path = _image_path_from_url(str(data["image_url"]))
                space_time_path = _image_path_from_url(str(data.get("space_time_url", ""))) if data.get("space_time_url") else Path("")

                copied_image = image_dir / f"{stage_key}_{candidate_key}_{image_path.name}"
                shutil.copy2(image_path, copied_image)
                copied_space_time = Path("")
                if space_time_path and space_time_path.exists():
                    copied_space_time = image_dir / f"{stage_key}_{candidate_key}_{space_time_path.name}"
                    shutil.copy2(space_time_path, copied_space_time)

                with Image.open(copied_image) as image:
                    heatmap = np.asarray(image.convert("L"), dtype=np.float64) / 255.0

                mode_result = getattr(texture_service, "last_mode_result", None)
                snapshots = []
                if mode_result is not None and getattr(mode_result, "snapshots", None):
                    snapshots = _extract_snapshots(mode_result)

                score, metrics = _candidate_score(heatmap, snapshots)
                report = Fig23StageCandidateReport(
                    stage_key=stage_key,
                    stage_label=str(data.get("label", stage_spec.get("label", stage_key))),
                    candidate_key=candidate_key,
                    image_path=str(copied_image),
                    space_time_path=str(copied_space_time) if copied_space_time else "",
                    continuity=metrics["continuity"],
                    anisotropy=metrics["anisotropy"],
                    spacing_variance=metrics["spacing_variance"],
                    blob_penalty=metrics["blob_penalty"],
                    temporal_stability=metrics["temporal_stability"],
                    score=score,
                    random_error_profile=dict(candidate_profile),
                )
                reports.append(report)
                if score > best_score:
                    best_score = score
                    best_report = report

            if best_report is not None:
                selected_profiles[stage_key] = dict(best_report.random_error_profile)

    if write_back:
        presets_path = Path(__file__).resolve().parents[1] / "configs" / "presets" / "figure_23.json"
        bundle = json.loads(presets_path.read_text(encoding="utf-8"))
        for stage_key, profile in selected_profiles.items():
            if stage_key in bundle.get("progression_levels", {}):
                bundle["progression_levels"][stage_key]["random_error_override"] = profile
        presets_path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    report_path = output_dir / "fig23_random_error_sweep.md"
    report_path.write_text(_render_markdown(reports, selected_profiles, output_dir), encoding="utf-8")

    summary_path = output_dir / "fig23_random_error_sweep.json"
    summary_path.write_text(
        json.dumps(
            {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "selected_profiles": selected_profiles,
                "candidates": [report.to_dict() for report in reports],
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return reports, output_dir


def _render_markdown(
    reports: list[Fig23StageCandidateReport],
    selected_profiles: dict[str, dict],
    output_dir: Path,
) -> str:
    by_stage: dict[str, list[Fig23StageCandidateReport]] = {}
    for report in reports:
        by_stage.setdefault(report.stage_key, []).append(report)

    lines = [
        "# Figure 2.3 Random Error Sweep",
        "",
        f"Output directory: `{output_dir}`",
        "",
    ]
    for stage_key in FIG23_PROGRESSION_ORDER:
        stage_reports = by_stage.get(stage_key, [])
        if not stage_reports:
            continue
        best = max(stage_reports, key=lambda item: item.score)
        lines.extend(
            [
                f"## {stage_key}",
                "",
                f"Recommended candidate: **{best.candidate_key}**",
                "",
                "| Candidate | Continuity | Anisotropy | Spacing Variance | Blob Penalty | Temporal | Score |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for item in stage_reports:
            lines.append(
                "| "
                + f"{item.candidate_key} | {item.continuity:.4f} | {item.anisotropy:.4f} | "
                + f"{item.spacing_variance:.5f} | {item.blob_penalty:.4f} | "
                + f"{item.temporal_stability:.4f} | {item.score:.4f} |"
            )
            lines.append(f"  - Image: `{Path(item.image_path).name}`")
        lines.append("")
        lines.append(f"Canonical profile stored for {stage_key}:")
        lines.append("```json")
        lines.append(json.dumps(selected_profiles.get(stage_key, {}), indent=2, ensure_ascii=False))
        lines.append("```")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stage",
        action="append",
        dest="stages",
        choices=DEFAULT_STAGES,
        help="Stage to sweep. Can be repeated. Defaults to all progression stages.",
    )
    parser.add_argument("--size", type=int, default=512, help="Texture size in pixels.")
    parser.add_argument("--write", action="store_true", help="Write the selected profiles back to figure_23.json.")
    args = parser.parse_args()

    stages = args.stages or list(DEFAULT_STAGES)
    reports, output_dir = run_stage_sweep(stages, size=args.size, write_back=bool(args.write))

    print(f"Figure 2.3 sweep written to: {output_dir}")
    for item in reports:
        print(
            f"{item.stage_key}/{item.candidate_key}: score={item.score:.4f}, "
            f"continuity={item.continuity:.4f}, anisotropy={item.anisotropy:.4f}, "
            f"spacing_var={item.spacing_variance:.5f}, blob={item.blob_penalty:.4f}, "
            f"temporal={item.temporal_stability:.4f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
