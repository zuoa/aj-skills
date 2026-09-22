import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from generate_docx import render_markdown, validate_strict_payload
from generate_figures import prepare_figures
from validate_disclosure import validate_payload


class FinalDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.payload = json.loads((ROOT / 'assets/examples/disclosure_input.sample.json').read_text())

    def test_internal_notes_are_not_exported(self):
        self.payload['assumptions'] = ['内部假设标记']
        self.payload['open_questions'] = ['内部问题标记']
        self.payload['appendices'] = ['内部附录标记']
        md = render_markdown(self.payload)
        for forbidden in ('内部假设标记', '内部问题标记', '内部附录标记', '摘要草案', 'evidence_status'):
            self.assertNotIn(forbidden, md)
        self.assertIn('关键技术点和欲保护点', md)
        report = validate_payload(self.payload, Path('input.json'), final=True)
        self.assertIn('unresolved-fact', {x['code'] for x in report['errors']})

    def test_missing_figure_and_unresolved_body_fail(self):
        self.payload['invention']['solution'] = '【待确认：核心公式】'
        self.payload['embodiments'][0]['figure_refs'].append('图99')
        codes = {x['code'] for x in validate_payload(self.payload, Path('input.json'), final=True)['errors']}
        self.assertTrue({'figure-file', 'placeholder', 'figure-reference'} <= codes)

    def test_purpose_and_problem_have_distinct_sections(self):
        md = render_markdown(self.payload)
        problem = self.payload['invention']['technical_problem']
        purpose = self.payload['invention']['purpose']
        self.assertIn('### 要解决的技术问题\n\n' + problem, md)
        self.assertIn('### 发明目的\n\n' + purpose, md)
        self.assertLess(md.index('### 要解决的技术问题'), md.index('### 发明目的'))
        self.assertLess(md.index('### 发明目的'), md.index('### 技术方案'))

    def test_missing_purpose_is_warning_in_draft_and_error_in_final(self):
        for value in (None, '', '  ', [], {}):
            with self.subTest(value=value):
                self.payload['invention']['purpose'] = value
                draft = validate_payload(self.payload, Path('input.json'), final=False)
                final = validate_payload(self.payload, Path('input.json'), final=True)
                self.assertIn('invention-purpose', {e['code'] for e in draft['warnings']})
                self.assertIn('invention-purpose', {e['code'] for e in final['errors']})
                self.assertTrue(any('invention.purpose' in e for e in validate_strict_payload(self.payload)))

    def test_purpose_does_not_substitute_for_problem(self):
        del self.payload['invention']['technical_problem']
        report = validate_payload(self.payload, Path('input.json'), final=False)
        self.assertIn('technical-problem', {e['code'] for e in report['errors']})
        md = render_markdown(self.payload)
        before_purpose = md.split('### 要解决的技术问题')[1].split('### 发明目的')[0]
        self.assertNotIn(self.payload['invention']['purpose'], before_purpose)

    @unittest.skipUnless(shutil.which('dot'), 'Graphviz unavailable')
    def test_branch_cycle_rendering_and_invalid_edge(self):
        payload = {'figure_plan': {'drawings': [{'kind': 'flowchart', 'steps': [
            {'id': 'S1', 'label': 'S1 输入校验', 'type': 'decision', 'next': ['S2', 'S3'], 'edge_label': {'S2': '通过', 'S3': '失败'}},
            {'id': 'S2', 'label': 'S2 输出结果', 'next': []},
            {'id': 'S3', 'label': 'S3 重试', 'next': ['S1']}
        ]}]}, 'figures': [{'num': 1, 'caption': '校验流程'}]}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = prepare_figures(payload, root/'input.json', root/'output.docx')
            self.assertTrue((root/result['figures'][0]['file']).read_bytes().startswith(b'\x89PNG'))
            dot = (root/'output_figures/figure_sources/fig1.dot').read_text()
            self.assertIn('"S3" -> "S1"', dot)
            broken = copy.deepcopy(payload)
            broken['figure_plan']['drawings'][0]['steps'][2]['next'] = ['missing']
            with self.assertRaises(ValueError):
                prepare_figures(broken, root/'input.json', root/'broken.docx')

    @unittest.skipUnless(shutil.which('dot') and shutil.which('pandoc'), 'export tools unavailable')
    def test_export_embeds_every_image_and_preserves_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)/'final.docx'
            command = [sys.executable, str(ROOT/'scripts/generate_docx.py'), '--input', str(ROOT/'assets/examples/disclosure_input.sample.json'), '--output', str(output), '--with-markdown']
            subprocess.run(command, check=True, capture_output=True)
            with zipfile.ZipFile(output) as archive:
                self.assertEqual(len([x for x in archive.namelist() if x.startswith('word/media/')]), 2)
                xml = ET.fromstring(archive.read('word/document.xml'))
                text = ''.join(xml.itertext())
                self.assertNotIn('内部附录', text)
                self.assertNotIn('sample_figures', text)
                self.assertIn('关键技术点和欲保护点', text)
                self.assertIn('发明目的', text)
                self.assertIn(self.payload['invention']['purpose'], text)
                self.assertIn(self.payload['invention']['technical_problem'], text)
                ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                table = xml.find('.//w:tbl', ns)
                self.assertEqual(len(table.findall('w:tr', ns)), 5)
                self.assertIn('所属部门', ''.join(table.itertext()))
                self.assertNotIn('******', text)
                self.assertNotIn('机器人', text)
                self.assertNotIn('写技术交底书需注意', text)
                self.assertIn('本发明是否经过实验、模拟、使用而证明可行，结果如何？', text)
                margins = xml.find('.//w:pgMar', ns)
                self.assertEqual(margins.get('{'+ns['w']+'}left'), '1800')
            before = output.read_bytes()
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
            self.assertEqual(before, output.read_bytes())


if __name__ == '__main__':
    unittest.main()
