"""Small helpers for preview data and cached gallery output."""

from __future__ import annotations

from pathlib import Path


def preview_filename(image_path: str | Path) -> str:
    """Return a filename that can be used in gallery previews."""

    return Path(image_path).name

