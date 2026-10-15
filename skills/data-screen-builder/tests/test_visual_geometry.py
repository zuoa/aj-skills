import copy
import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('geometry', Path(__file__).resolve().parents[1] / 'scripts/check_visual_geometry.py')
geometry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(geometry)


class VisualGeometryTests(unittest.TestCase):
    def snapshot(self):
        return {'viewports': [{'width': 1920, 'height': 1080, 'elements': [
            {'id': 'panel', 'rect': {'x': 0, 'y': 0, 'width': 300, 'height': 250}},
            {'id': 'chart', 'rect': {'x': 10, 'y': 40, 'width': 280, 'height': 160}},
            {'id': 'footer', 'rect': {'x': 10, 'y': 205, 'width': 280, 'height': 25}},
        ], 'relations': [{'kind': 'contains', 'a': 'panel', 'b': 'chart'}, {'kind': 'separate', 'a': 'chart', 'b': 'footer'}]}]}

    def test_valid_internal_layout(self):
        self.assertEqual(geometry.check_snapshot(self.snapshot()), [])

    def test_detects_internal_overlap_even_when_whole_panel_fits(self):
        snapshot = self.snapshot()
        snapshot['viewports'][0]['elements'][2]['rect']['y'] = 190
        self.assertTrue(any('overlap chart / footer' in issue for issue in geometry.check_snapshot(snapshot)))

    def test_detects_escaped_or_clipped_content(self):
        snapshot = self.snapshot()
        snapshot['viewports'][0]['elements'][1]['rect']['width'] = 310
        snapshot['viewports'][0]['elements'][1]['clipped'] = True
        issues = geometry.check_snapshot(snapshot)
        self.assertTrue(any('escapes panel' in issue for issue in issues))
        self.assertTrue(any('clipped content' in issue for issue in issues))

    def test_missing_measurements_never_pass(self):
        self.assertTrue(geometry.check_snapshot({}))
        snapshot = copy.deepcopy(self.snapshot())
        snapshot['viewports'][0]['relations'][0]['b'] = 'unmeasured'
        self.assertTrue(any('missing relation target' in issue for issue in geometry.check_snapshot(snapshot)))


if __name__ == '__main__':
    unittest.main()
