from __future__ import annotations
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import workflow as w


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.case = Path(self.temp.name).resolve()
        self.state = w.init(self.case, '测试案件')
        (self.case / 'materials').mkdir()
        (self.case / 'materials/design.txt').write_text('原始方案：依据上下文进行推荐。')
        self.common = {'summary': '本轮具体技术内容', 'decision': '核对所列事实与取舍', 'next_question': '', 'gaps': []}

    def payload(self, stage):
        forms = {
            'facts': {'sources': [{'id': 'SRC1', 'kind': 'file', 'path': 'materials/design.txt', 'locator': '第1行', 'version': 'v1'}],
                      'facts': [{'id': 'F1', 'statement': '依据上下文进行推荐', 'status': 'source-backed', 'source_ids': ['SRC1']}],
                      'technical_chain': {'problem': '时延', 'input': '上下文', 'processing': '权重融合', 'output': '排序', 'effect': '适配带宽'}},
            'mining': {'selected_candidate': 'P1', 'candidates': [{'id': 'P1', 'problem': '时延', 'mechanism': '融合', 'effect': '适配带宽', 'tradeoff': '尚需查新', 'status': 'core', 'features': [{'id': 'T1', 'description': '上下文融合', 'fact_ids': ['F1']}]}]},
            'search': {'selected_candidate': 'P1', 'mode': 'unavailable', 'reason': '此模拟测试不联网', 'cutoff_date': '2026-09-21', 'limitations': '未执行外部检索', 'conclusion': 'pending-search'},
            'basis': {'selected_candidate': 'P1', 'search_boundary': '仅为待检索候选', 'effects': [{'statement': '适配带宽', 'evidence': '处理机理', 'status': 'mechanism'}], 'embodiments': [{'id': 'E1', 'input': '上下文', 'steps': '编码、融合、排序', 'output': '推荐列表'}], 'support': [{'feature_id': 'T1', 'section': '技术方案S3', 'embodiment_id': 'E1', 'source_ids': ['SRC1']}], 'disclosure_file': 'drafts/disclosure_input.json'},
        }
        payload = {**copy.deepcopy(self.common), **copy.deepcopy(forms[stage])}
        if stage == 'mining':
            payload['exploration'] = {
                'mode': 'expand', 'problem_reframing': '重点可能在上下文与带宽约束的关系，而非模型名称',
                'assumptions': [{'premise': '模型是主要贡献', 'challenge': '信息交互可能更关键', 'check': '检查融合机制'}],
                'opportunities': [{'id': 'O1', 'direction': '核实资源约束下的信息融合', 'mechanism': '观察网络状态如何影响权重',
                                   'expected_effect': '候选排序适配带宽', 'grounding': 'hypothesis', 'fact_ids': ['F1'],
                                   'risk': '可能只是常规处理', 'cost': '低：先检查现有代码', 'validation': '跟踪一条低带宽请求', 'disposition': 'consider'}],
                'recommendation': {'opportunity_id': 'O1', 'reason': '能检验当前主线', 'tradeoff': '暂缓新增模块', 'next_action': '检查一条真实请求'},
            }
        return payload

    def submit_confirm(self, stage, payload=None):
        rec = w.submit(self.case, self.state, stage, payload or self.payload(stage))
        self.assertEqual(rec['errors'], [])
        w.confirm(self.case, self.state, stage, rec['digest'], '模拟用户', '确认本版所列内容', '测试会话第1轮', 'user')
        return rec

    def through_basis(self):
        shutil.copy2(ROOT/'assets/examples/disclosure_input.sample.json', self.case/'drafts/disclosure_input.json')
        for stage in w.STAGES[:4]:
            self.submit_confirm(stage)

    def test_init_refuses_overwrite_and_templates_are_not_ready(self):
        with self.assertRaises(ValueError):
            w.init(self.case, '重建')
        rec = w.submit(self.case, self.state, 'facts', w.read(self.case/'drafts/facts.json'))
        self.assertTrue(rec['errors'])
        self.assertEqual(w.statuses(self.case, self.state)['facts'], 'blocked')
        with self.assertRaises(ValueError):
            w.confirm(self.case, self.state, 'facts', rec['digest'], '用户', '确认', '对话', 'user')

    def test_confirmation_digest_is_exact_and_resumption_works(self):
        rec = self.submit_confirm('facts')
        with self.assertRaises(ValueError):
            w.confirm(self.case, self.state, 'facts', 'old', '用户', '确认', '对话', 'user')
        reloaded = w.load(self.case)
        self.assertEqual(w.statuses(self.case, reloaded)['facts'], 'confirmed')
        same = w.submit(self.case, reloaded, 'facts', self.payload('facts'))
        self.assertEqual(same['version'], rec['version'])
        self.assertEqual(w.statuses(self.case, reloaded)['facts'], 'confirmed')
        self.assertNotIn('```json', (self.case/'reviews/facts.md').read_text())
        self.assertIn('技术事实', (self.case/'reviews/facts.md').read_text())

    def test_source_and_snapshot_changes_block_downstream(self):
        self.through_basis()
        source = self.case/'materials/design.txt'
        source.write_text('新方案')
        self.assertEqual(w.statuses(self.case, self.state)['facts'], 'tampered')
        with self.assertRaises(ValueError):
            w.ensure_export(self.case, self.case/'drafts/disclosure_input.json')
        rec = w.submit(self.case, self.state, 'facts', self.payload('facts'))
        self.assertEqual(rec['version'], 2)
        self.assertEqual(w.statuses(self.case, self.state)['basis'], 'stale')
        snap = self.case/rec['snapshot']
        data = w.read(snap);data['data']['summary'] = '绕过修改';w.save(snap, data)
        self.assertEqual(w.statuses(self.case, self.state)['facts'], 'tampered')

    def test_proposals_and_missing_references_do_not_become_core(self):
        facts = self.payload('facts');facts['facts'][0]['status'] = 'proposal'
        self.submit_confirm('facts', facts)
        rec = w.submit(self.case, self.state, 'mining', self.payload('mining'))
        self.assertTrue(any('引用' in e for e in rec['errors']))
        with self.assertRaises(ValueError):
            w.confirm(self.case, self.state, 'mining', rec['digest'], '用户', '加进去', '对话', 'user')

    def test_new_case_requires_exploration_but_legacy_case_stays_compatible(self):
        self.submit_confirm('facts')
        mining = self.payload('mining');mining.pop('exploration')
        self.assertTrue(any('exploration' in e for e in w.submit(self.case, self.state, 'mining', mining)['errors']))
        self.state.pop('exploration_policy')
        errors, _ = w.validate(self.case, self.state, 'mining', mining)
        self.assertEqual(errors, [])

    def test_proposals_are_visible_before_core_is_ready(self):
        mining = self.payload('mining')
        opportunity = mining['exploration']['opportunities'][0]
        opportunity.update(grounding='proposal', fact_ids=[], disposition='explore')
        mining['candidates'] = [];mining['selected_candidate'] = ''
        rec = w.submit(self.case, self.state, 'mining', mining)
        self.assertTrue(rec['errors'])
        page = (self.case/'reviews/mining.md').read_text()
        self.assertIn('主动挖掘与推荐', page)
        self.assertIn('同意探索（不等于已实现）', page)
        self.assertIn('检查一条真实请求', page)
        with self.assertRaises(ValueError):
            w.confirm(self.case, self.state, 'mining', rec['digest'], '模拟用户', '很不错', '测试', 'user')

    def test_exploration_grounding_and_recommendation_references(self):
        self.submit_confirm('facts')
        mining = self.payload('mining')
        opportunity = mining['exploration']['opportunities'][0]
        opportunity.update(grounding='evidence', fact_ids=[])
        self.assertTrue(w.validate(self.case, self.state, 'mining', mining)[0])
        opportunity['fact_ids'] = ['F1']
        self.assertEqual(w.validate(self.case, self.state, 'mining', mining)[0], [])
        opportunity['disposition'] = 'reject'
        self.assertTrue(any('否决' in e for e in w.validate(self.case, self.state, 'mining', mining)[0]))
        opportunity['disposition'] = 'consider'
        mining['exploration']['recommendation']['opportunity_id'] = 'missing'
        self.assertTrue(any('不存在' in e for e in w.validate(self.case, self.state, 'mining', mining)[0]))

    def test_bounded_mode_requires_user_scope(self):
        self.submit_confirm('facts')
        mining = self.payload('mining');mining['exploration'] = {'mode': 'bounded'}
        self.assertTrue(w.validate(self.case, self.state, 'mining', mining)[0])
        mining['exploration']['scope_reason'] = '测试用户明确只整理已有实现，不增加研发方案'
        self.assertEqual(w.validate(self.case, self.state, 'mining', mining)[0], [])

    def test_dependency_confirmation_and_blocking_gaps(self):
        w.submit(self.case, self.state, 'facts', self.payload('facts'))
        rec = w.submit(self.case, self.state, 'mining', self.payload('mining'))
        self.assertEqual(w.statuses(self.case, self.state)['mining'], 'blocked')
        with self.assertRaises(ValueError):
            w.confirm(self.case, self.state, 'mining', rec['digest'], '用户', '确认', '对话', 'user')
        facts = self.payload('facts');facts['gaps'] = [{'id': 'G1', 'question': '实际阈值依据？', 'status': 'open', 'blocking': True}]
        facts['next_question'] = '实际阈值依据是什么？'
        self.assertTrue(w.submit(self.case, self.state, 'facts', facts)['errors'])

    def test_search_requires_full_feature_mapping_and_honest_status(self):
        self.submit_confirm('facts');self.submit_confirm('mining')
        search = self.payload('search');search['conclusion'] = 'preliminary-candidate'
        self.assertTrue(w.submit(self.case, self.state, 'search', search)['errors'])
        search.update(mode='executed', queries=[{'query': '上下文推荐', 'database': '模拟库', 'searched_at': '2026-09-21', 'result': '模拟文献'}], documents=[{'id': 'D1', 'publication': '模拟文献', 'date': '2025-01-01', 'url': 'https://example.org/test', 'scope': 'claims'}], comparisons=[], differences='差异', reverse_queries=[{'query': '反馈融合', 'result': '模拟未命中', 'implication': '尚待真实检索'}])
        self.assertTrue(w.submit(self.case, self.state, 'search', search)['errors'])
        search['comparisons'] = [{'document_id': 'D1', 'feature_id': 'T1', 'finding': '部分公开', 'locator': '权1'}]
        self.assertEqual(w.submit(self.case, self.state, 'search', search)['errors'], [])

    def test_basis_change_only_invalidates_delivery_not_search(self):
        self.through_basis()
        old = w.record(self.state, 'basis')['digest']
        basis = self.payload('basis');basis['summary'] = '调整正文标题说明'
        w.submit(self.case, self.state, 'basis', basis)
        self.assertEqual(w.statuses(self.case, self.state)['search'], 'confirmed')
        self.assertEqual(w.statuses(self.case, self.state)['basis'], 'ready')
        with self.assertRaises(ValueError):
            w.confirm(self.case, self.state, 'basis', old, '用户', '确认', '对话', 'user')

    def test_basis_purpose_is_required_and_versioned_in_review(self):
        self.through_basis()
        path = self.case/'drafts/disclosure_input.json'
        payload = w.read(path)
        old_purpose = payload['invention']['purpose']
        self.assertIn(old_purpose, (self.case/'reviews/basis.md').read_text())
        payload['invention']['purpose'] = '新的有据技术目标'
        w.save(path, payload)
        w.render(self.case, self.state)
        page = (self.case/'reviews/basis.md').read_text()
        self.assertIn(old_purpose, page)
        self.assertNotIn('新的有据技术目标', page)
        self.assertEqual(w.statuses(self.case, self.state)['basis'], 'tampered')
        rec = w.submit(self.case, self.state, 'basis', self.payload('basis'))
        self.assertEqual(rec['errors'], [])
        self.assertIn('新的有据技术目标', (self.case/'reviews/basis.md').read_text())
        self.assertEqual(w.statuses(self.case, self.state)['basis'], 'ready')
        del payload['invention']['purpose']
        w.save(path, payload)
        rec = w.submit(self.case, self.state, 'basis', self.payload('basis'))
        self.assertTrue(any('purpose' in e for e in rec['errors']))

    def test_path_escape_and_missing_support_are_blocked(self):
        facts = self.payload('facts');facts['sources'][0]['path'] = '../outside.txt'
        self.assertTrue(w.submit(self.case, self.state, 'facts', facts)['errors'])
        self.through_basis()
        basis = self.payload('basis');basis['support'][0]['embodiment_id'] = 'not-found'
        self.assertTrue(w.submit(self.case, self.state, 'basis', basis)['errors'])

    def test_attached_figure_change_invalidates_basis(self):
        self.through_basis()
        image = self.case/'materials/figure.png'
        image.write_bytes(b'original test image')
        path = self.case/'drafts/disclosure_input.json'
        payload = w.read(path)
        payload['figures'][0]['file'] = '../materials/figure.png'
        w.save(path, payload)
        self.submit_confirm('basis')
        image.write_bytes(b'changed image')
        self.assertEqual(w.statuses(self.case, self.state)['basis'], 'tampered')

    def test_delegated_confirmation_does_not_bypass_missing_facts(self):
        rec = w.submit(self.case, self.state, 'facts', w.read(self.case/'drafts/facts.json'))
        with self.assertRaises(ValueError):
            w.confirm(self.case, self.state, 'facts', rec['digest'], '模拟用户', '代我处理', '测试授权', 'delegated')
        rec = w.submit(self.case, self.state, 'facts', self.payload('facts'))
        w.confirm(self.case, self.state, 'facts', rec['digest'], '模拟用户', '按已提供资料代我处理', '测试授权', 'delegated')
        self.assertEqual(w.statuses(self.case, self.state)['facts'], 'confirmed')

    def test_direct_generator_cannot_bypass_case_gate(self):
        shutil.copy2(ROOT/'assets/examples/disclosure_input.sample.json', self.case/'drafts/disclosure_input.json')
        result = subprocess.run([sys.executable, str(ROOT/'scripts/generate_docx.py'), '--input', str(self.case/'drafts/disclosure_input.json'), '--output', str(self.case/'bad.docx')], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Workflow validation failed', result.stdout)
        self.assertFalse((self.case/'bad.docx').exists())

    @unittest.skipUnless(shutil.which('dot') and shutil.which('pandoc'), 'export tools unavailable')
    def test_full_export_review_and_artifact_change(self):
        self.through_basis()
        rec = w.export_case(self.case, 'deliverables/v1.docx')
        self.state = w.load(self.case)
        self.assertEqual(rec['errors'], [])
        self.assertEqual(w.statuses(self.case, self.state)['delivery'], 'ready')
        w.confirm(self.case, self.state, 'delivery', rec['digest'], '模拟用户', '已审阅具体文件', '测试会话第5轮', 'user')
        self.assertTrue(all(s == 'confirmed' for s in w.statuses(self.case, self.state).values()))
        with self.assertRaises(ValueError):
            w.export_case(self.case, 'deliverables/v1.docx')
        (self.case/'deliverables/v1.md').write_text('外部修改稿')
        self.assertEqual(w.statuses(self.case, self.state)['delivery'], 'tampered')
        delivery = w.data_for(self.case, self.state, 'delivery')
        altered = w.submit(self.case, self.state, 'delivery', delivery)
        self.assertTrue(any('文件集合或哈希' in e for e in altered['errors']))
        with self.assertRaises(ValueError):
            w.confirm(self.case, self.state, 'delivery', altered['digest'], '模拟用户', '确认', '测试', 'user')


if __name__ == '__main__':
    unittest.main()
