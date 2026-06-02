# Architecture

## Layers
- `simulation/` contains pure numerical code.
- `rendering/` converts arrays to images.
- `evaluation/` computes metrics and comparisons.
- `experiments/` stores records and reports.
- `services/` coordinates use cases.
- `routes/` only handles HTTP and template rendering.

## Data Flow
1. Request or script selects a preset.
2. Service builds validated parameters.
3. Simulation produces arrays.
4. Rendering saves the image.
5. Evaluation and experiment recording persist metadata.

