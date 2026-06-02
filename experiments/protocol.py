"""Experiment identity and record construction utilities."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from core.models import EvaluationResult, ExperimentRecord, SimulationParams


def _stable_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha1(encoded).hexdigest()[:12]


def build_experiment_name(params: SimulationParams) -> str:
    """Build a readable experiment name."""

    return f"{params.preset_name}:{params.name}"


def build_experiment_id(params: SimulationParams, color1: str, color2: str) -> str:
    """Build a reproducible identifier for a single run."""

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    slug = _stable_hash(
        {
            "name": params.name,
            "preset": params.preset_name,
            "seed": params.random_seed,
            "size": params.size,
            "K": params.K,
            "t_max": params.t_max,
            "delta_t": params.delta_t,
            "dx": params.dx,
            "s": params.s,
            "r_a": params.r_a,
            "r_b": params.r_b,
            "b_a": params.b_a,
            "b_b": params.b_b,
            "D_a": params.D_a,
            "D_b": params.D_b,
            "A0": params.A0,
            "B0": params.B0,
            "noise_a": params.initial_noise_a_amplitude,
            "noise_b": params.initial_noise_b_amplitude,
            "color1": color1,
            "color2": color2,
        }
    )
    return f"{timestamp}_{params.preset_name}_{params.random_seed}_{slug}"


def make_experiment_record(
    params: SimulationParams,
    experiment_id: str,
    image_path: str,
    evaluation: EvaluationResult,
    heatmap_path: str | None = None,
    notes: str = "",
) -> ExperimentRecord:
    """Build a record for persistence."""

    return ExperimentRecord(
        experiment_id=experiment_id,
        experiment_name=build_experiment_name(params),
        created_at=datetime.now(timezone.utc).isoformat(),
        preset_name=params.preset_name,
        seed=params.random_seed,
        parameters=params.to_dict(),
        image_path=image_path,
        heatmap_path=heatmap_path,
        metrics=dict(evaluation.metrics),
        algorithm_version=params.algorithm_version,
        status="completed",
        notes=notes,
    )
