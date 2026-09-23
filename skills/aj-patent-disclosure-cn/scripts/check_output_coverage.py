#!/usr/bin/env python3
"""Compare declared disclosure content with actual Markdown and DOCX output.

Checks text coverage and image embedding, not factual truth or visual layout.
"""
from __future__ import annotations
import argparse
import json
import re
import unicodedata
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS = {'w': W}
from template_contract import TITLE, INSTRUCTION, OUTLINE, HEADINGS, LEAF_HEADINGS, FALLBACK
QUESTIONS = HEADINGS
SUBHEADINGS = ()


def norm(value):
    text = unicodedata.normalize('NFKC', str(value))
    # Ignore Markdown link targets and inline syntax while preserving visible text.
    text = re.sub(r'!?\[([^\]]*)\]\([^)]*\)', r'\1', text)
    return ''.join(c for c in text if c.isalnum())


def meaningful(value):
    if isinstance(value, dict):
        return any(meaningful(v) for v in value.values())
    if isinstance(value, list):
        return any(meaningful(v) for v in value)
    return value is not None and bool(norm(value))


def leaves(value, path, skip=()):
    if isinstance(value, dict):
        for key, child in value.items():
            if key not in skip:
                yield from leaves(child, f'{path}.{key}', skip)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from leaves(child, f'{path}[{index}]', skip)
    elif meaningful(value):
        yield path, value


def content_groups(payload):
    inv = payload.get('invention', {})
    background = payload.get('background', {})
    internal = ('status', 'evidence_status', 'source', 'risk', 'id', 'num')
    groups = []
    def add(label, value, path, heading, required=False, skip=(), display=False, fallback=False):
        groups.append({'label': label, 'section': HEADINGS.index(heading), 'anchor': None,
                       'heading': heading, 'required': required, 'value': value, 'skip': skip,
                       'display_label': display, 'fallback': fallback,
                       'fragments': list(leaves(value, path, skip))})
    add('发明名称', payload.get('title'), '$.title', HEADINGS[0], True)
    for key, label in [('applicant', '申请人'), ('inventors', '发明人')]:
        add(label, payload.get(key), '$.'+key, HEADINGS[1], display=True, fallback=True)
    prior = payload.get('existing_technology', {})
    if not isinstance(prior, dict):
        prior = {}
    add('现有技术名称', prior.get('name'), '$.existing_technology.name', HEADINGS[3])
    add('现有技术来源', prior.get('source'), '$.existing_technology.source', HEADINGS[4])
    if isinstance(background, dict):
        scheme = {k: v for k,v in background.items() if k != 'limitations'}
        limitations = background.get('limitations')
    else:
        scheme, limitations = background, None
    add('背景技术', scheme, '$.background', HEADINGS[5], True, internal)
    add('现有技术方案', prior.get('solution'), '$.existing_technology.solution', HEADINGS[5])
    add('现有技术不足', limitations, '$.background.limitations', HEADINGS[6], skip=internal)
    add('现有技术不足补充', prior.get('limitations'), '$.existing_technology.limitations', HEADINGS[6])
    add('技术问题', inv.get('technical_problem'), '$.invention.technical_problem', HEADINGS[8], True)
    add('技术效果', inv.get('effects'), '$.invention.effects', HEADINGS[9], True, internal)
    target = HEADINGS[11]
    add('关键技术点和欲保护点', payload.get('protection_points') or inv.get('key_features'), '$.protection_points', target, True, internal, True)
    for key,label in [('technical_field','技术领域'), ('terminology','术语定义')]:
        add(label, payload.get(key), '$.'+key, target, key == 'technical_field', internal, True)
    for key,label in [('purpose','发明目的'), ('solution','技术方案'), ('inputs','输入'),
                      ('key_features','必要技术特征'), ('solution_steps','处理步骤'), ('outputs','输出')]:
        skip = internal if key != 'solution_steps' else ('status','evidence_status','source','risk')
        add(label, inv.get(key), '$.invention.'+key, target, key in ('purpose','solution_steps'), skip, True)
    add('参考资料', payload.get('references'), '$.references', target, skip=internal, display=True)
    add('具体实施方式', payload.get('embodiments'), '$.embodiments', target, True, ('status','evidence_status','source','risk'), True)
    add('替代方案', inv.get('alternatives') or payload.get('alternative_statement'), '$.alternatives', target, skip=internal, display=True)
    add('其他用途', payload.get('other_uses'), '$.other_uses', target, skip=internal, display=True)
    add('实现原理', inv.get('principle'), '$.invention.principle', HEADINGS[12])
    for i,figure in enumerate(payload.get('figures', [])):
        add(f'附图{i+1}', {k:figure.get(k) for k in ('caption','elements')}, f'$.figures[{i}]', HEADINGS[14], True)
    if not payload.get('figures'):
        add('附图不适用说明', payload.get('drawings_not_applicable'), '$.drawings_not_applicable', HEADINGS[14], True)
    add('实验数据', payload.get('verification'), '$.verification', HEADINGS[15])
    add('特定软件分析结果', payload.get('software_analysis'), '$.software_analysis', HEADINGS[16])
    add('专利申报目的', payload.get('application_purposes'), '$.application_purposes', HEADINGS[17])
    profile = payload.get('applicant_profile')
    if isinstance(profile, dict):
        for key,label in [('product_types','产品种类'),('work_content','工作内容'),('field','所属领域')]:
            add(label, profile.get(key), '$.applicant_profile.'+key, HEADINGS[18], display=True, fallback=True)
        extra = {k:v for k,v in profile.items() if k not in ('product_types','work_content','field')}
        add('背景补充', extra, '$.applicant_profile', HEADINGS[18])
    else:
        add('申请人或主要发明人背景', profile, '$.applicant_profile', HEADINGS[18])
    return groups


def check_output(payload, markdown, docx=None):
    errors, checks = [], []
    channels = {}
    def sections(blocks):
        result = {-1: []}; current = -1; seen = []; sub = None
        for heading, text in blocks:
            if heading in QUESTIONS:
                current = QUESTIONS.index(heading)
                seen.append(heading)
                result.setdefault(current, [])
                sub = None
            elif heading:
                sub = (current, heading)
                result.setdefault(sub, [])
            else:
                result.setdefault(current, []).append(text)
                if sub is not None:
                    result[sub].append(text)
        return {k: norm('\n'.join(v)) for k, v in result.items()}, seen
    md_blocks = []
    for line in markdown.splitlines():
        match = re.match(r'^#{2,3}\s+(.+?)\s*$', line)
        md_blocks.append((match[1] if match else None, line))
    channels['markdown'], md_seen = sections(md_blocks)
    if md_seen != list(QUESTIONS):
        errors.append({'code': 'output-sections', 'path': 'markdown', 'message': '模板栏目缺失、重复或顺序错误'})
    expected_outline = list(OUTLINE)
    actual_outline = [(len(m[1]), m[2]) for m in re.finditer(r'^(#{2,6})\s+(.+?)\s*$', markdown, re.M)]
    if actual_outline != expected_outline:
        errors.append({'code': 'output-outline', 'path': 'markdown', 'message': '栏目文字、层级或顺序与模板不一致'})
    if re.findall(r'^# (.+)$', markdown, re.M) != [TITLE] or INSTRUCTION not in markdown:
        errors.append({'code': 'output-template', 'path': 'markdown', 'message': '缺少原模板标题或填写说明'})
    if docx is not None:
        try:
            with zipfile.ZipFile(docx) as archive:
                tree = ET.fromstring(archive.read('word/document.xml'))
                body = tree.find('w:body', NS)
                blocks, subheads = [], []
                for element in body.findall('.//w:p', NS):
                    text = ''.join(element.itertext()) if element.tag != f'{{{W}}}p' else ''.join(t.text or '' for t in element.findall('.//w:t', NS))
                    style = element.find('w:pPr/w:pStyle', NS)
                    sid = style.get(f'{{{W}}}val') if style is not None else ''
                    if sid == 'Heading3':
                        subheads.append(text)
                    # Caption alt text is useful for accessibility but cannot stand in for body text.
                    blocks.append((text if text in HEADINGS else None, text))
                channels['docx'], seen = sections(blocks)
                if seen != list(QUESTIONS):
                    errors.append({'code': 'output-sections', 'path': 'docx', 'message': 'Word 模板栏目不完整或顺序错误'})
                texts = [text for _,text in blocks]
                if texts[:2] != [TITLE, INSTRUCTION]:
                    errors.append({'code': 'output-template', 'path': 'docx', 'message': 'Word 未保留模板标题和填写说明'})
                tables = body.findall('w:tbl', NS)
                if len(tables) != 1 or len(tables[0].findall('w:tr', NS)) != 8 or any(len(row.findall('w:tc', NS)) != 1 for row in tables[0].findall('w:tr', NS)):
                    errors.append({'code': 'output-template', 'path': 'docx', 'message': 'Word 必须保留原模板八行单列表格'})
                # Compare against the actual converted form, not renderer styling constants.
                reference = Path(__file__).resolve().parents[1] / 'assets/templates/专利申请信息及技术交底书.docx'
                with zipfile.ZipFile(reference) as source_archive:
                    source = ET.fromstring(source_archive.read('word/document.xml'))
                def signature(element):
                    if element is None:
                        return None
                    return (element.tag, tuple(sorted(element.attrib.items())), element.text or '', tuple(signature(c) for c in element))
                source_table = source.find('.//w:tbl', NS)
                if len(tables) == 1:
                    for key in ('tblPr', 'tblGrid'):
                        if signature(tables[0].find('w:'+key,NS)) != signature(source_table.find('w:'+key,NS)):
                            errors.append({'code': 'output-layout', 'path': key, 'message': '表格版式偏离源模板'})
                    for index,(row,src_row) in enumerate(zip(tables[0].findall('w:tr', NS),source_table.findall('w:tr',NS))):
                        row_headings = [''.join(p.itertext()) for p in row.findall('.//w:p',NS) if ''.join(p.itertext()) in HEADINGS]
                        expected_row = [''.join(p.itertext()) for p in src_row.findall('.//w:p',NS) if ''.join(p.itertext()) in HEADINGS]
                        if row_headings != expected_row:
                            errors.append({'code':'output-layout','path':f'row[{index}]','message':'栏目不在原模板指定单元格'})
                        if signature(row.find('w:tc/w:tcPr',NS)) != signature(src_row.find('w:tc/w:tcPr',NS)):
                            errors.append({'code':'output-layout','path':f'row[{index}]','message':'单元格边框或尺寸偏离源模板'})
                for key in ('pgSz','pgMar','docGrid'):
                    if signature(body.find('w:sectPr/w:'+key,NS)) != signature(source.find('.//w:sectPr/w:'+key,NS)):
                        errors.append({'code':'output-layout','path':key,'message':'页面版式偏离源模板'})
                source_fixed = {''.join(p.itertext()): p for p in source.findall('.//w:body//w:p', NS) if ''.join(p.itertext()) in (TITLE, INSTRUCTION, *HEADINGS)}
                for paragraph in body.findall('.//w:p',NS):
                    text = ''.join(t.text or '' for t in paragraph.findall('.//w:t',NS))
                    if text in source_fixed:
                        original = source_fixed[text]
                        if [signature(r) for r in paragraph.findall('w:r',NS)] != [signature(r) for r in original.findall('w:r',NS)]:
                            errors.append({'code':'output-layout','path':text,'message':'栏目原文或字体/高亮偏离源模板'})
                drawings = tree.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/main}blip')
                rels = ET.fromstring(archive.read('word/_rels/document.xml.rels'))
                relationships = {r.get('Id'): r for r in rels}
                embedded = []
                import posixpath
                for drawing in drawings:
                    rid = drawing.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                    rel = relationships.get(rid)
                    if rel is not None and rel.get('TargetMode') != 'External':
                        target = posixpath.normpath(posixpath.join('word', rel.get('Target', '')))
                        if target in archive.namelist() and archive.read(target):
                            embedded.append(target)
                figures = payload.get('figures', [])
                if len(embedded) < len(figures):
                    errors.append({'code': 'output-images', 'path': 'docx', 'message': '附图未全部以实际图片嵌入 Word'})
                import hashlib
                from collections import Counter
                source_files = [(Path(docx).parent / f.get('file', '')).resolve() for f in figures if isinstance(f, dict)]
                if source_files and all(p.is_file() for p in source_files):
                    expected = Counter(hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files)
                    actual = Counter(hashlib.sha256(archive.read(p)).hexdigest() for p in embedded)
                    if expected - actual:
                        errors.append({'code': 'output-images', 'path': 'docx', 'message': '嵌入附图与声明的原图片内容不匹配，存在缺图或替换'})
                elif len(set(embedded)) < len(figures):
                    errors.append({'code': 'output-images', 'path': 'docx', 'message': '多幅声明附图重复引用同一图片；需提供原图路径核验'})
        except (OSError, ValueError, KeyError, ET.ParseError, zipfile.BadZipFile) as exc:
            errors.append({'code': 'output-docx', 'path': str(docx), 'message': str(exc)})
    for figure in payload.get('figures', []):
        if isinstance(figure, dict) and (docx is not None or figure.get('file')):
            caption = f"图{figure.get('num')} {figure.get('caption')}"
            if not any(norm(alt) == norm(caption) for alt in re.findall(r'!\[([^\]]+)\]\([^\n]+\)', markdown)):
                errors.append({'code': 'output-images', 'path': 'markdown', 'message': '缺少附图图像语法: '+caption})
    for channel, output in channels.items():
        for heading in LEAF_HEADINGS:
            if not output.get(HEADINGS.index(heading)):
                errors.append({'code': 'output-empty-field', 'path': channel, 'message': '栏目不得空白: '+heading})
    for group in content_groups(payload):
        item = {'section': group['label'], 'required': group['required'], 'fragments': len(group['fragments']), 'status': 'passed'}
        if not group['fragments']:
            item['status'] = 'missing' if group['required'] else 'not_applicable'
            if group['required']:
                errors.append({'code': 'coverage-required', 'path': group['label'], 'message': '必需内容为空，不能仅靠标题通过校验'})
        for path, value in group['fragments']:
            expected = norm(value)
            if not expected:
                continue
            for channel, output in channels.items():
                location = (group['section'], group['anchor']) if group['anchor'] else group['section']
                if expected not in output.get(location, ''):
                    item['status'] = 'missing'
                    errors.append({'code': 'coverage-omitted', 'path': path, 'message': f'{channel} 对应章节未保留输入内容: {str(value)[:100]}'})
        checks.append(item)
    pending = []
    groups = content_groups(payload)
    for heading in LEAF_HEADINGS:
        matching = [g for g in groups if g['heading'] == heading]
        if not any(g['fragments'] for g in matching):
            pending.append(heading)
        else:
            pending.extend(g['label'] for g in matching if g.get('fallback') and not g['fragments'])
    for group in groups:
        if any(str(value).strip() == FALLBACK for _,value in group['fragments']):
            pending.append(group['label'])
    return {'errors': errors, 'coverage': checks, 'template_pending_fields': list(dict.fromkeys(pending)), 'scope': '检查输入到章节的文本覆盖、结构和图片嵌入；不证明事实真实性或技术充分性，不替代视觉审阅。'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--markdown', required=True, type=Path)
    parser.add_argument('--docx', type=Path)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    report = check_output(json.loads(args.input.read_text()), args.markdown.read_text(), args.docx)
    result = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(result+'\n')
    print(result)
    return 2 if report['errors'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
