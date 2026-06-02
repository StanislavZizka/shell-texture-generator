"""
Test Random Error ve statickém režimu
Ověření, že biologické poruchy se projeví ve výsledné textuře
"""

import numpy as np
from flask import Flask
from services.texture_generator import TextureGeneratorService
from services.random_error_module import create_random_error_params

def test_static_mode_random_error():
    """Test Random Error implementation in static mode"""
    print("=" * 80)
    print("TEST: Random Error in Static Mode")
    print("=" * 80)

    service = TextureGeneratorService()

    # Test parameters
    K = 0.80
    t_max = 60.0
    delta_t = 0.5
    color1 = "#FF5722"
    color2 = "#03A9F4"
    size = 128

    print(f"\nSimulation parameters:")
    print(f"  K: {K}")
    print(f"  t_max: {t_max}")
    print(f"  delta_t: {delta_t}")
    print(f"  size: {size}x{size}")
    print(f"  steps: {int(t_max/delta_t)}")

    # Test 1: WITHOUT Random Error (baseline)
    print(f"\n{'='*80}")
    print("TEST 1: Baseline (Random Error DISABLED)")
    print(f"{'='*80}")

    re_params_disabled = create_random_error_params(enabled=False)

    baseline_path = service.generate_with_biological_perturbation(
        K=K,
        t_max=t_max,
        delta_t=delta_t,
        color1=color1,
        color2=color2,
        size=size,
        random_error_params=re_params_disabled
    )

    print(f"[OK] Baseline texture generated: {baseline_path}")

    # Test 2: WITH Random Error (should show defects)
    print(f"\n{'='*80}")
    print("TEST 2: With Random Error (ENABLED)")
    print(f"{'='*80}")

    re_params_enabled = create_random_error_params(
        enabled=True,
        strength=0.045,      # Medium strength
        duration=30,         # Medium duration
        frequency=0.08,      # Moderate temporal oscillation
        probability=0.05,    # 5% trigger chance per step
        num_regions=3,       # 3 defect zones
        region_size=12,      # Medium-sized zones
        jitter=0.12,         # Edge irregularity
        micro_noise=0.06,    # Microstructure noise
        alpha_var=0.22,      # Amplitude variation
        beta=0.10,           # Coupling to inhibitor
        drift_x=1.2,         # Spatial drift
        drift_y=1.0,
        drift_frequency=0.002
    )

    print(f"\nRandom Error parameters:")
    for key, value in re_params_enabled.items():
        if key != 'enabled':
            print(f"  {key}: {value}")

    perturbed_path = service.generate_with_biological_perturbation(
        K=K,
        t_max=t_max,
        delta_t=delta_t,
        color1=color1,
        color2=color2,
        size=size,
        random_error_params=re_params_enabled
    )

    print(f"[OK] Perturbed texture generated: {perturbed_path}")

    # Visual comparison
    print(f"\n{'='*80}")
    print("VISUAL COMPARISON")
    print(f"{'='*80}")
    print(f"\nBaseline (no defects):  {baseline_path}")
    print(f"Perturbed (with defects): {perturbed_path}")
    print(f"\nExpected:")
    print(f"  - Baseline should show uniform pattern")
    print(f"  - Perturbed should show LOCAL biological defects:")
    print(f"    * Localized spots/disturbances")
    print(f"    * Pattern breakdown in affected regions")
    print(f"    * Irregular pigment clusters")
    print(f"    * Spatial drift effects")

    print(f"\n{'='*80}")
    print("[SUCCESS] Test completed - Check images manually")
    print(f"{'='*80}")

    return {
        'baseline': baseline_path,
        'perturbed': perturbed_path
    }


if __name__ == '__main__':
    # Create Flask app context for testing
    app = Flask(__name__)
    app.config['DEBUG'] = True

    with app.app_context():
        results = test_static_mode_random_error()

        print(f"\n{'='*80}")
        print("Test complete. Compare the two images:")
        print(f"  1. {results['baseline']}")
        print(f"  2. {results['perturbed']}")
        print(f"{'='*80}")
