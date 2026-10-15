#!/usr/bin/env python3
"""Read-only JSON Schema and semantic checks; never executes project code."""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def validate_framework(project: Path, screen: dict | None = None) -> list[str]:
    """Validate structural inputs without loading metrics or executing project code."""
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        return ['Missing jsonschema; install with: python3 -m pip install jsonschema']
    schema_path = Path(__file__).resolve().parents[1] / 'assets/vue-screen/src/display/framework.schema.json'
    schema = json.loads(schema_path.read_text())
    try:
        frame, layouts, palettes = [json.loads((project / f'src/config/{name}.json').read_text()) for name in ['framework', 'layouts', 'palettes']]
        style_path = project / 'src/config/styles.json'
        styles = json.loads((style_path if style_path.exists() else schema_path.parent.parent / 'config/styles.json').read_text())
        errors = []
        if not isinstance(frame, dict) or any(not isinstance(lib, dict) or not isinstance(lib.get('presets'), list) for lib in [layouts, palettes, styles]):
            return ['framework: expected a frame object and preset libraries']
        for kind, items in [('frame', [frame]), ('layout', layouts['presets']), ('palette', palettes['presets']), ('style', styles['presets'])]:
            validator = Draft202012Validator(dict(schema, **{'$ref': f'#/$defs/{kind}'}))
            for item in items:
                errors.extend(f'framework {kind}: {e.message}' for e in validator.iter_errors(item))
        if errors:
            return errors
        for kind, library in [('layout', layouts), ('palette', palettes), ('style', styles)]:
            if library.get('version') != '1':
                errors.append(f'framework: invalid {kind} library version')
            ids = [item['id'] for item in library['presets']]
            if len(set(ids)) != len(ids) or 'custom' in ids:
                errors.append(f'framework: duplicate or reserved {kind} ID')
        for kind in ['Layout', 'Palette', 'Style']:
            if f'custom{kind}' in frame:
                item = frame[f'custom{kind}']
                validator = Draft202012Validator(dict(schema, **{'$ref': f'#/$defs/{kind.lower()}'}))
                custom_errors = [f'framework custom{kind}: {e.message}' for e in validator.iter_errors(item)]
                errors.extend(custom_errors)
                if custom_errors:
                    continue
                if item.get('id') != 'custom':
                    errors.append(f'framework: custom{kind}.id must be custom')
        if errors:
            return errors
        layout = frame.get('customLayout') if frame['layoutId'] == 'custom' else next((p for p in layouts['presets'] if p['id'] == frame['layoutId']), None)
        palette = frame.get('customPalette') if frame['paletteId'] == 'custom' else next((p for p in palettes['presets'] if p['id'] == frame['paletteId']), None)
        if not layout or not palette:
            return ['framework: unknown layout or palette']
        style_id = frame.get('styleId') or ('command-hud' if frame.get('visualStyle') == 'cinematic' else 'editorial-light')
        style = frame.get('customStyle') if style_id == 'custom' else next((p for p in styles['presets'] if p['id'] == style_id), None)
        if not style:
            return [f'framework: unknown style {style_id}']
        for current in layouts['presets'] + ([frame['customLayout']] if 'customLayout' in frame else []):
            slots = current['slots']
            if len({s['id'] for s in slots}) != len(slots):
                errors.append('framework: duplicate slot ID')
            for slot in slots:
                r = slot['layout']
                if r['col'] + r['width'] > 13 or r['row'] + r['height'] > current['rows'] + 1:
                    errors.append(f'framework: slot {slot["id"]} exceeds grid')
            for i, a in enumerate(slots):
                for b in slots[i + 1:]:
                    x, y = a['layout'], b['layout']
                    if x['col'] < y['col'] + y['width'] and y['col'] < x['col'] + x['width'] and x['row'] < y['row'] + y['height'] and y['row'] < x['row'] + x['height']:
                        errors.append(f'framework: overlapping slots {a["id"]}, {b["id"]}')
        if screen is not None and frame['bindings']:
            bindings = frame['bindings']
            if set(bindings) != {b['id'] for b in screen['components']}:
                errors.append('framework: bindings must cover every component exactly once')
            if len(set(bindings.values())) != len(bindings):
                errors.append('framework: duplicate binding')
            slots = {s['id']: s for s in layout['slots']}
            if set(bindings.values()) != set(slots):
                errors.append('framework: unknown or unfilled slots')
            for b in screen['components']:
                slot = slots.get(bindings.get(b['id']))
                if slot and ((b['type'] == 'map') != (slot['role'] == 'map')):
                    errors.append(f'framework: map role mismatch for {b["id"]}')
                if slot and slot['role'] == 'metric' and b['type'] not in ['metric', 'status']:
                    errors.append(f'framework: metric role mismatch for {b["id"]}')
        return errors
    except (OSError, ValueError, KeyError, TypeError) as error:
        return [f'framework: {error}']


def validate(project: Path) -> list[str]:
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ImportError:
        return ['Missing jsonschema; install with: python3 -m pip install jsonschema']
    schema = json.loads((Path(__file__).resolve().parents[1] / 'assets/vue-screen/src/contracts/contract.schema.json').read_text())
    errors = []
    documents = {}
    for kind, name in [('catalog', 'metrics'), ('screen', 'screen')]:
        try:
            documents[kind] = json.loads((project / f'src/config/{name}.json').read_text())
        except (OSError, ValueError) as error:
            errors.append(f'{name}: {error}')
            continue
        selected = dict(schema, **{'$ref': f'#/$defs/{kind}'})
        for error in Draft202012Validator(selected, format_checker=FormatChecker()).iter_errors(documents[kind]):
            errors.append(f'{name}/{"/".join(map(str, error.absolute_path))}: {error.message}')
    if errors:
        return errors
    if (project / 'src/config/framework.json').exists():
        errors.extend(validate_framework(project, documents['screen']))
        if errors:
            return errors
    try:
        manifest = json.loads((project / 'src/config/component-types.json').read_text())
        types = manifest['builtin'] + manifest['custom']
        if not isinstance(types, list) or not all(isinstance(t, str) for t in types):
            raise ValueError('component type lists must contain strings')
    except (OSError, ValueError, KeyError, TypeError) as error:
        return [f'component-types: {error}']

    catalog, screen = documents['catalog'], documents['screen']
    metrics = {m['id']: m for m in catalog['metrics']}
    if len(metrics) != len(catalog['metrics']):
        errors.append('duplicate metric ID')
    for metric in metrics.values():
        names = [f['name'] for f in metric['dimensions']]
        if len(set(names)) != len(names) or set(names) & {'time', 'value'}:
            errors.append(f'{metric["id"]}: duplicate or reserved dimension')
        if metric['staleAfterMs'] < metric['refreshMs']:
            errors.append(f'{metric["id"]}: staleAfterMs must be >= refreshMs')

    def fields(query):
        metric = metrics[query['metricId']]
        dimensions = {f['name']: f['type'] for f in metric['dimensions']}
        return dict({name: dimensions[name] for name in query['dimensions']}, **({'time': 'timestamp'} if query['granularity'] != 'none' else {}), value='number')

    for key, query in screen['queries'].items():
        metric = metrics.get(query['metricId'])
        if not metric:
            errors.append(f'{key}: unknown metric'); continue
        dimensions = {f['name']: f['type'] for f in metric['dimensions']}
        if set(query['dimensions']) - dimensions.keys() or query['filters'].keys() - dimensions.keys():
            errors.append(f'{key}: unsupported dimension'); continue
        if query['granularity'] not in metric['granularities']:
            errors.append(f'{key}: unsupported granularity')
        window = query['timeRange']
        if datetime.fromisoformat(window['from']) >= datetime.fromisoformat(window['to']):
            errors.append(f'{key}: invalid time range')
        try:
            ZoneInfo(window['timezone'])
        except (ZoneInfoNotFoundError, ValueError):
            errors.append(f'{key}: invalid timezone')
        for name, raw in query['filters'].items():
            values = raw if isinstance(raw, list) else [raw]
            kind = dimensions[name]
            def valid(value):
                if value is None:
                    return True
                if kind == 'number':
                    return isinstance(value, (int, float)) and not isinstance(value, bool)
                if kind == 'boolean':
                    return isinstance(value, bool)
                if kind == 'timestamp':
                    return isinstance(value, str) and FormatChecker().conforms(value, 'date-time')
                return isinstance(value, str)
            if not all(valid(value) for value in values):
                errors.append(f'{key}: invalid filter type {name}')
        if query.get('orderBy', {}).get('field', 'value') not in fields(query):
            errors.append(f'{key}: unknown orderBy field')
    if errors:
        return errors

    ids = [b['id'] for b in screen['components']]
    if len(set(ids)) != len(ids):
        errors.append('duplicate component ID')
    required = {'metric': ['value'], 'trend': ['x', 'value'], 'ranking': ['label', 'value'], 'composition': ['label', 'value'], 'heatmap': ['x', 'y', 'value'], 'map': ['label', 'value'], 'status': ['value'], 'alerts': ['label']}
    for binding in screen['components']:
        prefix = binding['id']
        query = screen['queries'].get(binding['queryId'])
        if not query:
            errors.append(f'{prefix}: unknown queryId'); continue
        available = fields(query)
        if binding['type'] not in types:
            errors.append(f'{prefix}: unregistered component')
        for role in required.get(binding['type'], []):
            if role not in binding['fields']:
                errors.append(f'{prefix}: missing {role} binding')
        for role, name in binding['fields'].items():
            if name not in available:
                errors.append(f'{prefix}: unknown field {name}')
            elif role in {'value', 'longitude', 'latitude'} and available[name] != 'number':
                errors.append(f'{prefix}: {role} requires number')
        interaction = binding.get('interaction')
        if interaction:
            if interaction['field'] not in available:
                errors.append(f'{prefix}: unknown interaction field')
            for target in screen['queries'].values():
                if interaction['filter'] not in {d['name'] for d in metrics[target['metricId']]['dimensions']}:
                    errors.append(f'{prefix}: interaction filter unsupported by {target["metricId"]}')
        threshold = binding.get('thresholds')
        geo = binding.get('geography')
        if geo:
            if binding['type'] != 'map':
                errors.append(f'{prefix}: geography requires map component')
            if geo.get('basemap') and geo['basemap']['coordinateSystem'] != geo['coordinateSystem']:
                errors.append(f'{prefix}: basemap coordinate system mismatch')
            if any(layer['coordinateSystem'] != geo['coordinateSystem'] for layer in geo.get('overlays', [])):
                errors.append(f'{prefix}: overlay coordinate system mismatch')
        if threshold and ((threshold['direction'] == 'above' and threshold['warning'] > threshold['critical']) or (threshold['direction'] == 'below' and threshold['warning'] < threshold['critical'])):
            errors.append(f'{prefix}: invalid threshold order')
        layout = binding['layout']
        if layout['col'] + layout['width'] > 13:
            errors.append(f'{prefix}: layout exceeds 12 columns')
    for i, a in enumerate(screen['components']):
        for b in screen['components'][i + 1:]:
            x, y = a['layout'], b['layout']
            if x['col'] < y['col'] + y['width'] and y['col'] < x['col'] + x['width'] and x['row'] < y['row'] + y['height'] and y['row'] < x['row'] + x['height']:
                errors.append(f'overlapping layout: {a["id"]}, {b["id"]}')
    return errors


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    parser.add_argument('--framework-only', action='store_true', help='Validate the empty framework without business configuration')
    args = parser.parse_args()
    issues = validate_framework(args.project) if args.framework_only else validate(args.project)
    if issues:
        for issue in issues:
            print(f'FAIL: {issue}', file=sys.stderr)
        sys.exit(1)
    print('PASS: empty framework' if args.framework_only else 'PASS: schema, metrics, queries, bindings and layout')
