# Shell Texture Generator

Reproducible shell texture generator built around a reaction-diffusion core, a thin Flask web layer, and versioned presets.

## What It Does
- Generates shell-like textures from deterministic or seed-controlled simulations.
- Saves experiment metadata, metrics, and image outputs.
- Supports web-driven generation and scriptable batch workflows.

## Project Layout
- `simulation/` numerical core
- `rendering/` image export
- `evaluation/` metrics and comparisons
- `experiments/` records and reports
- `services/` orchestration layer
- `routes/` Flask endpoints and pages
- `scripts/` active CLI entrypoints
- `scripts/legacy/` archived ad hoc helpers
- `configs/presets/` versioned preset bundles

## Quick Start
```bash
python -m pip install -r requirements.txt
python app.py
```

## Tests
```bash
python -m pytest -q
```

## Batch Reproducibility
Run the three first-class modes from the command line:
```bash
python scripts/run_batch.py --size 32
```

Batch outputs are written under `outputs/batches/` and include:
- rendered textures
- experiment records
- markdown reports
- a JSON summary of the whole sweep

## Notes
- The project keeps Flask for compatibility, but the core logic now lives outside the web routes.
- Presets are loaded from JSON bundles to keep experiment runs reproducible.
- The reference snapshot for the smoke batch lives in `experiments/references/three_core_modes_smoke.json`.
