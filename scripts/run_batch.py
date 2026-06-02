"""CLI entry point for reproducible batch mode runs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.batch import BatchRunner, build_default_reproducibility_targets


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the three core shell texture modes.")
    parser.add_argument(
        "--size",
        type=int,
        default=128,
        help="Texture size used for the batch suite.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for JSON batch summaries.",
    )
    parser.add_argument(
        "--summary-name",
        type=str,
        default=None,
        help="Optional explicit filename for the summary JSON.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    runner = BatchRunner(output_dir=args.output_dir)
    targets = build_default_reproducibility_targets(size=args.size)
    results = runner.run(targets)
    summary_path = runner.write_summary(results, filename=args.summary_name)

    print(json.dumps({"summary_path": str(summary_path), "runs": [result.to_dict() for result in results]}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
