"""
Test Random Error - Porovnání s referenčním snapshot_step0300.png

Cíl: Ověřit, že aktuální Random Error generuje stejné lokální biologické defekty
jako v referenčním obrázku (červené skvrny na modrém pozadí).

Referenční charakteristiky (snapshot_step0300.png):
- Výrazné červené/růžové skvrny (lokální defekty)
- Modrá základna s jemnou texturou
- Ostře kontrastní přechody
- Rozptýlené defekty (ne uniformní)
- Velikost defektů: cca 5-15 pixelů
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from services.random_error_module import RandomErrorModule, create_random_error_params
from config import STATIC_RANDOM_ERROR_PRESETS

def test_reference_comparison():
    """
    Test Random Erroru s novými parametry vyladěnými podle reference
    """
    print("=" * 80)
    print("RANDOM ERROR - REFERENCE COMPARISON TEST")
    print("Reference: snapshot_step0300.png")
    print("=" * 80)
    print()

    # Grid size (stejný jako reference)
    size = (512, 512)

    # Output directory
    output_dir = Path("static/images/random_error_calibration")
    output_dir.mkdir(exist_ok=True, parents=True)

    # Test each preset
    presets = ['low_diffusion', 'medium_diffusion', 'high_diffusion', 'balanced']

    for preset_name in presets:
        print(f"\n{'='*80}")
        print(f"Testing preset: {preset_name.upper()}")
        print(f"{'='*80}")

        # Get parameters
        re_preset = STATIC_RANDOM_ERROR_PRESETS[preset_name]

        print(f"\nNew parameters (tuned to reference):")
        print(f"  Strength (alpha): {re_preset['strength']} (prev: 0.03)")
        print(f"  Frequency (f): {re_preset['frequency']}")
        print(f"  Num regions: {re_preset['num_regions']} (prev: 5)")
        print(f"  Region size: {re_preset['region_size']} (prev: 10)")
        print(f"  Duration: {re_preset['duration']}")

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
            region_size=re_preset['region_size']
        )

        # Trigger multiple perturbations (simulate realistic scenario)
        for _ in range(3):
            module.trigger_perturbation(
                strength=params['strength'],
                duration=params['duration'],
                num_regions=params['num_regions'],
                region_size=params['region_size'],
                frequency=params['frequency']
            )

        # Test at step 300 (same as reference snapshot)
        A_dummy = np.ones(size) * 0.5
        step = 300
        t = step * 0.5

        R = module.apply_random_error(A_dummy, t, step, params)

        # Statistics
        R_mean = np.mean(R)
        R_max = np.max(R)
        R_min = np.min(R)
        R_std = np.std(R)
        nonzero = np.count_nonzero(np.abs(R) > 1e-6)

        print(f"\nStep {step} statistics:")
        print(f"  Mean: {R_mean:+.6f}")
        print(f"  Max: {R_max:+.6f}")
        print(f"  Min: {R_min:+.6f}")
        print(f"  Std: {R_std:.6f}")
        print(f"  Nonzero pixels: {nonzero}/{size[0]*size[1]} ({nonzero/(size[0]*size[1])*100:.1f}%)")

        # Check if perturbations are visible
        if abs(R_max) > 0.01 or abs(R_min) > 0.01:
            print(f"  [PASS] Perturbations are VISIBLE (amplitude > 0.01)")
        else:
            print(f"  [FAIL] Perturbations too weak (amplitude < 0.01)")

        # Visualize
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        fig.suptitle(f'Random Error: {preset_name} (Step {step})\n' +
                     f'alpha={re_preset["strength"]}, f={re_preset["frequency"]}, ' +
                     f'regions={re_preset["num_regions"]}, size={re_preset["region_size"]}px',
                     fontsize=14, fontweight='bold')

        # 1. Perturbation field R
        ax = axes[0]
        im = ax.imshow(R, cmap='RdBu_r', vmin=-re_preset['strength'], vmax=re_preset['strength'])
        ax.set_title('Perturbation Field R(x,y,t)')
        ax.axis('off')
        plt.colorbar(im, ax=ax, fraction=0.046, label='Amplitude')

        # 2. Simulated activator with perturbation
        A_with_R = A_dummy + R
        ax = axes[1]
        im = ax.imshow(A_with_R, cmap='RdBu_r', vmin=0, vmax=1)
        ax.set_title('Activator A + R (Simulated)')
        ax.axis('off')
        plt.colorbar(im, ax=ax, fraction=0.046, label='Concentration')

        # 3. Mask visualization
        if module.perturbation_masks:
            combined_mask = np.zeros(size)
            for mask in module.perturbation_masks:
                combined_mask += mask
            combined_mask = np.clip(combined_mask, 0, 1)

            ax = axes[2]
            im = ax.imshow(combined_mask, cmap='hot', vmin=0, vmax=1)
            ax.set_title(f'Combined Perturbation Masks\n({len(module.perturbation_masks)} active)')
            ax.axis('off')
            plt.colorbar(im, ax=ax, fraction=0.046, label='Intensity')

        plt.tight_layout()
        output_path = output_dir / f'reference_test_{preset_name}.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"\n[OK] Visualization saved: {output_path}")

    print(f"\n{'='*80}")
    print("REFERENCE COMPARISON TEST COMPLETE")
    print(f"{'='*80}")
    print(f"\nGenerated visualizations in: {output_dir}")
    print("\nCompare with reference: static/images/snapshot_step0300.png")
    print("\nExpected characteristics:")
    print("  - Výrazné červené/růžové skvrny (lokální defekty)")
    print("  - Ostře kontrastní přechody")
    print("  - Rozptýlené defekty (ne uniformní)")
    print("  - Strength: 0.05-0.07 (výrazně vyšší než dříve)")
    print("  - Num regions: 4-6 (více defektů)")
    print("  - Region size: 8-12px (menší, ostřejší skvrny)")


if __name__ == '__main__':
    test_reference_comparison()
