"""
Shared model parameter presets used by the reaction-diffusion generators.

This recreates the source module that was previously available only through
cached bytecode in the workspace.
"""

MODEL_212_PARAMS = {
    "name": "Figure 2.12 Labyrinth",
    "s": 0.139266,
    "r_a": 0.211395,
    "r_b": 0.448224,
    "b_a": 0.01,
    "b_b": 0.01,
    "D_a": 0.019207,
    "D_b": 0.931674,
    "K": 0.492651,
    "delta_t": 0.5,
    "dx": 1.0,
    "random_seed": 42,
    "stage_tmax_map": {
        1: 20.0,
        2: 60.0,
        3: 140.0,
        4: 260.0,
        5: 400.0,
    },
}

RANDOM_ERROR_212_PRESET = {
    "strength": 0.001,
    "duration": 10,
    "frequency": 0.05,
    "num_regions": 3,
    "region_size": 15,
    "probability": 0.03,
}

RANDOM_ERROR_212_STAGES = {
    "stage1": {
        "strength": 0.02,
        "duration": 10,
        "frequency": 0.05,
        "num_regions": 3,
        "region_size": 15,
        "probability": 0.03,
    },
    "stage2": {
        "strength": 0.001,
        "duration": 10,
        "frequency": 0.05,
        "num_regions": 3,
        "region_size": 10,
        "probability": 0.03,
    },
    "stage3": {
        "strength": 0.01,
        "duration": 30,
        "frequency": 0.05,
        "num_regions": 3,
        "region_size": 15,
        "probability": 0.05,
    },
    "stage4": {
        "strength": 0.01,
        "duration": 10,
        "frequency": 0.05,
        "num_regions": 8,
        "region_size": 20,
        "probability": 0.05,
    },
    "stage5": {
        "strength": 0.005,
        "duration": 10,
        "frequency": 0.05,
        "num_regions": 3,
        "region_size": 20,
        "probability": 0.08,
    },
}

