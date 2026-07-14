#!/usr/bin/env python3
"""Create or refresh reference docx template via pandoc (through pypandoc)."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate templates/cnipa-reference.docx from pandoc default reference")
    p.add_argument("--output", default="templates/cnipa-reference.docx", help="Output path")
    p.add_argument("--overwrite", action="store_true", help="Overwrite existing template")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    if output.exists() and not args.overwrite:
        print(f"Skip: template already exists: {output}")
        return 0

    try:
        import pypandoc
    except Exception as e:
        print(f"pypandoc unavailable: {e}")
        return 2

    try:
        pandoc_bin = pypandoc.get_pandoc_path()
    except Exception as e:
        print(f"pandoc unavailable: {e}")
        return 2

    try:
        proc = subprocess.run(
            [pandoc_bin, "--print-default-data-file=reference.docx"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        output.write_bytes(proc.stdout)
        print(f"Generated: {output}")
        print("Note: this is pandoc default reference. Replace it if you need stricter CNIPA typography.")
        return 0
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode("utf-8", errors="ignore")
        print(f"Failed to generate reference template: {stderr.strip()}")
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
