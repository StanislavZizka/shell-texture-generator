"""Preset service that exposes versioned preset bundles."""

from __future__ import annotations

from core.presets import (
    load_activator_inhibitor_presets,
    load_figure_211_presets,
    load_figure_23_presets,
)


class PresetService:
    """Load preset bundles from JSON files."""

    def get_static_mode_presets(self) -> dict:
        return load_activator_inhibitor_presets()

    def get_figure_23_presets(self) -> dict:
        return load_figure_23_presets()

    def get_figure_211_presets(self) -> dict:
        return load_figure_211_presets()
