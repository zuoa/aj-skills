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
sys.path.insert(0, str(ROOT/'scripts'))
from check_output_coverage import check_output, QUESTIONS
from generate_docx import render_markdown
from validate_disclosure import validate_payload
from template_contract import HEADINGS, TITLE, INSTRUCTION

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS = {'w': W}


class CoverageTests(unittest.TestCase):
    def setUp(self):
        self.payload = json.loads((ROOT/'assets/examples/disclosure_input.sample.json').read_text())

    def test_valid_input_and_optional_absence(self):
        report = check_output(self.payload, render_markdown(self.payload))
        self.assertEqual(report['errors'], [])
        self.assertTrue(any(r['status'] == 'not_applicable' for r in report['coverage']))

    def test_heading_without_purpose_does_not_pass(self):
        md = render_markdown(self.payload).replace(self.payload['invention']['purpose'], '')
        report = check_output(self.payload, md)
        self.assertTrue(any(e['code'] == 'coverage-omitted' and e['path'].endswith('.purpose') for e in report['errors']))

    def test_content_moved_to_wrong_section_does_not_pass(self):
        purpose = self.payload['invention']['purpose']
        md = render_markdown(self.payload).replace(purpose, '')+'\n'+purpose
        report = check_output(self.payload, md)
        self.assertTrue(any(e['path'].endswith('.purpose') for e in report['errors']))

    def test_content_moved_to_wrong_subsection_does_not_pass(self):
        field = self.payload['technical_field']
        md = render_markdown(self.payload).replace(field, '').replace('### 第三，现有技术的技术方案：', '### 第三，现有技术的技术方案：\n\n'+field)
        self.assertTrue(any(e['path'] == '$.technical_field' for e in check_output(self.payload, md)['errors']))

    def test_punctuation_only_required_content_does_not_pass(self):
        self.payload['verification'] = {'status': '……'}
        self.assertIn('代理确定', render_markdown(self.payload).split('### 实验数据：')[1].split('### 特定软件分析结果：')[0])

    def test_optional_provided_content_cannot_be_silently_dropped(self):
        self.payload['other_uses'] = '可用于受限带宽的工业视频检索。'
        md = render_markdown(self.payload).replace(self.payload['other_uses'], '')
        self.assertTrue(any(e['path'] == '$.other_uses' for e in check_output(self.payload, md)['errors']))

    def test_missing_protection_and_empty_verification_are_blocked(self):
        self.payload['invention']['key_features'] = []
        self.payload['verification'] = {'status': ''}
        report = validate_payload(self.payload, Path('input.json'), final=True)
        self.assertIn('coverage-required', {e['code'] for e in report['errors']})
        self.assertIn('verification-status', {e['code'] for e in report['errors']})

    def test_missing_step_io_and_embodiment_output_are_blocked(self):
        self.payload['invention']['solution_steps'][0].pop('input')
        self.payload['invention']['solution_steps'][0].pop('output')
        self.payload['embodiments'][0].pop('outputs')
        codes = {e['code'] for e in validate_payload(self.payload, Path('input.json'), final=True)['errors']}
        self.assertTrue({'step-input', 'step-output', 'embodiment-output'} <= codes)

    @unittest.skipUnless(shutil.which('dot') and shutil.which('pandoc'), 'export tools unavailable')
    def test_word_coverage_styles_and_deleted_content(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)/'sample.docx'
            command = [sys.executable,str(ROOT/'scripts/generate_docx.py'),'--input',str(ROOT/'assets/examples/disclosure_input.sample.json'),'--output',str(output),'--with-markdown']
            subprocess.run(command, check=True, capture_output=True)
            report = json.loads(output.with_suffix('.quality.json').read_text())
            self.assertEqual(report['errors'], [])
            self.assertTrue(all(r['status'] == 'passed' for r in report['coverage'] if r['required']))
            md = output.with_suffix('.md').read_text()
            self.assertEqual(check_output(self.payload, md, output)['errors'], [])
            import re
            caption_only = re.sub(r'!\[([^\]]+)\]\([^\n]+\)', r'\1', md)
            self.assertTrue(any(e['code'] == 'output-images' and e['path'] == 'markdown' for e in check_output(self.payload,caption_only,output)['errors']))
            with zipfile.ZipFile(output) as archive:
                entries = {n: archive.read(n) for n in archive.namelist()}
            with zipfile.ZipFile(ROOT/'assets/templates/专利申请信息及技术交底书.docx') as template:
                source = ET.fromstring(template.read('word/document.xml'))
            tree = ET.fromstring(entries['word/document.xml'])
            table = tree.find('.//w:tbl',NS)
            self.assertEqual(len(table.findall('w:tr',NS)), 8)
            for key in ('pgSz','pgMar'):
                self.assertEqual(tree.find('.//w:'+key,NS).attrib,source.find('.//w:'+key,NS).attrib)
            fixed = {''.join(p.itertext()):p for p in source.findall('.//w:p',NS)}
            for p in tree.findall('.//w:p',NS):
                text = ''.join(p.itertext())
                if text in HEADINGS:
                    self.assertEqual([ET.tostring(r) for r in p.findall('w:r',NS)], [ET.tostring(r) for r in fixed[text].findall('w:r',NS)])
            tree = ET.fromstring(entries['word/document.xml'])
            for paragraph in tree.findall('.//w:p',NS):
                if paragraph.find('.//w:drawing',NS) is not None:
                    self.assertIn('图', ''.join(paragraph.itertext()))
                    self.assertEqual(paragraph.find('w:pPr/w:keepLines',NS).get('{'+W+'}val'),'1')
            duplicated = copy.deepcopy(tree)
            blips = duplicated.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/main}blip')
            embed = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed'
            blips[1].set(embed, blips[0].get(embed))
            duplicate_file = Path(directory)/'duplicated-image.docx'
            with zipfile.ZipFile(duplicate_file,'w') as archive:
                for name,data in entries.items():
                    archive.writestr(name, ET.tostring(duplicated) if name == 'word/document.xml' else data)
            self.assertTrue(any(e['code'] == 'output-images' for e in check_output(self.payload,md,duplicate_file)['errors']))
            for paragraph in tree.findall('.//w:p',NS):
                if ''.join(t.text or '' for t in paragraph.findall('.//w:t',NS)) == self.payload['invention']['purpose']:
                    for t in paragraph.findall('.//w:t',NS): t.text = ''
            entries['word/document.xml'] = ET.tostring(tree)
            broken = Path(directory)/'missing-purpose.docx'
            with zipfile.ZipFile(broken,'w') as archive:
                for name,data in entries.items(): archive.writestr(name,data)
            self.assertTrue(any(e['path'].endswith('.purpose') and 'docx' in e['message'] for e in check_output(self.payload,md,broken)['errors']))
            # A valid-looking caption must not stand in for actual embedded media.
            broken_images = Path(directory)/'missing-images.docx'
            with zipfile.ZipFile(broken_images,'w') as archive:
                for name,data in entries.items():
                    if not name.startswith('word/media/'): archive.writestr(name,data)
            self.assertTrue(any(e['code'] == 'output-images' for e in check_output(self.payload,md,broken_images)['errors']))


if __name__ == '__main__':
    unittest.main()
