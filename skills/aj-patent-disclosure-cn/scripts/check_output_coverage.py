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
QUESTIONS = (
    '本发明的关键点和欲保护点是什么？',
    '与现有技术相比，本发明有何优点？',
    '本发明是否经过实验、模拟、使用而证明可行，结果如何？',
    '本发明的变更设计（替代方案）及其它用途：',
    '附图及说明',
)
SUBHEADINGS = ('关键技术点和欲保护点', '技术领域', '背景技术', '要解决的技术问题', '发明目的', '技术方案', '具体实施方式')


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
    # source/status/risk are deliberately internal in generic list records.
    internal = ('status', 'evidence_status', 'source', 'risk', 'id', 'num')
    groups = []
    def add(label, value, path, section, required=False, skip=()):
        anchor = None
        if section == 0:
            anchor = {'$.protection_points': '关键技术点和欲保护点', '$.technical_field': '技术领域',
                      '$.terminology': '术语定义', '$.background': '背景技术',
                      '$.invention.technical_problem': '要解决的技术问题', '$.invention.purpose': '发明目的',
                      '$.embodiments': '具体实施方式'}.get(path, '技术方案')
        groups.append({'label': label, 'section': section, 'required': required,
                       'anchor': anchor,
                       'fragments': list(leaves(value, path, skip))})
    add('发明名称', payload.get('title'), '$.title', -1, True)
    for key in ('inventors', 'department', 'first_inventor_id'):
        add(key, payload.get(key), '$.'+key, -1)
    add('关键点和欲保护点', payload.get('protection_points') or inv.get('key_features'), '$.protection_points', 0, True, internal)
    for key in ('technical_field', 'terminology', 'background'):
        add(key, payload.get(key), '$.'+key, 0, key != 'terminology', internal)
    for key in ('technical_problem', 'purpose', 'solution', 'inputs', 'key_features', 'solution_steps', 'outputs'):
        # IDs of structured steps are displayed and must survive the export.
        skip = internal if key != 'solution_steps' else ('status', 'evidence_status', 'source', 'risk')
        add(key, inv.get(key), '$.invention.'+key, 0, key in ('technical_problem', 'purpose', 'solution_steps'), skip)
    add('参考资料', payload.get('references'), '$.references', 0, skip=internal)
    add('具体实施方式', payload.get('embodiments'), '$.embodiments', 0, True, ('status', 'evidence_status', 'source', 'risk'))
    add('技术效果', inv.get('effects'), '$.invention.effects', 1, True, internal)
    add('验证情况', payload.get('verification'), '$.verification', 2, True)
    add('替代方案', inv.get('alternatives') or payload.get('alternative_statement'), '$.alternatives', 3, True, internal)
    add('其它用途', payload.get('other_uses'), '$.other_uses', 3, skip=internal)
    for i, figure in enumerate(payload.get('figures', [])):
        if isinstance(figure, dict):
            add(f'附图{i+1}', {k: figure.get(k) for k in ('caption', 'elements')}, f'$.figures[{i}]', 4, True)
    if not payload.get('figures'):
        add('附图不适用说明', payload.get('drawings_not_applicable'), '$.drawings_not_applicable', 4, True)
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
        errors.append({'code': 'output-sections', 'path': 'markdown', 'message': '五个正文主章节缺失、重复或顺序错误'})
    md_headings = re.findall(r'^###\s+(.+?)\s*$', markdown, re.M)
    for heading in SUBHEADINGS:
        if heading not in md_headings:
            errors.append({'code': 'output-subheading', 'path': 'markdown', 'message': '缺少小节: '+heading})
    if docx is not None:
        try:
            with zipfile.ZipFile(docx) as archive:
                tree = ET.fromstring(archive.read('word/document.xml'))
                styles = ET.fromstring(archive.read('word/styles.xml'))
                style_map = {s.get(f'{{{W}}}styleId'): s for s in styles.findall('w:style', NS)}
                for sid in ('Heading2', 'Heading3', 'Heading4'):
                    style = style_map.get(sid)
                    if style is None:
                        errors.append({'code': 'output-heading-style', 'path': sid, 'message': 'Word 缺少实际标题样式定义'})
                        continue
                    bold = style.find('w:rPr/w:b', NS)
                    size = style.find('w:rPr/w:sz', NS)
                    keep = style.find('w:pPr/w:keepNext', NS)
                    if (bold is None or bold.get(f'{{{W}}}val', '1') in ('0', 'false', 'off')
                        or size is None or int(size.get(f'{{{W}}}val', '0')) <= 21
                        or keep is None or keep.get(f'{{{W}}}val', '1') in ('0', 'false', 'off')):
                        errors.append({'code': 'output-heading-style', 'path': sid, 'message': '标题未显式加粗、放大或与下段保持同页'})
                body = tree.find('w:body', NS)
                blocks, subheads = [], []
                for element in body:
                    text = ''.join(element.itertext()) if element.tag != f'{{{W}}}p' else ''.join(t.text or '' for t in element.findall('.//w:t', NS))
                    style = element.find('w:pPr/w:pStyle', NS)
                    sid = style.get(f'{{{W}}}val') if style is not None else ''
                    if sid == 'Heading3':
                        subheads.append(text)
                    # Caption alt text is useful for accessibility but cannot stand in for body text.
                    blocks.append((text if sid in ('Heading2', 'Heading3') else None, text))
                channels['docx'], seen = sections(blocks)
                if seen != list(QUESTIONS):
                    errors.append({'code': 'output-sections', 'path': 'docx', 'message': 'Word 五个正文主章节不完整或顺序错误'})
                for heading in SUBHEADINGS:
                    if heading not in subheads:
                        errors.append({'code': 'output-subheading', 'path': 'docx', 'message': 'Word 缺少小节: '+heading})
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
    return {'errors': errors, 'coverage': checks, 'scope': '检查输入到章节的文本覆盖、结构和图片嵌入；不证明事实真实性或技术充分性，不替代视觉审阅。'}


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
