#!/usr/bin/env python3
"""Versioned, evidence-linked patent case workflow. Standard library only."""
from __future__ import annotations
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

STAGES = ('facts', 'mining', 'search', 'basis', 'delivery')
LABELS = dict(zip(STAGES, ('事实梳理', '发明挖掘', '检索验证', '起草依据', '成稿与校验')))
STATUS_LABELS = {'not_started': '尚未开始', 'ready': '待核对', 'confirmed': '已确认',
                 'blocked': '尚未满足推进条件', 'stale': '上游已更新，需复核', 'tampered': '文件变化或不可用，需复核'}
ROOT = Path(__file__).resolve().parents[1]


def now():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(temp, path)


def inside(case, name):
    path = (case / name).resolve()
    if not path.is_relative_to(case):
        raise ValueError(f'案件引用必须位于案件目录内: {name}')
    return path


@contextmanager
def locked(case):
    lock = case / 'workflow' / '.lock'
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise ValueError('案件正在被其他操作修改；如上次异常退出，请先核实再移除 workflow/.lock')
    try:
        os.close(fd)
        yield
    finally:
        lock.unlink()


def load(case):
    state = read(case / 'workflow/state.json')
    if state.get('schema_version') != 1:
        raise ValueError('不支持的工作流版本')
    return state


def init(case, title):
    if case.is_relative_to(ROOT):
        raise ValueError('案件目录必须位于 skill 安装目录之外')
    if (case / 'workflow').exists():
        raise ValueError('工作流已存在；使用 status 恢复，不覆盖已有案件')
    (case / 'workflow').mkdir(parents=True)
    state = {'schema_version': 1, 'exploration_policy': 'proactive-v1', 'title': title, 'created_at': now(), 'stages': {}, 'events': []}
    for stage in STAGES:
        save(case / f'drafts/{stage}.json', read(ROOT / f'assets/workflow/{stage}.json'))
    save(case / 'workflow/state.json', state)
    render(case, state)
    return state


def record(state, stage):
    return state['stages'].get(stage)


def data_for(case, state, stage):
    rec = record(state, stage)
    return read(inside(case, rec['snapshot']))['data'] if rec else {}


def integrity(case, rec):
    errors = []
    try:
        snap = read(inside(case, rec['snapshot']))
        if digest(snap) != rec['digest']:
            errors.append('阶段快照被修改')
        for item in snap['attachments']:
            if file_hash(inside(case, item['path'])) != item['sha256']:
                errors.append('附件已变化: ' + item['path'])
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append('快照或附件不可用: ' + str(exc))
    return errors


def statuses(case, state):
    result = {}
    for i, stage in enumerate(STAGES):
        rec = record(state, stage)
        if not rec:
            result[stage] = 'not_started'
            continue
        previous = {s: record(state, s)['digest'] for s in STAGES[:i] if record(state, s)}
        if integrity(case, rec):
            result[stage] = 'tampered'
        elif rec.get('invalidated_by') or rec['upstream'] != previous or any(result[s] != 'confirmed' for s in STAGES[:i]):
            result[stage] = 'stale' if rec.get('confirmation') else 'blocked'
        elif rec['errors']:
            result[stage] = 'blocked'
        elif rec.get('confirmation') and rec['confirmation']['digest'] == rec['digest']:
            result[stage] = 'confirmed'
        else:
            result[stage] = 'ready'
    return result


def validate(case, state, stage, data):
    errors, attachments = [], []
    if not isinstance(data, dict):
        return ['阶段输入必须是 JSON 对象'], []

    def text(obj, key, where=''):
        v = obj.get(key)
        if not isinstance(v, str) or not v.strip():
            errors.append(f'{where}{key}: 需要非空文本')
            return ''
        return v

    def rows(obj, key, fields=(), minimum=1):
        values = obj.get(key)
        if not isinstance(values, list):
            errors.append(f'{key}: 需要列表')
            return []
        if len(values) < minimum:
            errors.append(f'{key}: 至少需要 {minimum} 项')
        valid = []
        for n, row in enumerate(values):
            if not isinstance(row, dict):
                errors.append(f'{key}[{n}]: 需要对象')
                continue
            for f in fields:
                text(row, f, f'{key}[{n}].')
            valid.append(row)
        return valid

    def ids(values, key='id'):
        values = [r.get(key) for r in values]
        if len(set(str(v) for v in values)) != len(values):
            errors.append(f'{key}: 存在重复 ID')
        return set(v for v in values if isinstance(v, str) and v)

    def refs(obj, key, allowed):
        values = obj.get(key)
        if not isinstance(values, list) or not values:
            errors.append(f'{key}: 需要非空引用列表')
        elif any(not isinstance(v, str) or v not in allowed for v in values):
            errors.append(f'{key}: 引用了不存在或不可采用的 ID')

    def attach(name):
        try:
            if not isinstance(name, str) or not name:
                raise ValueError('缺少附件路径')
            p = inside(case, name)
            if not p.is_file():
                raise ValueError('文件不存在: ' + name)
            attachments.append({'path': str(p.relative_to(case)), 'sha256': file_hash(p)})
            return p
        except (OSError, ValueError) as exc:
            errors.append(str(exc))
            return None

    text(data, 'summary')
    text(data, 'decision')
    gaps = rows(data, 'gaps', ('id', 'question', 'status'), minimum=0)
    for gap in gaps:
        if gap.get('status') not in ('open', 'resolved', 'excluded'):
            errors.append('gap.status: 必须为 open/resolved/excluded')
        if not isinstance(gap.get('blocking'), bool):
            errors.append('gap.blocking: 需要布尔值')
        if gap.get('status') == 'open' and gap.get('blocking'):
            errors.append('关键缺口尚未解决: ' + str(gap.get('id')))
        if gap.get('status') in ('resolved', 'excluded'):
            text(gap, 'resolution')
    if any(g.get('status') == 'open' for g in gaps):
        text(data, 'next_question')

    if stage == 'facts':
        sources = rows(data, 'sources', ('id', 'kind', 'locator', 'version'))
        source_ids = ids(sources)
        for source in sources:
            if source.get('kind') == 'file':
                attach(source.get('path'))
            elif source.get('kind') not in ('conversation', 'url'):
                errors.append('source.kind: 必须为 file/conversation/url')
        facts = rows(data, 'facts', ('id', 'statement', 'status'))
        ids(facts)
        for fact in facts:
            refs(fact, 'source_ids', source_ids)
            if fact.get('status') not in ('source-backed', 'user-confirmed', 'inferred', 'proposal', 'unknown'):
                errors.append('fact.status: 不支持的事实状态')
        for f in ('problem', 'input', 'processing', 'output', 'effect'):
            text(data.get('technical_chain', {}) if isinstance(data.get('technical_chain'), dict) else {}, f, 'technical_chain.')
    elif stage == 'mining':
        facts = data_for(case, state, 'facts').get('facts', [])
        supported = {f['id'] for f in facts if f['status'] in ('source-backed', 'user-confirmed')}
        if state.get('exploration_policy') == 'proactive-v1' or 'exploration' in data:
            exploration = data.get('exploration')
            if not isinstance(exploration, dict):
                errors.append('exploration: 新案件需提供主动挖掘与推荐，不能只要求用户提供创新点')
            elif exploration.get('mode') == 'bounded':
                text(exploration, 'scope_reason')
            elif exploration.get('mode') == 'expand':
                text(exploration, 'problem_reframing')
                rows(exploration, 'assumptions', ('premise', 'challenge', 'check'), minimum=0)
                opportunities = rows(exploration, 'opportunities', ('id', 'direction', 'mechanism', 'expected_effect', 'grounding', 'risk', 'cost', 'validation', 'disposition'))
                opportunity_ids = ids(opportunities)
                all_fact_ids = {f['id'] for f in facts}
                for opportunity in opportunities:
                    grounding = opportunity.get('grounding')
                    if grounding not in ('evidence', 'hypothesis', 'proposal'):
                        errors.append('opportunity.grounding: 必须为 evidence/hypothesis/proposal')
                    if opportunity.get('disposition') not in ('consider', 'explore', 'defer', 'reject'):
                        errors.append('opportunity.disposition: 不支持的处置状态')
                    if grounding == 'evidence':
                        refs(opportunity, 'fact_ids', supported)
                    else:
                        values = opportunity.get('fact_ids')
                        if not isinstance(values, list) or any(not isinstance(v, str) or v not in all_fact_ids for v in values):
                            errors.append('opportunity.fact_ids: 需要有效事实引用列表，可为空')
                recommendation = exploration.get('recommendation')
                if not isinstance(recommendation, dict):
                    errors.append('recommendation: 需要明确推荐、理由、取舍和下一步')
                else:
                    for key in ('opportunity_id', 'reason', 'tradeoff', 'next_action'):
                        text(recommendation, key)
                    selected_opportunity = recommendation.get('opportunity_id')
                    if not isinstance(selected_opportunity, str) or selected_opportunity not in opportunity_ids:
                        errors.append('recommendation.opportunity_id: 推荐机会不存在')
                    elif any(o.get('id') == selected_opportunity and o.get('disposition') in ('reject', 'defer') for o in opportunities):
                        errors.append('不能推荐已否决或延期的机会')
            else:
                errors.append('exploration.mode: 必须为 expand/bounded')
        candidates = rows(data, 'candidates', ('id', 'problem', 'mechanism', 'effect', 'tradeoff', 'status'))
        candidate_ids = ids(candidates)
        for candidate in candidates:
            if candidate.get('status') not in ('core', 'dependent', 'rejected', 'proposal'):
                errors.append('candidate.status: 不支持的候选状态')
            features = rows(candidate, 'features', ('id', 'description'))
            ids(features)
            if candidate.get('status') in ('core', 'dependent'):
                for feature in features:
                    refs(feature, 'fact_ids', supported)
        selected = text(data, 'selected_candidate')
        if selected not in candidate_ids or not any(c.get('id') == selected and c.get('status') == 'core' for c in candidates):
            errors.append('selected_candidate: 必须选择有事实支撑的 core 候选')
    elif stage == 'search':
        candidates = data_for(case, state, 'mining').get('candidates', [])
        allowed = {c['id'] for c in candidates if c['status'] in ('core', 'dependent')}
        selected = text(data, 'selected_candidate')
        if selected not in allowed:
            errors.append('selected_candidate: 不在已核对的候选中；先更新 mining')
        mode = data.get('mode')
        text(data, 'cutoff_date')
        text(data, 'limitations')
        if mode == 'unavailable':
            text(data, 'reason')
            if data.get('conclusion') != 'pending-search':
                errors.append('未检索时 conclusion 只能是 pending-search')
        elif mode == 'executed':
            rows(data, 'queries', ('query', 'database', 'searched_at', 'result'), minimum=1)
            documents = rows(data, 'documents', ('id', 'publication', 'date', 'url', 'scope'))
            doc_ids = ids(documents)
            for doc in documents:
                if doc.get('scope') not in ('full-text', 'claims'):
                    errors.append('核心对比文献需核验全文或权利要求，不能只用摘要')
            features = {f['id'] for c in candidates if c['id'] == selected for f in c['features']}
            comparisons = rows(data, 'comparisons', ('document_id', 'feature_id', 'finding', 'locator'))
            for row in comparisons:
                if row.get('document_id') not in doc_ids or row.get('feature_id') not in features:
                    errors.append('comparisons: 文献或特征引用无效')
            if not any(features <= {r['feature_id'] for r in comparisons if r['document_id'] == doc} for doc in doc_ids):
                errors.append('缺少覆盖选定候选全部必要特征的单一文献对照')
            text(data, 'differences')
            rows(data, 'reverse_queries', ('query', 'result', 'implication'))
            if data.get('conclusion') not in ('preliminary-candidate', 'high-risk', 'rejected'):
                errors.append('conclusion: 不支持的检索结论')
        else:
            errors.append('search.mode: 必须为 executed/unavailable')
    elif stage == 'basis':
        search = data_for(case, state, 'search')
        if data.get('selected_candidate') != search.get('selected_candidate'):
            errors.append('起草主线与检索阶段不一致')
        if search.get('conclusion') == 'rejected':
            errors.append('已淘汰主线不能进入起草；回到候选阶段')
        text(data, 'search_boundary')
        effects = rows(data, 'effects', ('statement', 'evidence', 'status'))
        for effect in effects:
            if effect.get('status') not in ('measured', 'mechanism'):
                errors.append('effect.status: 必须为 measured/mechanism，未验证设想不能写成确定效果')
        embodiments = rows(data, 'embodiments', ('id', 'input', 'steps', 'output'))
        embodiment_ids = ids(embodiments)
        support = rows(data, 'support', ('feature_id', 'section', 'embodiment_id'))
        source_ids = {s['id'] for s in data_for(case, state, 'facts').get('sources', [])}
        for row in support:
            refs(row, 'source_ids', source_ids)
            if row.get('embodiment_id') not in embodiment_ids:
                errors.append('support: 实施例引用不存在')
        candidates = data_for(case, state, 'mining').get('candidates', [])
        features = {f['id'] for c in candidates if c['id'] == data.get('selected_candidate') for f in c['features']}
        if not features or not features <= {r.get('feature_id') for r in support if isinstance(r, dict)}:
            errors.append('support: 未覆盖主线的全部必要特征')
        disclosure = attach(data.get('disclosure_file'))
        if disclosure:
            from validate_disclosure import validate_payload
            payload = read(disclosure)
            invention = payload.get('invention')
            text(invention if isinstance(invention, dict) else {}, 'purpose', 'invention.')
            report = validate_payload(payload, disclosure, final=False)
            errors.extend('交底输入: ' + str(e) for e in report['errors'])
            if payload.get('open_questions') or payload.get('assumptions'):
                errors.append('交底输入仍含未解决事实或假设')
            for figure in payload.get('figures', []):
                if isinstance(figure, dict) and figure.get('file'):
                    image = (disclosure.parent / figure['file']).resolve()
                    if image.exists():
                        if image.is_relative_to(case):
                            attach(str(image.relative_to(case)))
                        else:
                            errors.append('起草附图必须放在案件目录内')
    elif stage == 'delivery':
        items = rows(data, 'artifacts', ('kind', 'path'))
        kinds = {r.get('kind') for r in items}
        if not {'docx', 'markdown', 'quality', 'figure'} <= kinds:
            errors.append('交付需包含 docx、markdown、quality 和 figure')
        for item in items:
            p = attach(item.get('path'))
            if p and item.get('kind') == 'quality':
                report = read(p)
                if report.get('errors') != []:
                    errors.append('终稿质量报告未通过')
                coverage = report.get('coverage')
                if not isinstance(coverage, list) or not coverage or any(
                    not isinstance(row, dict) or row.get('status') not in ('passed', 'not_applicable')
                    or (row.get('required') and row.get('status') != 'passed') for row in coverage
                ):
                    errors.append('终稿缺少已通过的导出内容覆盖检查；请重新导出')
                basis = data_for(case, state, 'basis')
                disclosure = inside(case, basis.get('disclosure_file', ''))
                docx = next((inside(case, r['path']) for r in items if r.get('kind') == 'docx'), None)
                if not disclosure.is_file() or report.get('input_sha256') != file_hash(disclosure):
                    errors.append('质量报告与已确认输入不匹配')
                if not docx or not docx.is_file() or report.get('output_sha256') != file_hash(docx):
                    errors.append('质量报告与 Word 产物不匹配')
                manifest = report.get('artifacts', [])
                expected_files = {(r.get('kind'), str((p.parent / r.get('path', '')).resolve())): r.get('sha256')
                                  for r in manifest if isinstance(r, dict)}
                supplied_files = {(r.get('kind'), str(inside(case, r['path']))): file_hash(inside(case, r['path']))
                                  for r in items if r.get('kind') != 'quality' and inside(case, r['path']).is_file()}
                if not expected_files or supplied_files != expected_files:
                    errors.append('交付文件集合或哈希与导出报告不一致（包括正文、Markdown、附图和源文件）')
        if data.get('basis_digest') != (record(state, 'basis') or {}).get('digest'):
            errors.append('交付未绑定当前起草依据版本')
    return errors, attachments


def submit(case, state, stage, data):
    errors, attachments = validate(case, state, stage, data)
    i = STAGES.index(stage)
    upstream = {s: record(state, s)['digest'] for s in STAGES[:i] if record(state, s)}
    snap = {'stage': stage, 'data': data, 'attachments': attachments, 'upstream': upstream}
    if stage == 'basis' and isinstance(data, dict):
        # Derived display content is captured in this version, never edited separately.
        for attachment in attachments:
            if inside(case, attachment['path']) == inside(case, data.get('disclosure_file', '')):
                payload = read(inside(case, attachment['path']))
                invention = payload.get('invention', {})
                if isinstance(invention, dict):
                    snap['disclosure_overview'] = {key: invention.get(key, '') for key in ('technical_problem', 'purpose')}
                break
    sha = digest(snap)
    old = record(state, stage)
    if old and old['digest'] == sha and not old.get('invalidated_by') and not integrity(case, old):
        return old
    version = (old['version'] if old else 0) + 1
    path = f'workflow/revisions/{stage}/v{version:04d}.json'
    if inside(case, path).exists():
        raise ValueError('版本路径已存在，拒绝覆盖；请检查上次中断的工作流')
    save(inside(case, path), snap)
    rec = {'version': version, 'snapshot': path, 'digest': sha, 'upstream': upstream, 'errors': errors, 'submitted_at': now()}
    state['stages'][stage] = rec
    for downstream in STAGES[i+1:]:
        if record(state, downstream):
            state['stages'][downstream]['invalidated_by'] = stage
    state['events'].append({'action': 'submit', 'stage': stage, 'version': version, 'digest': sha, 'at': now()})
    save(case / 'workflow/state.json', state)
    render(case, state)
    return rec


def confirm(case, state, stage, sha, actor, quote, reference, mode):
    rec = record(state, stage)
    if not rec or rec['digest'] != sha:
        raise ValueError('确认版本已过期；先查看当前确认页')
    if statuses(case, state)[stage] not in ('ready', 'confirmed'):
        raise ValueError('阶段未就绪：关键缺口、上游确认或附件版本尚未满足')
    if not all(isinstance(v, str) and v.strip() for v in (actor, quote, reference)):
        raise ValueError('确认需记录确认人、原话/授权及会话定位')
    if mode not in ('user', 'delegated'):
        raise ValueError('确认模式必须为 user/delegated')
    # This records supplied evidence; it cannot authenticate the speaker.
    confirmation = {'digest': sha, 'actor': actor, 'quote': quote, 'reference': reference, 'mode': mode, 'at': now()}
    rec['confirmation'] = confirmation
    state['events'].append({'action': 'confirm', 'stage': stage, **confirmation})
    save(case / 'workflow/state.json', state)
    render(case, state)


FIELD_LABELS = {
    'technical_problem': '要解决的技术问题', 'purpose': '发明目的',
    'exploration': '主动挖掘与推荐', 'problem_reframing': '重新审视技术问题', 'scope_reason': '用户限定范围的依据',
    'assumptions': '前提检查', 'premise': '原有前提', 'challenge': '值得质疑之处', 'check': '核实办法',
    'opportunities': '可选机会', 'direction': '建议方向', 'expected_effect': '预期效果（尚需验证）',
    'grounding': '依据类别', 'risk': '风险', 'cost': '实施代价', 'validation': '最小验证动作',
    'disposition': '讨论处置', 'recommendation': '推荐与取舍', 'opportunity_id': '推荐机会',
    'next_action': '建议下一步',
    'gaps': '缺口与处置', 'id': '编号', 'question': '问题', 'status': '状态', 'blocking': '是否阻断',
    'resolution': '处置依据', 'sources': '证据来源', 'kind': '类型', 'locator': '定位', 'version': '版本',
    'path': '文件', 'facts': '技术事实', 'statement': '内容', 'source_ids': '来源编号',
    'technical_chain': '技术链', 'problem': '技术问题', 'input': '输入', 'processing': '处理',
    'output': '输出', 'effect': '效果', 'candidates': '候选比较', 'mechanism': '作用机理',
    'tradeoff': '取舍与风险', 'features': '必要特征', 'description': '描述', 'fact_ids': '事实编号',
    'selected_candidate': '选定主线', 'mode': '检索方式', 'cutoff_date': '检索截止日',
    'limitations': '检索边界', 'reason': '原因', 'queries': '检索记录', 'query': '检索式',
    'database': '数据库', 'searched_at': '检索时间', 'result': '结果', 'documents': '对比文献',
    'publication': '公开号/文献名称', 'date': '公开日期', 'url': '来源链接', 'scope': '核验范围',
    'comparisons': '逐项特征对比', 'document_id': '文献编号', 'feature_id': '特征编号',
    'finding': '对比发现', 'differences': '区别特征', 'reverse_queries': '反向检索',
    'implication': '对主线的影响', 'conclusion': '初步结论', 'search_boundary': '检索结论边界',
    'effects': '效果及依据', 'evidence': '证据', 'embodiments': '端到端实施例', 'steps': '步骤',
    'support': '保护点支撑', 'section': '正文定位', 'embodiment_id': '实施例编号',
    'disclosure_file': '起草输入', 'basis_digest': '起草依据版本', 'artifacts': '交付文件',
}
VALUE_LABELS = {'expand': '主动发散', 'bounded': '按用户限定范围', 'evidence': '已有方案新解读（有据）',
                'hypothesis': '待核实线索', 'consider': '待讨论', 'explore': '同意探索（不等于已实现）',
                'defer': '延期', 'reject': '不采用',
                'source-backed': '资料有据', 'user-confirmed': '用户口述确认', 'inferred': '推断',
                'proposal': '研发建议', 'unknown': '未知', 'open': '未解决', 'resolved': '已解决',
                'excluded': '已排除', 'core': '核心', 'dependent': '从属', 'rejected': '淘汰',
                'measured': '实测', 'mechanism': '机理依据', 'unavailable': '未执行外部检索',
                'executed': '已执行检索', 'pending-search': '待检索候选',
                'preliminary-candidate': '初步候选', 'high-risk': '高风险'}


def human_lines(value, level=0):
    prefix = '  ' * level
    if isinstance(value, dict):
        lines = []
        for key, item in value.items():
            label = FIELD_LABELS.get(key, key)
            if isinstance(item, (dict, list)):
                lines.append(f'{prefix}- **{label}**：')
                lines.extend(human_lines(item, level + 1))
            else:
                display = VALUE_LABELS.get(str(item), str(item))
                if isinstance(item, bool):
                    display = '是' if item else '否'
                elif key in ('path', 'disclosure_file') and isinstance(item, str) and item:
                    from urllib.parse import quote
                    display = f'[{item}](../{quote(item)})'
                lines.append(f'{prefix}- **{label}**：{display}')
        return lines
    if isinstance(value, list):
        if not value:
            return [prefix + '- 无']
        lines = []
        for index, item in enumerate(value, 1):
            if isinstance(item, (dict, list)):
                lines.append(f'{prefix}- **第 {index} 项**')
                lines.extend(human_lines(item, level + 1))
            else:
                lines.append(f'{prefix}- {item}')
        return lines
    return [prefix + str(value)]


def render(case, state):
    status = statuses(case, state)
    current = next((s for s in STAGES if status[s] != 'confirmed'), None)
    lines = [f"# {state['title']}：阶段总览", '', f"当前：{LABELS[current] if current else '全部阶段已确认'}", '', '| 阶段 | 版本 | 状态 | 确认页 |', '|---|---|---|---|']
    for stage in STAGES:
        rec = record(state, stage)
        lines.append(f"| {LABELS[stage]} | {rec['version'] if rec else '-'} | {STATUS_LABELS[status[stage]]} | [查看内容](reviews/{stage}.md) |")
        page = [f'# {LABELS[stage]}确认页', '', f'状态：{STATUS_LABELS[status[stage]]}', '']
        if rec:
            page += [f"版本：v{rec['version']}；确认摘要：`{rec['digest']}`", '']
            if rec.get('invalidated_by'):
                page += [f"需要重审：上游「{LABELS[rec['invalidated_by']]}」已经更新。请更新本阶段内容后重新提交。", '']
            waiting = [LABELS[s] for s in STAGES[:STAGES.index(stage)] if status[s] != 'confirmed']
            if waiting:
                page += ['前置阶段尚未通过：' + '、'.join(waiting), '']
            try:
                data = data_for(case, state, stage)
                page += ['## 本轮结论', '', str(data.get('summary', '')), '', '## 需要核对的决定', '', str(data.get('decision', '')), '', '## 当前一问', '', str(data.get('next_question') or '无新增问题；核对下列具体内容。'), '']
                page += ['## 具体内容', '']
                if stage == 'basis':
                    overview = read(inside(case, rec['snapshot'])).get('disclosure_overview')
                    if overview:
                        page += ['### 技术问题与发明目的', ''] + human_lines(overview) + ['']
                    else:
                        page += ['本版本未保存发明目的预览；重新提交起草依据后生成。', '']
                for key, value in data.items():
                    if key in ('summary', 'decision', 'next_question'):
                        continue
                    page += [f'### {FIELD_LABELS.get(key, key)}', ''] + human_lines(value) + ['']
                for error in rec['errors'] + integrity(case, rec):
                    page += [f'- 阻断：{error}']
                if rec.get('confirmation'):
                    c = rec['confirmation']
                    page += ['', f"确认记录：{c['actor']} / {c['mode']} / {c['reference']}", '', c['quote']]
            except (OSError, ValueError, KeyError):
                page += ['快照不可读取，不能使用此版本继续。']
        else:
            page += ['尚未提交。填写对应 drafts JSON 后运行 submit。']
        target = case / f'reviews/{stage}.md'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text('\n'.join(page) + '\n', encoding='utf-8')
    lines += ['', '状态说明：ready=可核对；blocked=缺口或上游未通过；stale=需按新上游复核；tampered=快照或附件变化。', '', '确认仅记录用户提供的事实/取舍，不是法律结论，也不能证明发言人身份。']
    (case / 'REVIEW.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return status


def ensure_export(case, input_path):
    state = load(case)
    status = statuses(case, state)
    if any(status[s] != 'confirmed' for s in STAGES[:4]):
        raise ValueError('导出前 facts/mining/search/basis 必须为当前版本已确认状态')
    basis = data_for(case, state, 'basis')
    expected = inside(case, basis['disclosure_file'])
    if expected != Path(input_path).resolve():
        raise ValueError('导出输入不是本次已确认的 disclosure_file')
    return state


def export_case(case, output):
    state = load(case)
    basis = data_for(case, state, 'basis')
    input_path = inside(case, basis.get('disclosure_file', ''))
    ensure_export(case, input_path)
    output = inside(case, output)
    if output.suffix != '.docx':
        raise ValueError('输出必须为 .docx')
    report_path = output.with_suffix('.quality.json')
    if any(p.exists() for p in (output, output.with_suffix('.md'), report_path, output.parent/(output.stem+'_figures'))):
        raise ValueError('交付路径已使用，请选择新的版本文件名，不覆盖旧稿或附件')
    command = [sys.executable, str(ROOT/'scripts/generate_docx.py'), '--input', str(input_path), '--output', str(output), '--with-markdown', '--workflow-case', str(case), '--validation-report', str(report_path)]
    subprocess.run(command, check=True)
    ensure_export(case, input_path)
    files = [('docx', output), ('markdown', output.with_suffix('.md')), ('quality', report_path)]
    files.extend(('figure', p) for p in sorted((output.parent/(output.stem+'_figures')).rglob('*')) if p.is_file())
    payload = {'summary': '已生成正文、Word、附图和机器校验报告，请审阅具体稿件。', 'decision': '核对本版交底书与已确认起草依据是否一致。', 'next_question': '', 'gaps': [], 'basis_digest': record(state, 'basis')['digest'], 'artifacts': [{'kind': k, 'path': str(p.relative_to(case))} for k, p in files]}
    return submit(case, state, 'delivery', payload)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case-dir', required=True, type=Path)
    commands = parser.add_subparsers(dest='command', required=True)
    init_parser = commands.add_parser('init')
    init_parser.add_argument('--title', required=True)
    commands.add_parser('status')
    submit_parser = commands.add_parser('submit')
    submit_parser.add_argument('stage', choices=STAGES)
    submit_parser.add_argument('--input', type=Path, help='默认读取案件 drafts/<stage>.json')
    confirm_parser = commands.add_parser('confirm')
    confirm_parser.add_argument('stage', choices=STAGES)
    for name in ('digest', 'actor', 'quote', 'reference'):
        confirm_parser.add_argument('--'+name, required=True)
    confirm_parser.add_argument('--mode', choices=('user', 'delegated'), default='user')
    export_parser = commands.add_parser('export')
    export_parser.add_argument('--output', default='deliverables/disclosure_v1.docx')
    args = parser.parse_args()
    case = args.case_dir.resolve()
    try:
        if args.command == 'init':
            init(case, args.title)
        else:
            with locked(case):
                state = load(case)
                if args.command == 'submit':
                    rec = submit(case, state, args.stage, read(args.input or case/f'drafts/{args.stage}.json'))
                    if rec['errors']:
                        print(json.dumps({'errors': rec['errors']}, ensure_ascii=False, indent=2))
                        return 2
                elif args.command == 'confirm':
                    confirm(case, state, args.stage, args.digest, args.actor, args.quote, args.reference, args.mode)
                elif args.command == 'export':
                    export_case(case, args.output)
                else:
                    render(case, state)
        print(json.dumps(statuses(case, load(case)), ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        print(f'工作流失败: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
