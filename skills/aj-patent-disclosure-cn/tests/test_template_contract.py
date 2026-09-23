"""Regressions against the supplied .doc, not merely generated headings."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from template_contract import TITLE, INSTRUCTION, HEADINGS, LEAF_HEADINGS, verify_template_files
from generate_docx import render_markdown
from check_output_coverage import check_output
from validate_disclosure import validate_payload


class TemplateContractTests(unittest.TestCase):
    def setUp(self):
        self.payload = json.loads((ROOT/'assets/examples/disclosure_input.sample.json').read_text())

    def test_source_and_reference_hashes_match(self):
        verify_template_files()

    @unittest.skipUnless(shutil.which('textutil'), 'macOS source reader unavailable')
    def test_contract_matches_original_binary_doc_text(self):
        result = subprocess.run(['textutil','-convert','txt','-stdout',str(ROOT/'assets/templates/专利申请信息及技术交底书.doc')], capture_output=True, text=True, check=True)
        actual = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        self.assertEqual(actual, [TITLE, INSTRUCTION, *HEADINGS])

    def test_unknown_template_fields_get_agent_fallback(self):
        for key in ('applicant','inventors','existing_technology','software_analysis','application_purposes','applicant_profile','verification'):
            self.payload.pop(key, None)
        self.payload['invention'].pop('principle',None)
        md = render_markdown(self.payload)
        report = check_output(self.payload,md)
        self.assertEqual(report['errors'], [])
        self.assertIn('实验数据：', report['template_pending_fields'])
        for heading in ('第一，现有技术的名称：','第二，现有技术的来源：','实现原理：','实验数据：','特定软件分析结果：'):
            self.assertIn('### '+heading+'\n\n代理确定\n',md)
        self.assertIn('**申请人：**\n\n代理确定',md)
        self.assertIn('**发明人：**\n\n代理确定',md)
        errors = validate_payload(self.payload,Path('input.json'),final=True)['errors']
        self.assertFalse(any(e['code'] in ('verification','verification-status') for e in errors))

    def test_application_purpose_is_not_technical_purpose(self):
        self.payload['application_purposes'] = ['保护推荐技术','申报研发项目']
        md = render_markdown(self.payload)
        section = md.split('## '+HEADINGS[-2])[1].split('## '+HEADINGS[-1])[0]
        self.assertIn('申报研发项目',section)
        self.assertNotIn(self.payload['invention']['purpose'],section)
        self.assertTrue(any(e['path']=='$.application_purposes[1]' for e in check_output(self.payload,md.replace('申报研发项目',''))['errors']))

    def test_all_new_fields_preserved_in_correct_slots(self):
        self.payload.update(existing_technology={'name':'现有方案甲','source':'材料甲第六页'},software_analysis='分析记录乙',applicant_profile={'product_types':'产品丙','work_content':'研发丁','field':'领域戊'})
        self.payload['invention']['principle']='通过约束传播阻断不可行候选。'
        md=render_markdown(self.payload)
        self.assertEqual(check_output(self.payload,md)['errors'],[])
        for value in ('现有方案甲','材料甲第六页','分析记录乙','产品丙','研发丁','领域戊','通过约束传播阻断不可行候选。'):
            self.assertTrue(check_output(self.payload,value+'\n'+md.replace(value,''))['errors'])

    def test_unknown_not_empty_and_no_extra_sections(self):
        self.payload.pop('software_analysis',None)
        md=render_markdown(self.payload)
        broken=md.replace('### 特定软件分析结果：\n\n代理确定','### 特定软件分析结果：\n')
        self.assertTrue(any(e['code']=='output-empty-field' for e in check_output(self.payload,broken)['errors']))
        self.assertTrue(any(e['code']=='output-outline' for e in check_output(self.payload,md+'\n## 摘要草案\n')['errors']))
        # Same labels in a different order must not pass.
        swapped=md.replace(HEADINGS[3],'TEMP').replace(HEADINGS[4],HEADINGS[3]).replace('TEMP',HEADINGS[4])
        self.assertTrue(any(e['code']=='output-sections' for e in check_output(self.payload,swapped)['errors']))

    def test_legacy_personal_information_not_exported(self):
        self.payload.update(department='旧部门标记',first_inventor_id='旧身份标记')
        md=render_markdown(self.payload)
        self.assertNotIn('旧部门标记',md)
        self.assertNotIn('旧身份标记',md)


if __name__ == '__main__':
    unittest.main()
