"""Mode dispatch and shared generation orchestration."""

from __future__ import annotations

from typing import Any

import numpy as np

from config import DEFAULT_TEXTURE_SIZE
from core.models import EvaluationResult, SimulationParams
from core.modes import get_mode_definition
from core.modes_result import ModeGenerationResult
from core.presets import (
    load_activator_inhibitor_presets,
    load_figure_212_presets,
    load_figure_23_presets,
)
from evaluation.metrics_basic import active_area_ratio, image_contrast, image_mean, image_std
from evaluation.metrics_spatial import dominant_orientation_score
from experiments.protocol import build_experiment_id
from rendering.texture_export import save_texture_image
from rendering.stripe_export import (
    save_stripe_raw_image,
    save_stripe_space_time_image,
    save_stripe_texture_image,
)
from services.experiment_service import ExperimentService
from services.export_service import ExportService
from services.simulation_service import SimulationService


class ModeService:
    """Dispatch first-class modes onto the shared simulation and export core."""

    def __init__(
        self,
        simulation_service: SimulationService | None = None,
        export_service: ExportService | None = None,
        experiment_service: ExperimentService | None = None,
    ) -> None:
        self.simulation_service = simulation_service or SimulationService()
        self.export_service = export_service or ExportService()
        self.experiment_service = experiment_service or ExperimentService()

    def _metrics(self, heatmap: np.ndarray) -> dict[str, float]:
        return {
            "mean": image_mean(heatmap),
            "std": image_std(heatmap),
            "contrast": image_contrast(heatmap),
            "active_area_ratio": active_area_ratio(heatmap),
            "dominant_orientation_score": dominant_orientation_score(heatmap),
        }

    def generate_mode(self, mode_key: str, **kwargs: Any) -> ModeGenerationResult:
        """Generate a mode by registry key."""

        mode_definition = get_mode_definition(mode_key)
        if mode_definition.key == "activator_inhibitor":
            return self.generate_activator_inhibitor(**kwargs)
        if mode_definition.key == "stable_periodic_patterns":
            return self.generate_stable_periodic_patterns(**kwargs)
        if mode_definition.key == "labyrinths":
            return self.generate_labyrinths(**kwargs)
        raise KeyError(f"Unsupported mode: {mode_key}")

    def _finalize(
        self,
        mode_key: str,
        preset_key: str,
        params: SimulationParams,
        image_path: str,
        heatmap_data: list[list[float]],
        stage_label: str = "",
        notes: str = "",
    ) -> ModeGenerationResult:
        evaluation = EvaluationResult(
            metrics=self._metrics(np.asarray(heatmap_data, dtype=np.float64)),
            summary=(
                f"Completed {mode_key} using preset '{preset_key}'"
                + (f" ({stage_label})" if stage_label else "")
                + "."
            ),
        )
        record = self.experiment_service.make_record(
            params=params,
            image_path=image_path,
            evaluation=evaluation,
            color1=str(params.extras.get("color1", "#000000")),
            color2=str(params.extras.get("color2", "#ffffff")),
            notes=notes,
        )
        record_path, report_path = self.experiment_service.persist(record, evaluation)
        return ModeGenerationResult(
            mode_key=mode_key,
            preset_key=preset_key,
            image_path=image_path,
            heatmap_data=heatmap_data,
            evaluation=evaluation,
            record=record,
            record_path=record_path,
            report_path=report_path,
            stage_label=stage_label,
        )

    @staticmethod
    def _select_progression_texture_field(
        output: Any,
        progress_percent: int | None,
    ) -> np.ndarray:
        """Pick a progression snapshot for Figure 2.3 texture export.

        The stripe progression is visually clearer when the displayed square
        texture comes from the corresponding time window instead of always
        using the final heatmap, which tends to converge toward a similar
        late-stage stripe field for nearby presets.
        """

        snapshots = list(getattr(output, "snapshots", None) or [])
        if not snapshots:
            return np.asarray(getattr(output, "heatmap"), dtype=np.float64)

        if progress_percent is None:
            target_index = len(snapshots) - 1
        else:
            fraction = max(0.0, min(1.0, float(progress_percent) / 100.0))
            target_index = int(round(fraction * (len(snapshots) - 1)))

        target_index = max(0, min(target_index, len(snapshots) - 1))
        _step, activator, _inhibitor = snapshots[target_index]
        return np.asarray(activator, dtype=np.float64)

    @staticmethod
    def _fig23_texture_profile(progress_percent: int | None) -> dict[str, float]:
        """Return a stage-dependent export profile for Figure 2.3."""

        if progress_percent is None:
            return {}

        level_profiles = {
            10: {
                "texture_mix": 0.82,
                "phase_strength": 0.36,
                "amplitude_floor": 0.61,
                "amplitude_span": 0.31,
                "gamma": 0.90,
            },
            30: {
                "texture_mix": 0.71,
                "phase_strength": 0.31,
                "amplitude_floor": 0.64,
                "amplitude_span": 0.28,
                "gamma": 0.92,
            },
            60: {
                "texture_mix": 0.60,
                "phase_strength": 0.26,
                "amplitude_floor": 0.68,
                "amplitude_span": 0.24,
                "gamma": 0.95,
            },
            90: {
                "texture_mix": 0.48,
                "phase_strength": 0.21,
                "amplitude_floor": 0.71,
                "amplitude_span": 0.20,
                "gamma": 0.98,
            },
        }
        return dict(level_profiles.get(int(progress_percent), {}))

    def generate_activator_inhibitor(
        self,
        *,
        K: float,
        t_max: float,
        delta_t: float,
        color1: str,
        color2: str,
        size: int = DEFAULT_TEXTURE_SIZE,
        preset_key: str = "balanced",
        params_override: dict | None = None,
        export_snapshots: bool = False,
    ) -> ModeGenerationResult:
        bundle = load_activator_inhibitor_presets()
        preset_params = dict(bundle.get(preset_key, {}))
        if params_override:
            preset_params.update(params_override)

        params = SimulationParams(
            name="activator_inhibitor",
            preset_name=preset_key,
            K=float(K),
            t_max=float(t_max),
            delta_t=float(delta_t),
            size=int(size),
            dx=float(preset_params.get("dx", 1.0)),
            random_seed=int(preset_params.get("random_seed", 42)),
            s=float(preset_params.get("s", 1.0)),
            r_a=float(preset_params.get("r_a", 1.0)),
            r_b=float(preset_params.get("r_b", 2.0)),
            b_a=float(preset_params.get("b_a", 0.1)),
            b_b=float(preset_params.get("b_b", 0.1)),
            D_a=float(preset_params.get("D_a", 0.01)),
            D_b=float(preset_params.get("D_b", 0.5)),
            A0=float(preset_params.get("A0", 0.1)),
            B0=float(preset_params.get("B0", 1.0)),
            initial_noise_a_amplitude=float(
                preset_params.get("initial_noise_a_amplitude", 0.05)
            ),
            initial_noise_b_amplitude=float(
                preset_params.get("initial_noise_b_amplitude", 0.01)
            ),
            extras={
                "color1": color1,
                "color2": color2,
                "mode_key": "activator_inhibitor",
                "params_override": dict(params_override or {}),
            },
        )
        output = self.simulation_service.run_activator_inhibitor(
            params,
            export_snapshots=export_snapshots,
        )
        experiment_id = build_experiment_id(params, color1, color2)
        image_path = save_texture_image(
            output.A,
            output.B,
            color1,
            color2,
            self.export_service.output_dir / f"{experiment_id}.png",
        )
        return self._finalize(
            "activator_inhibitor",
            preset_key,
            params,
            image_path,
            output.heatmap.tolist(),
            notes="Generated through mode dispatch",
        )

    def generate_stable_periodic_patterns(
        self,
        *,
        stage: int | None = None,
        development_percent: int | None = None,
        stripe_variant: str | None = None,
        params_override: dict | None = None,
        spatial_modulation_override: dict | None = None,
        random_error_params: dict | None = None,
        color1: str,
        color2: str,
        size: int = DEFAULT_TEXTURE_SIZE,
        export_snapshots: bool = False,
    ) -> ModeGenerationResult:
        bundle = load_figure_23_presets()
        if stripe_variant is not None:
            variant_key = str(stripe_variant).strip().lower()
            variant_spec = dict(bundle.get("stripe_variants", {}).get(variant_key, {}))
            if not variant_spec:
                raise KeyError(f"Unknown stripe variant: {stripe_variant}")
            base_stage = str(variant_spec.get("base_stage", "stage_3"))
            stage_spec = dict(bundle["stages"][base_stage])
            merged_params_override = dict(stage_spec.get("params_override", {}))
            merged_params_override.update(dict(variant_spec.get("params_override", {})))
            if params_override:
                merged_params_override.update(dict(params_override))
            spatial_modulation = dict(variant_spec.get("spatial_modulation", {}))
            if spatial_modulation_override:
                spatial_modulation.update(dict(spatial_modulation_override))
            preset_name = variant_key
            stage_label = str(variant_spec.get("label", variant_key))
            t_max = float(variant_spec.get("t_max", 110.0))
            notes = str(variant_spec.get("reference_report", f"Stripe variant '{variant_key}'"))
            export_snapshots = True
            snapshot_count = int(variant_spec.get("snapshot_count", 96))
        elif development_percent is not None:
            development_key = f"dev_{int(development_percent)}"
            development_spec = dict(bundle["development_presets"][development_key])
            merged_params_override = dict(development_spec.get("params_override", {}))
            if params_override:
                merged_params_override.update(dict(params_override))
            preset_name = development_key
            stage_label = str(development_spec.get("label", development_key))
            t_max = float(development_spec.get("t_max", 110.0))
            notes = f"Generated through mode dispatch at {int(development_percent)}% development"
            spatial_modulation = dict(development_spec.get("spatial_modulation", {}))
            if spatial_modulation_override:
                spatial_modulation.update(dict(spatial_modulation_override))
            snapshot_count = int(development_spec.get("snapshot_count", 72))
        else:
            if stage is None:
                stage = int(bundle["default_stage"].split("_")[-1])
            stage_key = f"stage_{int(stage)}"
            stage_spec = dict(bundle["stages"][stage_key])
            merged_params_override = dict(stage_spec.get("params_override", {}))
            if params_override:
                merged_params_override.update(dict(params_override))
            preset_name = stage_key
            stage_label = str(stage_spec.get("label", stage_key))
            t_max = 110.0
            notes = "Generated through mode dispatch"
            spatial_modulation = dict(stage_spec.get("spatial_modulation", {}))
            if spatial_modulation_override:
                spatial_modulation.update(dict(spatial_modulation_override))
            snapshot_count = int(stage_spec.get("snapshot_count", 0))

        params = SimulationParams(
            name="stable_periodic_patterns",
            preset_name=preset_name,
            K=0.80,
            t_max=t_max,
            delta_t=0.05,
            size=int(size),
            dx=float(merged_params_override.get("dx", 1.0)),
            random_seed=int(merged_params_override.get("random_seed", 42)),
            s=float(merged_params_override.get("s", 1.0)),
            r_a=float(merged_params_override.get("r_a", 1.0)),
            r_b=float(merged_params_override.get("r_b", 2.0)),
            b_a=float(merged_params_override.get("b_a", 0.1)),
            b_b=float(merged_params_override.get("b_b", 0.1)),
            D_a=float(merged_params_override.get("D_a", 0.01)),
            D_b=float(merged_params_override.get("D_b", 0.5)),
            A0=float(merged_params_override.get("A0", 0.1)),
            B0=float(merged_params_override.get("B0", 1.0)),
            initial_noise_a_amplitude=float(
                merged_params_override.get("initial_noise_a_amplitude", 0.05)
            ),
            initial_noise_b_amplitude=float(
                merged_params_override.get("initial_noise_b_amplitude", 0.01)
            ),
            extras={
                "color1": color1,
                "color2": color2,
                "mode_key": "stable_periodic_patterns",
                "params_override": merged_params_override,
                "development_percent": development_percent,
                "random_error_params": random_error_params,
                "spatial_modulation": spatial_modulation,
                "stripe_variant": stripe_variant,
                "snapshot_count": snapshot_count,
            },
        )
        output = self.simulation_service.run_activator_inhibitor(
            params,
            export_snapshots=export_snapshots,
            random_error_params=random_error_params,
        )
        experiment_id = build_experiment_id(params, color1, color2)
        texture_field = self._select_progression_texture_field(output, development_percent)
        texture_profile = self._fig23_texture_profile(development_percent)
        image_path = save_stripe_texture_image(
            texture_field,
            color1,
            color2,
            self.export_service.output_dir / f"{experiment_id}.png",
            **texture_profile,
        )
        raw_image_path = ""
        space_time_path = ""
        if stripe_variant is not None:
            raw_image_path = save_stripe_raw_image(
                output.A,
                self.export_service.output_dir / f"{experiment_id}_raw.png",
            )
            space_time_path = save_stripe_space_time_image(
                output.snapshots,
                self.export_service.output_dir / f"{experiment_id}_space_time.png",
            )
        result = self._finalize(
            "stable_periodic_patterns",
            preset_name,
            params,
            image_path,
            output.heatmap.tolist(),
            stage_label=stage_label,
            notes=notes,
        )
        result.raw_image_path = raw_image_path
        result.space_time_path = space_time_path
        result.snapshots = list(output.snapshots)
        return result

    def generate_labyrinths(
        self,
        *,
        stage: int,
        color1: str,
        color2: str,
        size: int = DEFAULT_TEXTURE_SIZE,
        params_override: dict | None = None,
        random_error_params: dict | None = None,
        export_snapshots: bool = False,
    ) -> ModeGenerationResult:
        bundle = load_figure_212_presets()
        stage_key = f"stage_{int(stage)}"
        stage_spec = dict(bundle["stage_presets"][stage_key])
        stage_overrides = dict(stage_spec.get("params_override", {}))
        model_params = dict(bundle["model_params"])
        if params_override:
            model_params.update(dict(params_override))
        if stage_overrides:
            model_params.update(stage_overrides)
        stage_tmax_map = dict(model_params.pop("stage_tmax_map"))
        initial_noise_a_amplitude = float(
            params_override.get("initial_noise_a_amplitude")
            if params_override and "initial_noise_a_amplitude" in params_override
            else stage_overrides.get(
                "initial_noise_a_amplitude",
                stage_spec.get(
                    "initial_noise_a_amplitude",
                    model_params.get("initial_noise_a_amplitude", 0.05),
                ),
            )
        )
        initial_noise_b_amplitude = float(
            params_override.get("initial_noise_b_amplitude")
            if params_override and "initial_noise_b_amplitude" in params_override
            else stage_overrides.get(
                "initial_noise_b_amplitude",
                stage_spec.get(
                    "initial_noise_b_amplitude",
                    model_params.get("initial_noise_b_amplitude", 0.01),
                ),
            )
        )
        initial_noise_smoothing_passes = int(
            params_override.get("initial_noise_smoothing_passes")
            if params_override and "initial_noise_smoothing_passes" in params_override
            else stage_overrides.get(
                "initial_noise_smoothing_passes",
                stage_spec.get(
                    "initial_noise_smoothing_passes",
                    model_params.get("initial_noise_smoothing_passes", 0),
                ),
            )
        )
        early_smoothing_fraction = float(
            params_override.get("early_smoothing_fraction")
            if params_override and "early_smoothing_fraction" in params_override
            else stage_overrides.get(
                "early_smoothing_fraction",
                stage_spec.get(
                    "early_smoothing_fraction",
                    model_params.get("early_smoothing_fraction", 0.0),
                ),
            )
        )
        early_smoothing_strength = float(
            params_override.get("early_smoothing_strength")
            if params_override and "early_smoothing_strength" in params_override
            else stage_overrides.get(
                "early_smoothing_strength",
                stage_spec.get(
                    "early_smoothing_strength",
                    model_params.get("early_smoothing_strength", 0.0),
                ),
            )
        )
        stage_re_defaults = dict(bundle["random_error_presets"][stage_key])
        merged_re_params = dict(stage_re_defaults)
        if random_error_params:
            merged_re_params.update(random_error_params)

        params = SimulationParams(
            name="labyrinths",
            preset_name=stage_key,
            K=float(model_params["K"]),
            t_max=float(stage_tmax_map[stage_key]),
            delta_t=float(model_params["delta_t"]),
            size=int(size),
            dx=float(model_params.get("dx", 1.0)),
            random_seed=int(model_params.get("random_seed", 42)),
            s=float(model_params["s"]),
            r_a=float(model_params["r_a"]),
            r_b=float(model_params["r_b"]),
            b_a=float(model_params["b_a"]),
            b_b=float(model_params["b_b"]),
            D_a=float(model_params["D_a"]),
            D_b=float(model_params["D_b"]),
            A0=0.1,
            B0=1.0,
            initial_noise_a_amplitude=initial_noise_a_amplitude,
            initial_noise_b_amplitude=initial_noise_b_amplitude,
            extras={
                "color1": color1,
                "color2": color2,
                "mode_key": "labyrinths",
                "random_error_params": merged_re_params,
                "initial_noise_smoothing_passes": initial_noise_smoothing_passes,
                "early_smoothing_fraction": early_smoothing_fraction,
                "early_smoothing_strength": early_smoothing_strength,
            },
        )
        output = self.simulation_service.run_labyrinth(
            params,
            random_error_params=merged_re_params,
            export_snapshots=export_snapshots,
        )
        experiment_id = build_experiment_id(params, color1, color2)
        image_path = save_texture_image(
            output.A,
            output.B,
            color1,
            color2,
            self.export_service.output_dir / f"{experiment_id}.png",
        )
        result = self._finalize(
            "labyrinths",
            stage_key,
            params,
            image_path,
            output.heatmap.tolist(),
            stage_label=str(stage_spec.get("label", stage_key)),
            notes="Generated through mode dispatch",
        )
        result.snapshots = list(output.snapshots)
        return result
