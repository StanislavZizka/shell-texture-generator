"""Figure 2.3 stripe stage presets loaded from versioned JSON."""

from __future__ import annotations

from core.presets import load_figure_23_presets

_FIG23_BUNDLE = load_figure_23_presets()

FIG23_MODEL_PARAMS = dict(
    _FIG23_BUNDLE.get("model_params")
    or _FIG23_BUNDLE.get("stages", {}).get("stage_3", {}).get("params_override", {})
)
FIG23_STAGE_ORDER = list(_FIG23_BUNDLE["stage_order"])
FIG23_DEFAULT_STAGE = str(_FIG23_BUNDLE["default_stage"])
FIG23_STAGE_PRESETS = dict(_FIG23_BUNDLE["stages"])
FIG23_DEVELOPMENT_ORDER = list(_FIG23_BUNDLE["development_order"])
FIG23_DEFAULT_DEVELOPMENT = str(_FIG23_BUNDLE["default_development"])
FIG23_DEVELOPMENT_PRESETS = dict(_FIG23_BUNDLE["development_presets"])
FIG23_PROGRESSION_ORDER = list(_FIG23_BUNDLE.get("progression_order", []))
FIG23_PROGRESSION_LEVELS = dict(_FIG23_BUNDLE.get("progression_levels", {}))
FIG23_DEVELOPMENT_RANDOM_ERROR_PRESETS = dict(_FIG23_BUNDLE["random_error_presets"])
FIG23_STRIPE_VARIANTS = dict(_FIG23_BUNDLE.get("stripe_variants", {}))


def get_fig23_stage(stage_key: str) -> dict:
    """Return a normalized stage spec for Figure 2.3."""

    return dict(FIG23_STAGE_PRESETS[stage_key])


def get_fig23_development(development_key: str) -> dict:
    """Return a normalized development spec for Figure 2.3."""

    return dict(FIG23_DEVELOPMENT_PRESETS[development_key])


def get_fig23_development_random_error(development_key: str) -> dict:
    """Return a normalized random-error spec for Figure 2.3 development."""

    return dict(FIG23_DEVELOPMENT_RANDOM_ERROR_PRESETS[development_key])


def get_fig23_stripe_variant(variant_key: str) -> dict:
    """Return a normalized spatial-modulation variant for Figure 2.3 stripes."""

    return dict(FIG23_STRIPE_VARIANTS[variant_key])


def get_fig23_progression_level(level_key: str) -> dict:
    """Return a normalized progression level for Figure 2.3 space-time view."""

    return dict(FIG23_PROGRESSION_LEVELS[level_key])
