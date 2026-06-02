"""Export service for rendering simulation output to disk."""

from __future__ import annotations

from pathlib import Path

from core.paths import STATIC_DIR
from rendering.texture_export import save_texture_image


class ExportService:
    """Render images into the web-served static directory."""

    def __init__(self, output_dir: Path | None = None):
        self.output_dir = output_dir or (STATIC_DIR / "images")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_texture(
        self,
        A,
        B,
        color1: str,
        color2: str,
        filename: str,
    ) -> str:
        return save_texture_image(A, B, color1, color2, self.output_dir / filename)

    def cleanup_outputs(self, prefix: str) -> None:
        """Remove generated images that start with the given prefix."""
        for path in self.output_dir.glob(f"{prefix}*.png"):
            if path.is_file():
                path.unlink(missing_ok=True)
