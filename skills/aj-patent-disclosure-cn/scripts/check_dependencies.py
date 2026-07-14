#!/usr/bin/env python3
"""Preflight dependency checks for patent disclosure skill."""

from __future__ import annotations

import argparse
import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


def has_python_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def has_binary(name: str) -> bool:
    return shutil.which(name) is not None


def run_pandoc_probe() -> bool:
    try:
        subprocess.run(["pandoc", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False


def check_docx(strict_cnipa: bool = True) -> List[Tuple[str, str, bool, str]]:
    rows: List[Tuple[str, str, bool, str]] = []
    rows.append(("python module", "pypandoc", has_python_module("pypandoc"), "pip install pypandoc"))
    rows.append(("system binary", "pandoc", has_binary("pandoc") and run_pandoc_probe(), "brew install pandoc"))
    if strict_cnipa:
        tpl = Path("templates/cnipa-reference.docx")
        rows.append(("file", str(tpl), tpl.exists(), "python scripts/create_cnipa_reference_doc.py"))
    return rows


def check_figures() -> List[Tuple[str, str, bool, str]]:
    rows: List[Tuple[str, str, bool, str]] = []
    rows.append(("python module", "matplotlib", has_python_module("matplotlib"), "pip install matplotlib"))
    rows.append(("system binary(optional)", "mmdc", has_binary("mmdc"), "npm install -g @mermaid-js/mermaid-cli"))
    return rows


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Check runtime dependencies before running skill scripts")
    p.add_argument("--task", choices=["docx", "figures", "all"], default="all")
    p.add_argument("--strict", action="store_true", help="Exit non-zero if required dependencies are missing")
    return p.parse_args()


def print_rows(title: str, rows: List[Tuple[str, str, bool, str]]) -> int:
    print(f"\n[{title}]")
    missing_required = 0
    for kind, name, ok, fix in rows:
        optional = "optional" in kind
        status = "PASS" if ok else ("WARN" if optional else "FAIL")
        print(f"- {status:4} | {kind:17} | {name}")
        if not ok:
            print(f"        fix: {fix}")
            if not optional:
                missing_required += 1
    return missing_required


def main() -> int:
    args = parse_args()
    missing_required = 0

    if args.task in ("docx", "all"):
        missing_required += print_rows("DOCX", check_docx(strict_cnipa=True))

    if args.task in ("figures", "all"):
        missing_required += print_rows("FIGURES", check_figures())

    if missing_required == 0:
        print("\nDependency check passed.")
        return 0

    print(f"\nDependency check found {missing_required} missing required item(s).")
    return 2 if args.strict else 0


if __name__ == "__main__":
    raise SystemExit(main())
