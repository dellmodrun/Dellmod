"""Build ``data.json`` for the dashboard.

Usage::

    python -m engine.pipeline            # writes ./data.json
    python -m engine.pipeline --out web  # writes web/data.json
"""
from __future__ import annotations

import argparse
import json
import os

from . import network


def build(out_dir: str = ".") -> str:
    snapshot = network.build_snapshot()
    path = os.path.join(out_dir, "data.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(snapshot, fh, indent=2, ensure_ascii=False)
    return path


def main() -> None:
    ap = argparse.ArgumentParser(description="Build Dellmod dashboard telemetry")
    ap.add_argument("--out", default=".", help="output directory (default: cwd)")
    args = ap.parse_args()
    path = build(args.out)
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
