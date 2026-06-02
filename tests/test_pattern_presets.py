from config_23 import (
    FIG23_DEFAULT_DEVELOPMENT,
    FIG23_DEFAULT_STAGE,
    FIG23_DEVELOPMENT_ORDER,
    FIG23_DEVELOPMENT_PRESETS,
    FIG23_DEVELOPMENT_RANDOM_ERROR_PRESETS,
    FIG23_PROGRESSION_LEVELS,
    FIG23_STAGE_ORDER,
    FIG23_STAGE_PRESETS,
)


def test_fig23_stage_order_and_default():
    assert FIG23_STAGE_ORDER == [
        "stage_1",
        "stage_2",
        "stage_3",
        "stage_4",
        "stage_5",
    ]
    assert FIG23_DEFAULT_STAGE == "stage_3"


def test_fig23_stage_three_is_best_candidate():
    stage3 = FIG23_STAGE_PRESETS["stage_3"]
    assert stage3["label"] == "Stage 3 - Current best"
    assert stage3["params_override"]["D_b"] == 0.3450
    assert stage3["params_override"]["D_a"] == 0.0057
    assert stage3["params_override"]["r_b"] == 0.050
    assert stage3["params_override"]["initial_noise_a_amplitude"] == 0.0420
    assert stage3["params_override"]["initial_noise_b_amplitude"] == 0.0085


def test_fig23_development_order_and_default():
    assert FIG23_DEVELOPMENT_ORDER == [
        "dev_10",
        "dev_30",
        "dev_60",
        "dev_90",
    ]
    assert FIG23_DEFAULT_DEVELOPMENT == "dev_60"


def test_fig23_development_sixty_percent_uses_best_stripe_calibration():
    dev60 = FIG23_DEVELOPMENT_PRESETS["dev_60"]
    assert dev60["progress_percent"] == 60
    assert dev60["t_max"] == 54.0
    assert dev60["params_override"]["D_b"] == 0.276
    assert dev60["params_override"]["D_a"] == 0.00456


def test_fig23_development_random_error_defaults_follow_progression():
    dev10 = FIG23_DEVELOPMENT_RANDOM_ERROR_PRESETS["dev_10"]
    dev30 = FIG23_DEVELOPMENT_RANDOM_ERROR_PRESETS["dev_30"]
    dev60 = FIG23_DEVELOPMENT_RANDOM_ERROR_PRESETS["dev_60"]
    dev90 = FIG23_DEVELOPMENT_RANDOM_ERROR_PRESETS["dev_90"]

    assert dev10["enabled"] is False
    assert dev10["strength"] < dev60["strength"] < dev90["strength"]
    assert dev10["region_size"] < dev60["region_size"] < dev90["region_size"]
    assert dev10["drift_frequency"] < dev30["drift_frequency"] <= dev60["drift_frequency"] < dev90["drift_frequency"]


def test_fig23_progression_random_error_profiles_are_monotonic_and_stripe_focused():
    profiles = [FIG23_PROGRESSION_LEVELS[key]["random_error_override"] for key in ["malo", "vice", "jeste_vice", "nejvice"]]

    strengths = [profile["strength"] for profile in profiles]
    micro_noises = [profile["micro_noise"] for profile in profiles]
    probabilities = [profile["probability"] for profile in profiles]
    local_segment_flags = [bool(profile.get("local_y_segments", False)) for profile in profiles]

    assert strengths[0] >= strengths[1] > strengths[2] >= strengths[3]
    assert micro_noises[0] >= micro_noises[1] >= micro_noises[2] >= micro_noises[3]
    assert probabilities[0] > probabilities[1] > probabilities[2] >= probabilities[3]
    assert local_segment_flags == [True, True, False, False]


def test_fig23_progression_spatial_modulation_is_stripe_oriented_and_within_target_range():
    profiles = [FIG23_PROGRESSION_LEVELS[key]["spatial_modulation"] for key in ["malo", "vice", "jeste_vice", "nejvice"]]

    eps_s = [profile["eps_s"] for profile in profiles]
    eps_da = [profile["eps_Da"] for profile in profiles]
    orientations = {profile.get("orientation") for profile in profiles}

    assert orientations == {"stripe_x"}
    assert all(0.03 <= value <= 0.05 for value in eps_s)
    assert all(0.03 <= value <= 0.05 for value in eps_da)
    assert eps_s[0] < eps_s[1] < eps_s[2] < eps_s[3]
    assert eps_da[0] < eps_da[1] < eps_da[2] < eps_da[3]
