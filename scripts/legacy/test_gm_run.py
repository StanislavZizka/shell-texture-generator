"""
Test script for Gierer-Meinhardt preset optimization
Usage: python -u scripts/legacy/test_gm_run.py --preset stable --K 1.0 --t_max 200 --delta_t 0.02 --size 100
"""
import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import SIMULATION_PRESETS
from services.texture_generator import TextureGeneratorService

def test_preset(preset_name, K, t_max, delta_t, size):
    """Test a specific preset with given parameters"""
    if preset_name not in SIMULATION_PRESETS:
        print(f"ERROR: Unknown preset '{preset_name}'")
        print(f"Available: {list(SIMULATION_PRESETS.keys())}")
        return

    params = SIMULATION_PRESETS[preset_name]
    print(f"\n{'='*60}")
    print(f"Testing preset: {preset_name}")
    print(f"Parameters: {params}")
    print(f"K={K}, t_max={t_max}, delta_t={delta_t}, size={size}")
    print(f"Expected steps: {int(t_max / delta_t)}")
    print(f"{'='*60}\n")

    service = TextureGeneratorService()
    image_path = service.generate_activator_inhibitor(
        K=K,
        t_max=t_max,
        delta_t=delta_t,
        color1='#0000ff',
        color2='#ff0000',
        size=size,
        params_override=params
    )

    print(f"\n{'='*60}")
    print(f"Generated: {image_path}")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test Gierer-Meinhardt presets')
    parser.add_argument('--preset', type=str, default='stable',
                        help='Preset name (stable/balanced/active/chaotic)')
    parser.add_argument('--K', type=float, default=1.0,
                        help='Reaction rate (default: 1.0)')
    parser.add_argument('--t_max', type=float, default=200,
                        help='Simulation time (default: 200)')
    parser.add_argument('--delta_t', type=float, default=0.02,
                        help='Time step (default: 0.02)')
    parser.add_argument('--size', type=int, default=100,
                        help='Texture size (default: 100)')
    parser.add_argument('--all', action='store_true',
                        help='Test all presets')

    args = parser.parse_args()

    if args.all:
        for preset in SIMULATION_PRESETS.keys():
            test_preset(preset, args.K, args.t_max, args.delta_t, args.size)
    else:
        test_preset(args.preset, args.K, args.t_max, args.delta_t, args.size)
