"""
Test Random Error - Vizuální ověření Gaussian gradientů a oscilací

Ověřuje:
1. Gaussian gradient masky (ne binární kruhy)
2. Rozptýlené frekvence a fáze
3. Oscilace sin(2πft+φ) v čase
4. Lokální biologické defekty (ne globální šum)
5. Každý preset má jiný vizuální charakter
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from services.random_error_module import RandomErrorModule, create_random_error_params
from config import STATIC_RANDOM_ERROR_PRESETS, STATIC_MODE_PRESETS

def test_visual_output():
    """
    Test vizuálního výstupu Random Erroru s Gaussian gradienty
    """
    print("=" * 80)
    print("RANDOM ERROR VISUAL TEST - Gaussian Gradients & Oscillations")
    print("=" * 80)
    print()

    # Grid size
    size = (128, 128)

    # Output directory
    output_dir = Path("static/images/random_error_calibration")
    output_dir.mkdir(exist_ok=True, parents=True)

    # Test all presets
    presets = ['low_diffusion', 'medium_diffusion', 'high_diffusion', 'balanced']

    for preset_name in presets:
        print(f"\n{'='*80}")
        print(f"Testing preset: {preset_name.upper()}")
        print(f"{'='*80}")

        # Get parameters
        re_preset = STATIC_RANDOM_ERROR_PRESETS[preset_name]
        sim_preset = STATIC_MODE_PRESETS[preset_name]

        print(f"\nParameters:")
        print(f"  Strength (alpha): {re_preset['strength']}")
        print(f"  Frequency (f): {re_preset['frequency']}")
        print(f"  Num regions: {re_preset['num_regions']}")
        print(f"  Region size: {re_preset['region_size']}")
        print(f"  D_b: {sim_preset['D_b']}")

        # Create module
        module = RandomErrorModule(size, seed=42)

        # Create params
        params = create_random_error_params(
            enabled=True,
            strength=re_preset['strength'],
            duration=re_preset['duration'],
            frequency=re_preset['frequency'],
            probability=re_preset['probability'],
            num_regions=re_preset['num_regions'],
            region_size=re_preset['region_size'],
            jitter=re_preset['jitter'],
            micro_noise=re_preset['micro_noise'],
            alpha_var=re_preset['alpha_var']
        )

        # Trigger perturbation
        module.trigger_perturbation(
            strength=params['strength'],
            duration=params['duration'],
            num_regions=params['num_regions'],
            region_size=params['region_size'],
            frequency=params['frequency'],
            jitter=params['jitter'],
            micro_noise=params['micro_noise'],
            alpha_var=params['alpha_var']
        )

        # Test time evolution
        A_dummy = np.ones(size) * 0.5
        time_steps = [0, 10, 20, 30, 40, 50, 60, 70]
        R_fields = []

        print(f"\nTime evolution:")
        for step in time_steps:
            t = step * 0.5
            R = module.apply_random_error(A_dummy, t, step, params)
            R_fields.append(R)

            R_mean = np.mean(R)
            R_max = np.max(R)
            R_min = np.min(R)
            nonzero = np.count_nonzero(np.abs(R) > 1e-6)

            print(f"  Step {step:3d}: mean={R_mean:+.6f}, max={R_max:+.6f}, min={R_min:+.6f}, "
                  f"nonzero={nonzero}/{size[0]*size[1]}")

        # Visualize
        fig, axes = plt.subplots(2, 4, figsize=(16, 8))
        fig.suptitle(f'Random Error: {preset_name}\n' +
                     f'alpha={re_preset["strength"]}, f={re_preset["frequency"]}, ' +
                     f'regions={re_preset["num_regions"]} (Gaussian gradient)',
                     fontsize=14, fontweight='bold')

        for i, (step, R) in enumerate(zip(time_steps, R_fields)):
            ax = axes[i // 4, i % 4]
            im = ax.imshow(R, cmap='RdBu_r', vmin=-params['strength'], vmax=params['strength'])
            ax.set_title(f'Step {step}')
            ax.axis('off')
            plt.colorbar(im, ax=ax, fraction=0.046)

        plt.tight_layout()
        output_path = output_dir / f'visual_{preset_name}.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"\n[OK] Visualization saved: {output_path}")

        # Test mask properties
        print(f"\n[CHECK] Mask properties:")
        mask = module.perturbation_masks[0]

        # Check for gradient (not binary)
        unique_vals = len(np.unique(mask))
        print(f"  Unique mask values: {unique_vals}")

        if unique_vals > 10:
            print(f"  [PASS] Mask has gradient (Gaussian), not binary")
        else:
            print(f"  [FAIL] Mask appears binary (only {unique_vals} unique values)")

        # Check localization
        affected_ratio = np.sum(mask > 0.1) / (size[0] * size[1])
        print(f"  Affected area (>10% intensity): {affected_ratio*100:.2f}%")

        if affected_ratio < 0.3:
            print(f"  [PASS] Perturbations are localized")
        else:
            print(f"  [FAIL] Perturbations too widespread")

        # Visualize mask
        fig, ax = plt.subplots(1, 1, figsize=(6, 6))
        im = ax.imshow(mask, cmap='hot', vmin=0, vmax=1)
        ax.set_title(f'Perturbation Mask: {preset_name}\n' +
                     f'{re_preset["num_regions"]} regions with Gaussian gradient')
        ax.axis('off')
        plt.colorbar(im, ax=ax, fraction=0.046, label='Intensity')

        mask_path = output_dir / f'mask_{preset_name}.png'
        plt.savefig(mask_path, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"[OK] Mask visualization saved: {mask_path}")

    print(f"\n{'='*80}")
    print("VISUAL TEST COMPLETE")
    print(f"{'='*80}")
    print(f"\nCheck visualizations in: {output_dir}")
    print("\nExpected results:")
    print("  - Gaussian gradients (smooth fade), not sharp circles")
    print("  - Oscillating patterns (sin wave)")
    print("  - Localized defects (<30% of grid)")
    print("  - Different character for each preset (strength varies)")


if __name__ == '__main__':
    test_visual_output()
