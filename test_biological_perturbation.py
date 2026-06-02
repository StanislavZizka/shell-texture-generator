"""
Test biologických perturbací - porovnání s snapshot_step0300.png

Nové úpravy:
1. Nepravidelné masky s jitterem (±10% na hranách)
2. Variabilní amplituda α (±20% random noise)
3. Počáteční šum v A, B polích
4. R aplikováno PO difuzi

Očekávaný výsledek:
- Jemné, organické defekty (ne hladké kruhy)
- Biologická nepravidelnost
- Mikrostruktura
- Podobné snapshot_step0300.png
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from services.random_error_module import RandomErrorModule, create_random_error_params
from config import STATIC_RANDOM_ERROR_PRESETS

def test_biological_appearance():
    """
    Test biologického vzhledu s novými úpravami
    """
    print("=" * 80)
    print("TEST BIOLOGICKÝCH PERTURBACÍ - Nepravidelné masky + šum")
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

        print(f"\nParameters:")
        print(f"  Strength (alpha): {re_preset['strength']}")
        print(f"  Num regions: {re_preset['num_regions']}")
        print(f"  Region size: {re_preset['region_size']}")
        print(f"\nNew biological features:")
        print(f"  - Irregular masks (jitter on edges)")
        print(f"  - Variable amplitude (+-20% random)")
        print(f"  - Microstructure noise (+-5%)")

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

        # Simulate with initial noise (like in texture_generator.py)
        np.random.seed(42)
        A = 1.0 + np.random.rand(*size) * 0.1
        A += np.random.normal(0, 0.01, A.shape)  # Biological noise

        # Trigger multiple perturbations
        for _ in range(5):
            module.trigger_perturbation(
                strength=params['strength'],
                duration=params['duration'],
                num_regions=params['num_regions'],
                region_size=params['region_size'],
                frequency=params['frequency']
            )

        # Simulate to step 300 (like reference)
        print(f"\nSimulating 300 steps...")
        for step in range(300):
            t = step * 0.5
            R = module.apply_random_error(A, t, step, params)

            # Apply perturbation
            A += R

            # Simple clipping (no full simulation, just perturbation test)
            np.clip(A, 0, 2, out=A)

            # Print stats every 50 steps
            if step % 50 == 0:
                num_active = len(module.active_perturbations)
                R_max = np.max(np.abs(R))
                print(f"  Step {step:3d}: {num_active} active, max|R|={R_max:.6f}")

        # Final perturbation field at step 300
        R_final = module.apply_random_error(A, 300 * 0.5, 300, params)

        # Statistics
        R_mean = np.mean(R_final)
        R_max = np.max(R_final)
        R_min = np.min(R_final)
        nonzero = np.count_nonzero(np.abs(R_final) > 1e-6)

        print(f"\nStep 300 statistics:")
        print(f"  Mean: {R_mean:+.6f}")
        print(f"  Max: {R_max:+.6f}")
        print(f"  Min: {R_min:+.6f}")
        print(f"  Nonzero: {nonzero}/{size[0]*size[1]} ({nonzero/(size[0]*size[1])*100:.1f}%)")

        # Visualize
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        fig.suptitle(f'Biological Perturbation Test: {preset_name} (Step 300)\n' +
                     f'Irregular masks + Variable amplitude + Microstructure',
                     fontsize=14, fontweight='bold')

        # 1. Perturbation field R
        ax = axes[0]
        im = ax.imshow(R_final, cmap='RdBu_r', vmin=-re_preset['strength'], vmax=re_preset['strength'])
        ax.set_title('R(x,y,t) - Biological Perturbation')
        ax.axis('off')
        plt.colorbar(im, ax=ax, fraction=0.046)

        # 2. Activator with perturbation
        ax = axes[1]
        im = ax.imshow(A, cmap='RdBu_r', vmin=0, vmax=2)
        ax.set_title('Activator A (with perturbations)')
        ax.axis('off')
        plt.colorbar(im, ax=ax, fraction=0.046)

        # 3. Sample mask (show irregularity)
        if module.perturbation_masks:
            sample_mask = module.perturbation_masks[0]
            ax = axes[2]
            im = ax.imshow(sample_mask, cmap='hot', vmin=0, vmax=1)
            ax.set_title('Sample Mask (with jitter + noise)')
            ax.axis('off')
            plt.colorbar(im, ax=ax, fraction=0.046)

        plt.tight_layout()
        output_path = output_dir / f'biological_{preset_name}_step300.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"\n[OK] Saved: {output_path}")

    print(f"\n{'='*80}")
    print("TEST COMPLETE")
    print(f"{'='*80}")
    print(f"\nGenerated biological perturbation tests in:")
    print(f"  {output_dir}")
    print(f"\nCompare with reference:")
    print(f"  static/images/snapshot_step0300.png")
    print(f"\nExpected improvements:")
    print(f"  - Irregular, organic edges (not smooth circles)")
    print(f"  - Micro-variations in intensity")
    print(f"  - Biological noise texture")
    print(f"  - More similar to natural shell defects")


if __name__ == '__main__':
    test_biological_appearance()
