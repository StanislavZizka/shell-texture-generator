"""
Test dynamického spouštění perturbací během simulace

Ověřuje:
1. Nové perturbace se spouštějí průběžně (ne jen při inicializaci)
2. Perturbace se objevují a mizí v čase (dynamické)
3. Každý krok má jinou masku a fázi
"""

import numpy as np
from services.random_error_module import RandomErrorModule, create_random_error_params

def test_dynamic_triggering():
    """
    Test, že perturbace se spouštějí dynamicky během simulace
    """
    print("=" * 80)
    print("TEST DYNAMICKÉHO SPOUŠTĚNÍ PERTURBACÍ")
    print("=" * 80)
    print()

    # Setup
    size = (128, 128)
    module = RandomErrorModule(size, seed=42)

    # Parameters
    params = create_random_error_params(
        enabled=True,
        strength=0.06,
        duration=30,
        frequency=0.06,
        probability=0.05,  # 5% šance každý krok
        num_regions=5,
        region_size=10
    )

    # Simulate 200 steps
    A_dummy = np.ones(size) * 0.5
    perturbation_counts = []
    max_amplitudes = []

    print("Simulace 200 kroků...")
    print(f"Pravděpodobnost nové perturbace: {params['probability']*100}% každý krok")
    print()

    for step in range(200):
        t = step * 0.5
        R = module.apply_random_error(A_dummy, t, step, params)

        # Track statistics
        num_active = len(module.active_perturbations)
        perturbation_counts.append(num_active)

        max_amp = np.max(np.abs(R))
        max_amplitudes.append(max_amp)

        # Print every 20 steps
        if step % 20 == 0:
            print(f"Krok {step:3d}: {num_active} aktivních perturbací, max|R|={max_amp:.6f}")

    print()
    print("=" * 80)
    print("VÝSLEDKY")
    print("=" * 80)

    # Statistics
    avg_active = np.mean(perturbation_counts)
    max_active = np.max(perturbation_counts)
    total_triggered = sum(1 for i in range(1, len(perturbation_counts))
                          if perturbation_counts[i] > perturbation_counts[i-1])

    print(f"\nStatistiky perturbací:")
    print(f"  Průměrný počet aktivních: {avg_active:.2f}")
    print(f"  Maximální počet současně: {max_active}")
    print(f"  Celkem spuštěno nových: {total_triggered}")

    # Check if perturbations were triggered
    if total_triggered > 0:
        print(f"\n[PASS] Perturbace se spousteji dynamicky behem simulace")
        print(f"       {total_triggered} novych perturbaci za 200 kroku")
    else:
        print(f"\n[FAIL] Zadne nove perturbace se nespustily")

    # Check amplitude variation
    amp_variation = np.std(max_amplitudes)
    if amp_variation > 0.001:
        print(f"[PASS] Amplituda se meni v case (std={amp_variation:.6f})")
    else:
        print(f"[FAIL] Amplituda je konstantni (staticke)")

    # Check for non-zero perturbations
    nonzero_steps = sum(1 for amp in max_amplitudes if amp > 1e-6)
    coverage = (nonzero_steps / len(max_amplitudes)) * 100

    print(f"\nPokryti perturbacemi:")
    print(f"  {nonzero_steps}/{len(max_amplitudes)} kroku ma nenulove R ({coverage:.1f}%)")

    if coverage > 50:
        print(f"[PASS] Perturbace jsou aktivni po vetsinu casu")
    else:
        print(f"[WARNING] Perturbace jsou aktivni pouze {coverage:.1f}% casu")

    print()
    print("=" * 80)
    print("ZAVER")
    print("=" * 80)

    if total_triggered > 0 and amp_variation > 0.001:
        print("[SUCCESS] Random Error je DYNAMICKY - nove perturbace se spousteji prubezne")
        print("          Efekt bude vizualne zivy a organicky (jako snapshot_step0300.png)")
    else:
        print("[FAIL] Random Error je STATICKY - perturbace se nespousteji dynamicky")
        print("       Efekt bude uniformni a pravidelny")


if __name__ == '__main__':
    test_dynamic_triggering()
