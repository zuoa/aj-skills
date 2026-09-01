#!/usr/bin/env python3
"""Generate numbered prototype images from prompt markdown files.

Dependencies:
  pip install google-genai pillow

Environment:
  GEMINI_API_KEY is read from --env (default: ~/aj-skills/.env) or the process env.
  GEMINI_IMAGE_MODEL or GOOGLE_IMAGE_MODEL is optional. If omitted, the script
  tries current Gemini image models and then falls back to Imagen.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validate_outputs import ValidationError, validate_numbered_files, validate_prototype_files


DEFAULT_GEMINI_MODEL = "gemini-3.1-flash-image-preview"
FALLBACK_GEMINI_MODELS = ["gemini-3-pro-image-preview", "gemini-2.5-flash-image"]
DEFAULT_IMAGEN_MODEL = "imagen-4.0-generate-001"


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def parse_size(value: str) -> tuple[int, int]:
    normalized = value.lower().replace("*", "x")
    if normalized in {"1080p", "fullhd", "fhd"}:
        return 1920, 1080
    if "x" not in normalized:
        raise argparse.ArgumentTypeError("size must look like 1920x1080 or 1080p")
    width, height = normalized.split("x", 1)
    parsed = int(width), int(height)
    if parsed[0] <= 0 or parsed[1] <= 0:
        raise argparse.ArgumentTypeError("size dimensions must be positive")
    return parsed


def aspect_ratio_from_size(size: tuple[int, int]) -> str:
    width, height = size
    ratio = width / height
    common = {
        "16:9": 16 / 9,
        "9:16": 9 / 16,
        "4:3": 4 / 3,
        "3:4": 3 / 4,
        "1:1": 1,
    }
    return min(common, key=lambda key: abs(common[key] - ratio))


def image_size_label(size: tuple[int, int]) -> str:
    return "2K" if max(size) >= 1500 else "1K"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def prompt_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def module_path_from_prompt(prompt_file: Path, output_root: Path) -> str:
    if prompt_file.stem == "00-login":
        return "login"
    module_id = prompt_file.stem.split("-", 1)[0]
    text = prompt_file.read_text(encoding="utf-8")
    match = re.search(r"^对应模块\s*[:：]\s*(.+?)\s*$", text, flags=re.MULTILINE)
    if match:
        raw = match.group(1).strip().strip("`")
        path = Path(raw)
        if not path.is_absolute():
            path = output_root / path
        return str(path.resolve())
    return str((output_root / "02.modules" / f"{module_id}.md").resolve())


def build_manifest(
    prompt_files: list[Path],
    output_dir: Path,
    batch_file: Path,
    size: tuple[int, int],
    models: list[str],
    max_retries: int,
    force: bool,
) -> dict:
    output_root = output_dir.parent
    previous_manifest: dict = {}
    previous: dict[str, dict] = {}
    if batch_file.exists() and not force:
        try:
            data = json.loads(batch_file.read_text(encoding="utf-8"))
            previous_manifest = data
            previous = {item["id"]: item for item in data.get("items", []) if "id" in item}
        except Exception:
            previous = {}

    items = []
    for prompt_file in prompt_files:
        output_path = output_dir / f"{prompt_file.stem}.jpg"
        previous_item = previous.get(prompt_file.stem, {})
        prompt_hash = prompt_sha256(prompt_file)
        prompt_changed = previous_item.get("prompt_sha256") not in {None, prompt_hash}
        output_exists = output_path.exists() and output_path.stat().st_size > 0
        keep_success = (
            not force
            and not prompt_changed
            and previous_item.get("status") == "success"
            and output_exists
        )
        item = {
            "id": prompt_file.stem,
            "module": module_path_from_prompt(prompt_file, output_root),
            "prompt": str(prompt_file.resolve()),
            "prompt_sha256": prompt_hash,
            "output": str(output_path.resolve()),
            "retry": {
                "attempts": 0,
                "max": max_retries,
            },
            "status": "success" if keep_success else "pending",
            "error": None if keep_success else previous_item.get("error"),
            "updated_at": previous_item.get("updated_at") if keep_success else utc_now(),
        }
        items.append(item)

    return {
        "version": 1,
        "created_at": previous_manifest.get("created_at", utc_now()),
        "updated_at": utc_now(),
        "size": f"{size[0]}x{size[1]}",
        "aspect_ratio": aspect_ratio_from_size(size),
        "models": models,
        "prompt_dir": str(prompt_files[0].parent.resolve()) if prompt_files else "",
        "output_dir": str(output_dir.resolve()),
        "items": items,
    }


def save_manifest(manifest: dict, batch_file: Path) -> None:
    manifest["updated_at"] = utc_now()
    batch_file.parent.mkdir(parents=True, exist_ok=True)
    batch_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def extract_image_bytes(response: object) -> bytes:
    generated_images = getattr(response, "generated_images", None)
    if generated_images:
        for generated in generated_images:
            image = getattr(generated, "image", generated)
            for attr in ("image_bytes", "data", "bytes"):
                value = getattr(image, attr, None)
                if value:
                    return base64.b64decode(value) if isinstance(value, str) else value

    candidates = getattr(response, "candidates", None) or []
    for candidate in candidates:
        content = getattr(candidate, "content", None)
        parts = getattr(content, "parts", None) or []
        for part in parts:
            inline_data = getattr(part, "inline_data", None)
            if inline_data and getattr(inline_data, "data", None):
                data = inline_data.data
                return base64.b64decode(data) if isinstance(data, str) else data

    parts = getattr(response, "parts", None) or []
    for part in parts:
        inline_data = getattr(part, "inline_data", None)
        if inline_data and getattr(inline_data, "data", None):
            data = inline_data.data
            return base64.b64decode(data) if isinstance(data, str) else data

    raise RuntimeError("Google API response did not contain image bytes")


def gemini_generate_content_config(types: object, aspect_ratio: str, size: tuple[int, int], model: str) -> object:
    image_options = {"aspect_ratio": aspect_ratio}
    if model.startswith("gemini-3"):
        image_options["image_size"] = image_size_label(size)

    for response_modalities in (["Image"], ["IMAGE"]):
        try:
            return types.GenerateContentConfig(
                response_modalities=response_modalities,
                response_format={"image": image_options},
            )
        except TypeError:
            pass

    try:
        image_config = types.ImageConfig(
            aspect_ratio=aspect_ratio,
            image_size=image_size_label(size),
        )
        return types.GenerateContentConfig(response_modalities=["Image"], image_config=image_config)
    except Exception:
        return types.GenerateContentConfig(response_modalities=["Image"])


def call_google_image_api(client: object, types: object, prompt: str, models: list[str], size: tuple[int, int]) -> bytes:
    last_error: Exception | None = None
    aspect_ratio = aspect_ratio_from_size(size)
    for model in models:
        try:
            if model.startswith("imagen"):
                config = types.GenerateImagesConfig(number_of_images=1, aspect_ratio=aspect_ratio)
                response = client.models.generate_images(model=model, prompt=prompt, config=config)
            else:
                config = gemini_generate_content_config(types, aspect_ratio, size, model)
                response = client.models.generate_content(
                    model=model,
                    contents=[prompt],
                    config=config,
                )
            return extract_image_bytes(response)
        except Exception as exc:  # Keep trying fallback models when available.
            last_error = exc
    raise RuntimeError(f"All image models failed. Last error: {last_error}") from last_error


def save_jpeg(image_bytes: bytes, output_path: Path, size: tuple[int, int]) -> None:
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("Pillow is required to resize and save JPG files: pip install pillow") from exc

    target_w, target_h = size
    with Image.open(BytesIO(image_bytes)) as image:
        image = image.convert("RGB")
        scale = max(target_w / image.width, target_h / image.height)
        resized_w = max(target_w, round(image.width * scale))
        resized_h = max(target_h, round(image.height * scale))
        resample = getattr(getattr(Image, "Resampling", Image), "LANCZOS")
        image = image.resize((resized_w, resized_h), resample)
        left = (resized_w - target_w) // 2
        top = (resized_h - target_h) // 2
        image = image.crop((left, top, left + target_w, top + target_h))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path, "JPEG", quality=92, optimize=True)


def build_prompt(raw_prompt: str, size: tuple[int, int]) -> str:
    width, height = size
    guardrails = f"""

Render as a polished product UI screenshot, {width}x{height}, 16:9.
Use clear Chinese interface labels, realistic data, readable text, stable spacing,
and no overlapping UI elements. Do not add watermarks or explanatory captions.
"""
    return raw_prompt.strip() + guardrails


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--module-dir", type=Path)
    parser.add_argument("--batch-file", type=Path)
    parser.add_argument("--env", default="~/aj-skills/.env", type=Path)
    parser.add_argument("--size", default="1920x1080", type=parse_size)
    parser.add_argument("--max-retries", default=3, type=int)
    parser.add_argument("--force", action="store_true", help="Regenerate all images and reset manifest status")
    parser.add_argument("--no-login", action="store_true", help="Do not require a 00-login prototype")
    parser.add_argument("--sleep", default=1.0, type=float, help="Seconds to pause between API calls")
    args = parser.parse_args()
    if args.max_retries < 1:
        print("--max-retries must be >= 1", file=sys.stderr)
        return 2

    load_env_file(args.env.expanduser())
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Missing GEMINI_API_KEY. Add it to ~/aj-skills/.env or export it.", file=sys.stderr)
        return 2

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("Missing dependency: pip install google-genai pillow", file=sys.stderr)
        return 2

    explicit_model = os.environ.get("GEMINI_IMAGE_MODEL") or os.environ.get("GOOGLE_IMAGE_MODEL")
    models = [explicit_model] if explicit_model else [DEFAULT_GEMINI_MODEL, *FALLBACK_GEMINI_MODELS, DEFAULT_IMAGEN_MODEL]
    client = genai.Client(api_key=api_key)

    try:
        module_dir = args.module_dir or args.prompt_dir.parent / "02.modules"
        prompt_files = validate_prototype_files(args.prompt_dir, ".md", "prototype prompts", module_dir if module_dir.exists() else None, not args.no_login)
        if module_dir.exists():
            validate_numbered_files(module_dir, ".md", "modules")
    except ValidationError as exc:
        print(f"Validation failed before generation: {exc}", file=sys.stderr)
        return 2

    batch_file = args.batch_file or args.output_dir / "batch.json"
    manifest = build_manifest(
        prompt_files=prompt_files,
        output_dir=args.output_dir,
        batch_file=batch_file,
        size=args.size,
        models=models,
        max_retries=args.max_retries,
        force=args.force,
    )
    save_manifest(manifest, batch_file)

    failures: list[str] = []
    for item in manifest["items"]:
        prompt_file = Path(item["prompt"])
        output_path = Path(item["output"])
        if item["status"] == "success" and output_path.exists() and not args.force:
            print(f"Skipping {output_path}; manifest already marks it successful.")
            continue
        raw_prompt = prompt_file.read_text(encoding="utf-8")
        prompt = build_prompt(raw_prompt, args.size)
        print(f"Generating {output_path} from {prompt_file} ...")
        while item["retry"]["attempts"] < item["retry"]["max"]:
            item["status"] = "running"
            item["updated_at"] = utc_now()
            save_manifest(manifest, batch_file)
            try:
                image_bytes = call_google_image_api(client, types, prompt, models, args.size)
                save_jpeg(image_bytes, output_path, args.size)
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
                print(f"FAILED {prompt_file.name} attempt {item['retry']['attempts']}: {exc}", file=sys.stderr)
                if item["retry"]["attempts"] < item["retry"]["max"]:
                    time.sleep(max(args.sleep, 0))
        if item["status"] != "success":
            failures.append(f"{prompt_file.name}: {item['error']}")
        time.sleep(max(args.sleep, 0))

    if failures:
        print("\nFailures:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    try:
        validate_prototype_files(args.output_dir, ".jpg", "prototype images", module_dir if module_dir.exists() else None, not args.no_login)
    except ValidationError as exc:
        print(f"Validation failed after generation: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
