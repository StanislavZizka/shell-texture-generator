"""Figure 2.12 labyrinth configuration loaded from versioned JSON."""

from __future__ import annotations

from core.presets import load_figure_212_presets

_FIG212_BUNDLE = load_figure_212_presets()

FIG212_STAGE_ORDER = list(_FIG212_BUNDLE["stage_order"])
FIG212_DEFAULT_STAGE = str(_FIG212_BUNDLE["default_stage"])
MODEL_212_PARAMS = dict(_FIG212_BUNDLE["model_params"])
FIG212_STAGE_PRESETS = dict(_FIG212_BUNDLE["stage_presets"])
RANDOM_ERROR_212_STAGES = dict(_FIG212_BUNDLE["random_error_presets"])
FIG212_DEVELOPMENT_ORDER = list(_FIG212_BUNDLE["development_order"])
FIG212_DEFAULT_DEVELOPMENT = str(_FIG212_BUNDLE["default_development"])
FIG212_DEVELOPMENT_PRESETS = dict(_FIG212_BUNDLE["development_presets"])
FIG212_DEVELOPMENT_RANDOM_ERROR_PRESETS = dict(_FIG212_BUNDLE["development_random_error_presets"])
