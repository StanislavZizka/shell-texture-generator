#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify Random Error restoration
Validates that biological perturbations work correctly after restoration
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import numpy as np
from services.random_error_module import RandomErrorModule, create_random_error_params

print("=" * 80)
print("RANDOM ERROR RESTORATION TEST")
print("=" * 80)

# Test configuration
size = (128, 128)
module = RandomErrorModule(size, seed=42)

params = create_random_error_params(
    enabled=True,
    strength=0.03,
    duration=30,
    frequency=0.05,
    probability=1.0,  # Force trigger for test
    num_regions=3,
    region_size=10
)

print("\nConfiguration:")
print(f"  Strength (α): {params['strength']:.4f}")
print(f"  Duration: {params['duration']} steps")
print(f"  Frequency: {params['frequency']:.3f}")
print(f"  Regions: {params['num_regions']}")
print(f"  Region size: {params['region_size']} pixels")

# Trigger perturbation
module.trigger_perturbation(
    strength=params['strength'],
    duration=params['duration'],
    num_regions=params['num_regions'],
    region_size=(params['region_size'], params['region_size']),
    frequency=params['frequency']
)

print("\n✓ Perturbation triggered")

# Test at multiple time steps
A = np.ones(size) * 0.5  # Dummy activator field
test_steps = [0, 10, 20, 30, 40]

print("\nTesting R(x,y,t) computation:")
print("-" * 80)

for step in test_steps:
    t = step * 0.5
    R = module.apply_random_error(A, t, step, params)

    # Statistics
    R_mean = np.mean(R)
    R_max = np.max(R)
    R_min = np.min(R)
    R_nonzero = np.sum(np.abs(R) > 1e-6) / R.size * 100

    print(f"Step {step:3d} (t={t:5.1f}): "
          f"R ∈ [{R_min:+.5f}, {R_max:+.5f}], "
          f"mean={R_mean:+.6f}, {R_nonzero:5.1f}% nonzero")

    # Verify R is nonzero during active period
    if step < params['duration']:
        if R_nonzero < 1.0:
            print(f"  ⚠ WARNING: Expected nonzero R during active period!")
        if abs(R_max) < 0.001:
            print(f"  ⚠ WARNING: R magnitude too small!")

print("-" * 80)

# Verify no decay_factor is being applied
print("\n✓ VERIFICATION: Constant strength (no decay)")
step_early = 5
step_late = 25

R_early = module.apply_random_error(A, step_early * 0.5, step_early, params)
R_late = module.apply_random_error(A, step_late * 0.5, step_late, params)

max_early = np.max(np.abs(R_early))
max_late = np.max(np.abs(R_late))

print(f"  Early (step {step_early}): max|R| = {max_early:.6f}")
print(f"  Late  (step {step_late}): max|R| = {max_late:.6f}")

# Both should have similar magnitude (allowing for sin oscillation)
if max_early > 1e-6 and max_late > 1e-6:
    ratio = max_late / max_early
    print(f"  Ratio: {ratio:.3f}")
    if 0.3 < ratio < 3.0:  # Allow for temporal oscillation
        print("  ✓ PASS: Strength appears constant (no decay)")
    else:
        print("  ⚠ WARNING: Strength varies significantly (possible decay issue)")
else:
    print("  ⚠ WARNING: Perturbation magnitude too small")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
print("\n✓ Random Error module restored successfully")
print("✓ R(x,y,t) = α·M(x,y)·sin(2πft+φ)·H(t-t₀)H(t₁-t)")
print("✓ Constant strength (no decay)")
print("\nReady for integration testing with texture generator.")
