#!/usr/bin/env python3
"""Screenshot numbered HTML prototypes with a headless browser.

Dependencies:
  pip install playwright pillow
  python -m playwright install chromium
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validate_outputs import ValidationError, validate_html_prototypes, validate_numbered_files, validate_prototype_files


def parse_size(value: str) -> tuple[int, int]:
    normalized = value.lower().replace("*", "x")
    if normalized in {"1080p", "fullhd", "fhd"}:
        return 1920, 1080
    if "x" not in normalized:
        raise argparse.ArgumentTypeError("viewport must look like 1920x1080 or 1080p")
    width, height = normalized.split("x", 1)
    parsed = int(width), int(height)
    if parsed[0] <= 0 or parsed[1] <= 0:
        raise argparse.ArgumentTypeError("viewport dimensions must be positive")
    return parsed


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def module_path_from_html(html_file: Path, output_root: Path) -> str:
    if html_file.stem == "00-login":
        return "login"
    module_id = html_file.stem.split("-", 1)[0]
    text = html_file.read_text(encoding="utf-8", errors="ignore")
    patterns = [
        r"<meta\s+name=[\"']module[\"']\s+content=[\"'](.+?)[\"']\s*/?>",
        r"<!--\s*module\s*[:：]\s*(.+?)\s*-->",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            raw = match.group(1).strip()
            path = Path(raw)
            if not path.is_absolute():
                path = output_root / path
            return str(path.resolve())
    return str((output_root / "02.modules" / f"{module_id}.md").resolve())


def build_manifest(
    html_files: list[Path],
    output_dir: Path,
    batch_file: Path,
    viewport: tuple[int, int],
    max_retries: int,
    force: bool,
) -> dict:
    output_root = output_dir.parent
    previous_manifest: dict = {}
    previous: dict[str, dict] = {}
    if batch_file.exists() and not force:
        try:
            previous_manifest = json.loads(batch_file.read_text(encoding="utf-8"))
            previous = {item["id"]: item for item in previous_manifest.get("items", []) if "id" in item}
        except Exception:
            previous_manifest = {}
            previous = {}

    items = []
    for html_file in html_files:
        output_path = output_dir / f"{html_file.stem}.jpg"
        previous_item = previous.get(html_file.stem, {})
        html_hash = file_sha256(html_file)
        html_changed = previous_item.get("html_sha256") not in {None, html_hash}
        output_exists = output_path.exists() and output_path.stat().st_size > 0
        keep_success = (
            not force
            and not html_changed
            and previous_item.get("status") == "success"
            and output_exists
        )
        items.append(
            {
                "id": html_file.stem,
                "mode": "html",
                "module": module_path_from_html(html_file, output_root),
                "html": str(html_file.resolve()),
                "html_sha256": html_hash,
                "output": str(output_path.resolve()),
                "viewport": f"{viewport[0]}x{viewport[1]}",
                "retry": {
                    "attempts": 0,
                    "max": max_retries,
                },
                "status": "success" if keep_success else "pending",
                "error": None if keep_success else previous_item.get("error"),
                "updated_at": previous_item.get("updated_at") if keep_success else utc_now(),
            }
        )

    return {
        "version": 1,
        "mode": "html",
        "created_at": previous_manifest.get("created_at", utc_now()),
        "updated_at": utc_now(),
        "viewport": f"{viewport[0]}x{viewport[1]}",
        "html_dir": str(html_files[0].parent.resolve()) if html_files else "",
        "output_dir": str(output_dir.resolve()),
        "items": items,
    }


def save_manifest(manifest: dict, batch_file: Path) -> None:
    manifest["updated_at"] = utc_now()
    batch_file.parent.mkdir(parents=True, exist_ok=True)
    batch_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def screenshot_items(manifest: dict, batch_file: Path, viewport: tuple[int, int], wait_ms: int, force: bool) -> list[str]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return ["Missing dependency: pip install playwright && python -m playwright install chromium"]

    failures: list[str] = []
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(headless=True)
        except Exception as exc:
            return [f"Failed to launch Chromium: {exc}. Run: python -m playwright install chromium"]
        context = browser.new_context(
            viewport={"width": viewport[0], "height": viewport[1]},
            device_scale_factor=1,
            locale="zh-CN",
        )
        page = context.new_page()

        for item in manifest["items"]:
            html_path = Path(item["html"])
            output_path = Path(item["output"])
            if item["status"] == "success" and output_path.exists() and not force:
                print(f"Skipping {output_path}; manifest already marks it successful.")
                continue
            print(f"Screenshot {output_path} from {html_path} ...")
            while item["retry"]["attempts"] < item["retry"]["max"]:
                item["status"] = "running"
                item["updated_at"] = utc_now()
                save_manifest(manifest, batch_file)
                try:
                    page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
                    if wait_ms > 0:
                        page.wait_for_timeout(wait_ms)
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    page.screenshot(path=str(output_path), type="jpeg", quality=92, full_page=False)
                    item["status"] = "success"
                    item["error"] = None
                    item["updated_at"] = utc_now()
                    save_manifest(manifest, batch_file)
                    break
                except Exception as exc:
                    item["retry"]["attempts"] += 1
                    item["status"] = "failed"
                    item["error"] = str(exc)
                    item["updated_at"] = utc_now()
                    save_manifest(manifest, batch_file)
                    print(f"FAILED {html_path.name} attempt {item['retry']['attempts']}: {exc}", file=sys.stderr)
            if item["status"] != "success":
                failures.append(f"{html_path.name}: {item['error']}")

        context.close()
        browser.close()
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--html-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--module-dir", type=Path)
    parser.add_argument("--batch-file", type=Path)
    parser.add_argument("--viewport", default="1920x1080", type=parse_size)
    parser.add_argument("--wait-ms", default=500, type=int)
    parser.add_argument("--max-retries", default=2, type=int)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--no-login", action="store_true", help="Do not require a 00-login prototype")
    args = parser.parse_args()

    if args.max_retries < 1:
        print("--max-retries must be >= 1", file=sys.stderr)
        return 2

    try:
        module_dir = args.module_dir or args.html_dir.parent / "02.modules"
        html_files = validate_html_prototypes(args.html_dir, module_dir if module_dir.exists() else None, require_login=not args.no_login)
        if module_dir.exists():
            validate_numbered_files(module_dir, ".md", "modules")
    except ValidationError as exc:
        print(f"Validation failed before screenshot: {exc}", file=sys.stderr)
        return 2

    batch_file = args.batch_file or args.output_dir / "batch.json"
    manifest = build_manifest(
        html_files=html_files,
        output_dir=args.output_dir,
        batch_file=batch_file,
        viewport=args.viewport,
        max_retries=args.max_retries,
        force=args.force,
    )
    save_manifest(manifest, batch_file)

    failures = screenshot_items(manifest, batch_file, args.viewport, args.wait_ms, args.force)
    if failures:
        print("\nFailures:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    try:
        validate_prototype_files(args.output_dir, ".jpg", "prototype images", module_dir if module_dir.exists() else None, not args.no_login)
    except ValidationError as exc:
        print(f"Validation failed after screenshot: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
