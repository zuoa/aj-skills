import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ScreenScriptsTests(unittest.TestCase):
    def test_framework_choices_and_empty_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            creator, validator = load('create_screen'), load('validate_screen')
            target = Path(tmp) / 'screen'
            with self.assertRaises(ValueError):
                creator.create_screen(target, layout='unknown')
            self.assertFalse(target.exists())
            with self.assertRaises(ValueError):
                creator.create_screen(target, style='unknown')
            self.assertFalse(target.exists())
            creator.create_screen(target, layout='panorama-wide', palette='pine-teal', title='自定义主题', style='industrial-blueprint')
            path = target / 'src/config/framework.json'
            frame = json.loads(path.read_text())
            self.assertEqual(frame['canvas'], {'width': 3840, 'height': 1080})
            self.assertEqual(frame['paletteId'], 'pine-teal')
            self.assertEqual(frame['styleId'], 'industrial-blueprint')
            self.assertEqual(frame['title'], '自定义主题')
            self.assertTrue((target / 'screen-brief.json').is_file())
            (target / 'src/config/metrics.json').unlink()
            self.assertEqual(validator.validate_framework(target), [])
            frame['styleId'] = 'missing'
            path.write_text(json.dumps(frame))
            self.assertTrue(any('unknown style' in issue for issue in validator.validate_framework(target)))
            frame['styleId'] = 'industrial-blueprint'
            frame['layoutId'] = 'custom'
            frame['customLayout'] = json.loads((target / 'src/config/layouts.json').read_text())['presets'][0]
            frame['customLayout']['id'] = 'custom'
            frame['customLayout']['slots'][1]['layout']['col'] = 1
            path.write_text(json.dumps(frame))
            self.assertTrue(any('overlapping' in issue for issue in validator.validate_framework(target)))

    def test_framework_mapping_diagnostics(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = load('create_screen').create_screen(Path(tmp) / 'screen', layout='map-center')
            path = target / 'src/config/framework.json'
            frame = json.loads(path.read_text())
            frame['bindings'] = {'enterprises': 'overview-1'}
            path.write_text(json.dumps(frame))
            issues = load('validate_screen').validate(target)
            self.assertTrue(any('every component' in issue for issue in issues))
            self.assertTrue(any('unfilled' in issue for issue in issues))

    def test_copy_is_clean_and_never_overwrites(self):
        creator = load('create_screen')
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'screen'
            creator.create_screen(target)
            self.assertTrue((target / 'package-lock.json').is_file())
            self.assertTrue((target / 'REPORTING.md').is_file())
            self.assertTrue((target / 'src/components/MetricReport.vue').is_file())
            self.assertTrue((target / 'src/data/local-reports.ts').is_file())
            self.assertFalse((target / 'node_modules').exists())
            self.assertEqual(load('validate_screen').validate(target), [])
            with self.assertRaises(FileExistsError):
                creator.create_screen(target)

    def test_broken_configs_are_diagnosed_without_execution(self):
        validator = load('validate_screen')
        with tempfile.TemporaryDirectory() as tmp:
            target = load('create_screen').create_screen(Path(tmp) / 'screen')
            path = target / 'src/config/screen.json'
            original = json.loads(path.read_text())
            cases = [('unknown queryId', lambda s: s['components'][0].update(queryId='missing')),
                     ('unknown field', lambda s: s['components'][0]['fields'].update(value='missing')),
                     ('invalid timezone', lambda s: s['queries']['enterprises']['timeRange'].update(timezone='bad/zone')),
                     ('overlapping layout', lambda s: s['components'][0]['layout'].update(width=12)),
                     ('invalid filter type', lambda s: s['queries']['enterprises']['filters'].update(area=42))]
            for message, mutate in cases:
                screen = json.loads(json.dumps(original))
                mutate(screen)
                path.write_text(json.dumps(screen))
                self.assertTrue(any(message in issue for issue in validator.validate(target)), message)


if __name__ == '__main__':
    unittest.main()
