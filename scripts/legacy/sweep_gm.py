"""Legacy Gierer-Meinhardt sweep helper."""

from __future__ import annotations

import contextlib
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.texture_generator import TextureGeneratorService
from config import SIMULATION_PARAMS, IMAGES_DIR


def run_one(s: float, D_b: float, t_max: float, delta_t: float, size: int,
            color1: str = '#0000ff', color2: str = '#ff0000') -> str:
    # Lock B-centered fixed params while sweeping s and D_b
    SIMULATION_PARAMS.update({
        's': s,
        'D_b': D_b,
        'r_b': 0.08,
        'b_b': 0.0022,
        'B0': 0.45,
    })

    svc = TextureGeneratorService()
    with contextlib.redirect_stdout(open(os.devnull, 'w')):
        path = svc.generate_activator_inhibitor(
            K=1.0,
            t_max=t_max,
            delta_t=delta_t,
            color1=color1,
            color2=color2,
            size=size,
        )

    # Move/rename output with parameters in filename
    base = f"activator_inhibitor_s{str(s).replace('.', '_')}_Db{str(D_b).replace('.', '_')}_t{int(t_max)}.png"
    dst = Path(IMAGES_DIR) / base
    os.replace(path, dst)
    print(f"Saved: {dst}")
    return str(dst)


def main():
    combos = [(0.11, 0.30), (0.11, 0.32), (0.115, 0.30), (0.115, 0.32)]

    # Short verification run to see early behavior (optional; PNGs still created)
    for s, Db in combos:
        print(f"=== Short run for s={s}, D_b={Db} (t_max=250) ===")
        run_one(s=s, D_b=Db, t_max=250.0, delta_t=0.025, size=100)

    # Final renders for thesis (t_max=400)
    for s, Db in combos:
        print(f"=== Final render for s={s}, D_b={Db} (t_max=400) ===")
        run_one(s=s, D_b=Db, t_max=400.0, delta_t=0.025, size=100)


if __name__ == '__main__':
    main()
