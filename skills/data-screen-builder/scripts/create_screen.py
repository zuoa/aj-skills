#!/usr/bin/env python3
"""Copy the bundled starter to a NEW directory without installed/build artifacts."""
import argparse
import json
import shutil
from pathlib import Path


def create_screen(destination: Path, layout: str | None = None, palette: str | None = None, title: str | None = None, style: str | None = None) -> Path:
    source = Path(__file__).resolve().parents[1] / 'assets' / 'vue-screen'
    destination = destination.expanduser().absolute()
    if source == destination or source in destination.resolve().parents:
        raise ValueError('Target must be outside the bundled template directory.')
    if destination.exists():
        raise FileExistsError(f'Target already exists: {destination}; merge existing projects explicitly.')
    # Validate requested choices before creating anything. Custom choices are authored after the interview.
    for selected, library in [(layout, 'layouts'), (palette, 'palettes'), (style, 'styles')]:
        choices = json.loads((source / f'src/config/{library}.json').read_text())['presets']
        if selected is not None and selected not in {item['id'] for item in choices}:
            raise ValueError(f'Unknown {library} choice: {selected}; available: {", ".join(item["id"] for item in choices)}')
    if title is not None and not title.strip():
        raise ValueError('Title cannot be empty.')
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns(
        'node_modules', 'dist', '.env.local', '.env.*.local', 'test-results', 'playwright-report', '__pycache__'))
    path = destination / 'src/config/framework.json'
    frame = json.loads(path.read_text())
    if layout:
        frame['layoutId'] = layout
        if layout == 'panorama-wide':
            frame['canvas'] = {'width': 3840, 'height': 1080}
    if palette:
        frame['paletteId'] = palette
    if style:
        frame['styleId'] = style
    if title:
        frame['title'] = title
    path.write_text(json.dumps(frame, ensure_ascii=False, indent=2) + '\n')
    workflow = source.parent / 'workflow'
    shutil.copy2(workflow / 'brief.template.json', destination / 'screen-brief.json')
    shutil.copy2(workflow / 'acceptance.template.md', destination / 'acceptance.md')
    return destination


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    parser.add_argument('--layout', help='Preset ID; custom layouts are authored in framework.json after discussion')
    parser.add_argument('--palette', help='Independent palette preset ID')
    parser.add_argument('--style', help='Independent visual style preset ID')
    parser.add_argument('--title', help='Theme title shown in the empty framework')
    args = parser.parse_args()
    try:
        print(f'Created: {create_screen(args.destination, args.layout, args.palette, args.title, args.style)}')
        print('Next: npm ci; npm run validate:framework; npm run dev:framework')
        print('After framework confirmation, populate content and framework.bindings, then validate, test and build.')
    except (OSError, ValueError, shutil.Error) as error:
        parser.exit(1, f'{error}\n')
