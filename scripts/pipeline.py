#!/usr/bin/env python3
"""Rebuild listings and the static site.

  python3 scripts/pipeline.py           # listings + site from data/raw
  python3 scripts/pipeline.py --fetch   # download sources first
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(script: str):
    subprocess.check_call([sys.executable, str(ROOT / "scripts" / script)], cwd=ROOT)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch", action="store_true", help="Download public source files before rebuilding")
    args = parser.parse_args()
    if args.fetch:
        run("fetch_sources.py")
    run("build_listings.py")
    run("build_site.py")


if __name__ == "__main__":
    main()
