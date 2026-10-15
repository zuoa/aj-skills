#!/usr/bin/env python3
"""Check browser-measured rectangles. Geometry checks do not certify visual quality."""
import argparse
import json
import math
import sys
from pathlib import Path


def inside(a, b, tolerance=1.0):
    return a['x'] >= b['x'] - tolerance and a['y'] >= b['y'] - tolerance and a['x'] + a['width'] <= b['x'] + b['width'] + tolerance and a['y'] + a['height'] <= b['y'] + b['height'] + tolerance


def overlap(a, b, tolerance=1.0):
    return min(a['x'] + a['width'], b['x'] + b['width']) - max(a['x'], b['x']) > tolerance and min(a['y'] + a['height'], b['y'] + b['height']) - max(a['y'], b['y']) > tolerance


def check_snapshot(snapshot):
    issues = []
    for view in snapshot.get('viewports', []):
        label = f'{view["width"]}x{view["height"]}'
        items = {item['id']: item for item in view['elements']}
        if len(items) != len(view['elements']):
            issues.append(f'{label}: duplicate element ID')
        invalid = False
        for item in items.values():
            rect = item['rect']
            if any(not isinstance(rect.get(k), (int, float)) or not math.isfinite(rect[k]) for k in ['x', 'y', 'width', 'height']) or rect['width'] < 0 or rect['height'] < 0:
                issues.append(f'{label}: invalid rectangle {item["id"]}')
                invalid = True
            if item.get('clipped'):
                issues.append(f'{label}: clipped content {item["id"]}')
        if invalid:
            continue
        for relation in view.get('relations', []):
            a, b = items.get(relation['a']), items.get(relation['b'])
            if a is None or b is None:
                issues.append(f'{label}: missing relation target {relation}')
                continue
            kind = relation['kind']
            if kind == 'contains' and not inside(b['rect'], a['rect']):
                issues.append(f'{label}: {b["id"]} escapes {a["id"]}')
            elif kind == 'separate' and overlap(a['rect'], b['rect']):
                issues.append(f'{label}: overlap {a["id"]} / {b["id"]}')
            elif kind not in {'contains', 'separate'}:
                issues.append(f'{label}: unknown relation {kind}')
    if not snapshot.get('viewports'):
        issues.append('No measured viewports')
    return issues


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('snapshot', type=Path, help='JSON with viewports, measured elements and explicit contains/separate relations')
    args = parser.parse_args()
    try:
        snapshot = json.loads(args.snapshot.read_text())
        issues = check_snapshot(snapshot)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f'Invalid visual snapshot: {error}\n')
    if issues:
        for issue in issues:
            print(f'FAIL: {issue}', file=sys.stderr)
        sys.exit(1)
    print(f'PASS: {len(snapshot["viewports"])} measured viewports; explicit internal containment and overlap checks')
