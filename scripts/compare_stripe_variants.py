"""Generate and compare biologically plausible Figure 2.3 stripe variants."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.paths import OUTPUTS_DIR
from evaluation.metrics_stripes import (
    stripe_count_estimate,
    stripe_continuity_score,
    stripe_orientation_score,
    stripe_spacing_variance,
    temporal_stability_score,
)
from experiments.repository import ExperimentRepository
from services.experiment_service import ExperimentService
from services.export_service import ExportService
from services.mode_service import ModeService
from services.simulation_service import SimulationService


DEFAULT_VARIANTS = [
    "baseline",
    "mild_modulation",
    "moderate_modulation",
]


@dataclass(slots=True)
class StripeVariantReport:
    """Structured comparison output for one stripe variant."""

    variant_key: str
    label: str
    image_path: str
    record_path: str
    report_path: str
    continuity: float
    anisotropy: float
    stripe_count: int
    spacing_variance: float
    temporal_stability: float
    score: float

    def to_dict(self) -> dict:
        return asdict(self)


def _build_mode_service(output_dir: Path) -> ModeService:
    repository = ExperimentRepository(
        runs_dir=output_dir / "runs",
        reports_dir=output_dir / "reports",
    )
    return ModeService(
        simulation_service=SimulationService(),
        export_service=ExportService(output_dir=output_dir / "images"),
        experiment_service=ExperimentService(repository=repository),
    )


def _score_variant(continuity: float, anisotropy: float, spacing_variance: float, temporal_stability: float) -> float:
    """Prefer continuous, anisotropic stripes with slight irregularity."""

    target_spacing_variance = 0.015
    spacing_penalty = abs(spacing_variance - target_spacing_variance)
    return (
        0.40 * continuity
        + 0.30 * anisotropy
        + 0.20 * temporal_stability
        - 0.45 * spacing_penalty
    )


def _extract_snapshots(result) -> list[np.ndarray]:
    snapshots = []
    for _step, activator, _inhibitor in result.snapshots:
        snapshots.append(np.asarray(activator, dtype=np.float64))
    return snapshots


def run_comparison(variants: list[str], size: int = 512) -> tuple[list[StripeVariantReport], Path]:
    """Generate comparison images and return a structured report."""

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_dir = OUTPUTS_DIR / "stripe_variants" / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    mode_service = _build_mode_service(output_dir)
    reports: list[StripeVariantReport] = []

    for variant_key in variants:
        mode_result = mode_service.generate_stable_periodic_patterns(
            stripe_variant=variant_key,
            color1="#f3e7c6",
            color2="#101010",
            size=size,
            export_snapshots=True,
        )
        heatmap = np.asarray(mode_result.heatmap_data, dtype=np.float64)
        snapshots = _extract_snapshots(mode_result)
        continuity = stripe_continuity_score(heatmap)
        anisotropy = stripe_orientation_score(heatmap)
        stripe_count = stripe_count_estimate(heatmap)
        spacing_variance = stripe_spacing_variance(heatmap)
        temporal_stability = temporal_stability_score(snapshots[-2:]) if snapshots else 1.0
        score = _score_variant(continuity, anisotropy, spacing_variance, temporal_stability)

        reports.append(
            StripeVariantReport(
                variant_key=variant_key,
                label=mode_result.stage_label or variant_key,
                image_path=mode_result.image_path,
                record_path=mode_result.record_path,
                report_path=mode_result.report_path,
                continuity=continuity,
                anisotropy=anisotropy,
                stripe_count=stripe_count,
                spacing_variance=spacing_variance,
                temporal_stability=temporal_stability,
                score=score,
            )
        )

    report_path = output_dir / "stripe_variant_comparison.md"
    report_path.write_text(_render_markdown(reports, output_dir), encoding="utf-8")
    summary_path = output_dir / "stripe_variant_comparison.json"
    summary_path.write_text(
        json.dumps(
            {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "variants": [item.to_dict() for item in reports],
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return reports, output_dir


def _render_markdown(reports: list[StripeVariantReport], output_dir: Path) -> str:
    best = max(reports, key=lambda item: item.score)
    lines = [
        "# Figure 2.3 Stripe Variant Comparison",
        "",
        f"Output directory: `{output_dir}`",
        "",
        "| Variant | Continuity | Anisotropy | Stripe Count | Spacing Variance | Temporal Stability | Score |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in reports:
        rel_image = Path(item.image_path).name
        lines.append(
            "| "
            + f"{item.variant_key} | {item.continuity:.4f} | {item.anisotropy:.4f} | "
            + f"{item.stripe_count} | {item.spacing_variance:.5f} | {item.temporal_stability:.4f} | {item.score:.4f} |"
        )
        lines.append(f"  - Image: `{rel_image}`")
    lines.extend(
        [
            "",
            f"Recommended variant: **{best.variant_key}**",
            "",
            "Rationale:",
            "- Baseline keeps the stripe regime as a reference point.",
            "- Mild modulation is usually the sweet spot when we want stripes that stay long and vertical, but stop looking mechanically periodic.",
            "- Moderate modulation is useful as a stress test, but it can start to trade regularity for irregularity too aggressively.",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--variant",
        action="append",
        dest="variants",
        choices=DEFAULT_VARIANTS,
        help="Stripe variant to include. Can be repeated. Defaults to all three.",
    )
    parser.add_argument("--size", type=int, default=512, help="Texture size in pixels.")
    args = parser.parse_args()

    variants = args.variants or list(DEFAULT_VARIANTS)
    reports, output_dir = run_comparison(variants, size=args.size)

    print(f"Stripe comparison written to: {output_dir}")
    for item in reports:
        print(
            f"{item.variant_key}: score={item.score:.4f}, "
            f"continuity={item.continuity:.4f}, anisotropy={item.anisotropy:.4f}, "
            f"spacing_var={item.spacing_variance:.5f}, temporal={item.temporal_stability:.4f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
