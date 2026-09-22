import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from figure_layout import build_dot, build_sequence_dot, fit_to_page, inspect_geometry, wrap_label
from generate_figures import prepare_figures


class FigureValidationTests(unittest.TestCase):
    def test_cjk_line_breaks_and_literal_text(self):
        self.assertEqual(wrap_label('步骤S1\n获取传感器输入并进行校验', 12), '步骤S1\n获取传感器输\n入并进行校验')
        self.assertIn('"A\\"B"', build_dot([{'id': 'A"B', 'label': '<input>&值'}], []))

    def test_bad_groups_edges_and_options_fail(self):
        nodes = [{'id': 'n', 'label': '模块', 'group': 'g'}]
        with self.assertRaises(ValueError):
            build_dot(nodes, [])
        with self.assertRaises(ValueError):
            build_dot(nodes, [], {'groups': [{'id': 'g', 'parent': 'h'}, {'id': 'h', 'parent': 'g'}]})
        with self.assertRaises(ValueError):
            build_dot([{'id': 'n'}], [{'from': 'n', 'to': 'missing'}])
        with self.assertRaises(ValueError):
            build_dot([{'id': 'n'}], [], {'layout': {'ranksep': float('nan')}})
        with self.assertRaises(ValueError):
            build_dot([{'id': 'n'}], [], {'layout': {'same_rank': [['missing']]}})

    def test_print_fit_preserves_ratio_and_does_not_upscale(self):
        for width, height in ((100, 200), (200, 3000), (2400, 300)):
            fit = fit_to_page(width, height)
            self.assertLessEqual(fit['width_cm'], 14)
            self.assertLessEqual(fit['height_cm'], 18)
            self.assertAlmostEqual(fit['width_cm']/fit['height_cm'], width/height, delta=0.002)
            self.assertLessEqual(fit['scale'], 1)
        with self.assertRaises(ValueError):
            fit_to_page(float('nan'), 100)

    def test_geometry_detects_overlap_and_detached_arrow(self):
        graph = {'objects': [{'name': n, 'pos': '20,20', 'width': '1', 'height': '1'} for n in ('a', 'b')],
                 'edges': [{'tail': 0, 'head': 1, '_draw_': [{'op': 'b', 'points': [[0, 0], [10, 0]]}],
                            '_hdraw_': [{'op': 'P', 'points': [[50, 0], [45, 2], [45, -2]]}]}]}
        report = inspect_geometry(graph)
        self.assertEqual(report['overlapping_node_boxes'], [['a', 'b']])
        self.assertEqual(len(report['disconnected_arrowheads']), 1)

    def test_sequence_rejects_unknown_actor_and_unimplemented_self_call(self):
        spec = {'participants': [{'id': 'a'}, {'id': 'b'}], 'messages': [{'from': 'a', 'to': 'c', 'label': '消息'}]}
        with self.assertRaises(ValueError):
            build_sequence_dot(spec)
        spec['messages'][0]['to'] = 'a'
        with self.assertRaises(ValueError):
            build_sequence_dot(spec)


@unittest.skipUnless(shutil.which('dot') and shutil.which('neato'), 'Graphviz unavailable')
class FigureRenderingTests(unittest.TestCase):
    def setUp(self):
        self.payload = json.loads((ROOT / 'assets/examples/figure_gallery.sample.json').read_text())

    def test_gallery_exports_native_drawio_and_preserves_message_order(self):
        before = copy.deepcopy(self.payload)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            result = prepare_figures(self.payload, root/'input.json', root/'gallery.docx')
            self.assertEqual(self.payload, before)
            for i in range(1, 4):
                stem = root/'gallery_figures'/f'fig{i}'
                for suffix in ('.png', '.svg', '.pdf', '.drawio', '.layout.json'):
                    self.assertGreater(stem.with_suffix(suffix).stat().st_size, 0)
                svg = ET.parse(stem.with_suffix('.svg')).getroot()
                # SVG remains in physical points, not 300-DPI multiplied units.
                self.assertLess(float(svg.attrib['width'].removesuffix('pt')), 1000)
                xml = ET.parse(stem.with_suffix('.drawio'))
                cells = xml.findall('.//mxCell')
                ids = {cell.get('id') for cell in cells}
                for edge in [c for c in cells if c.get('edge') == '1']:
                    self.assertIn(edge.get('source'), ids)
                    self.assertIn(edge.get('target'), ids)
                self.assertFalse(xml.findall('.//image'))
                report = json.loads(stem.with_suffix('.layout.json').read_text())
                self.assertEqual(report['geometry']['overlapping_node_boxes'], [])
                self.assertEqual(report['geometry']['disconnected_arrowheads'], [])
                self.assertEqual(report['visual_review'], 'required')
            xml = ET.parse(root/'gallery_figures/fig1.drawio')
            vertices = [c for c in xml.findall('.//mxCell') if c.get('vertex') == '1']
            self.assertTrue(any(c.get('parent') not in ('0', '1') for c in vertices))
            sequence = ET.parse(root/'gallery_figures/fig3.svg')
            ns = {'s': 'http://www.w3.org/2000/svg'}
            labels = {e.text: float(e.get('y')) for e in sequence.findall('.//s:text', ns)}
            self.assertLess(labels['上传待复核样本'], labels['返回复核结果'])
            self.assertLess(labels['返回复核结果'], labels['确认结果已接收'])
            # Arrows must remain the three requested directed messages.
            edges = [c for c in ET.parse(root/'gallery_figures/fig3.drawio').findall('.//mxCell') if c.get('edge') == '1' and c.get('value')]
            self.assertEqual([e.get('value') for e in edges], ['上传待复核样本', '返回复核结果', '确认结果已接收'])
            self.assertTrue(all(0 < f['display_width_cm'] <= 14 for f in result['figures']))

    def test_nested_groups_and_invalid_membership(self):
        payload = {'figure_plan': {'drawings': [{'kind': 'architecture', 'groups': [
            {'id': 'device', 'label': '设备'}, {'id': 'scheduler', 'label': '调度子系统', 'parent': 'device'}],
            'components': [{'id': 'a', 'name': '调度', 'group': 'scheduler', 'connections': ['b']},
                           {'id': 'b', 'name': '缓存', 'group': 'device', 'connections': []}]}]}}
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            prepare_figures(payload, root/'input.json', root/'nested.docx')
            xml = ET.parse(root/'nested_figures/fig1.drawio')
            values = {c.get('value'): c for c in xml.findall('.//mxCell') if c.get('vertex')}
            self.assertEqual(values['调度'].get('parent'), values['调度子系统'].get('id'))
            self.assertEqual(values['调度子系统'].get('parent'), values['设备'].get('id'))

    def test_dense_figure_reports_print_readability_limit(self):
        nodes = [{'id': f'S{i}', 'label': f'S{i} 处理数据', 'next': [f'S{i+1}'] if i < 19 else []} for i in range(20)]
        payload = {'figure_plan': {'drawings': [{'kind': 'flowchart', 'steps': nodes}]}}
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            prepare_figures(payload, root/'in.json', root/'dense.docx')
            report = json.loads((root/'dense_figures/fig1.layout.json').read_text())
            self.assertLess(report['estimated_min_font_pt'], 7.5)
            self.assertTrue(report['warnings'])
            self.assertLessEqual(report['print_size']['height_cm'], 18)

    @unittest.skipUnless(shutil.which('pandoc'), 'Pandoc unavailable')
    def test_docx_uses_fitted_dimensions_and_embeds_all_three_types(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            payload = json.loads((ROOT/'assets/examples/disclosure_input.sample.json').read_text())
            payload['figure_plan'] = self.payload['figure_plan']
            payload['figures'] = [{'num': i, 'caption': d['caption']} for i, d in enumerate(self.payload['figure_plan']['drawings'], 1)]
            source = root/'input.json'
            source.write_text(json.dumps(payload, ensure_ascii=False))
            subprocess.run([sys.executable, str(ROOT/'scripts/generate_docx.py'), '--input', str(source),
                            '--output', str(root/'gallery.docx'), '--with-markdown'], check=True, capture_output=True)
            with zipfile.ZipFile(root/'gallery.docx') as archive:
                xml = ET.fromstring(archive.read('word/document.xml'))
                extents = xml.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}extent')
                self.assertEqual(len(extents), 3)
                for extent in extents:
                    self.assertLessEqual(int(extent.get('cx')), 5040000)
                    self.assertLessEqual(int(extent.get('cy')), 6480000)
                self.assertLess(int(extents[2].get('cx')), 5040000)


if __name__ == '__main__':
    unittest.main()
