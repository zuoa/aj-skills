"""Apply the supplied disclosure form without changing the source template."""
from copy import deepcopy
from pathlib import Path
import zipfile
from lxml import etree as ET

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS = {'w': W}

# Half-point font sizes and twip spacing. Preserve the user's form geometry.
HEADING_TOKENS = {
    'Heading1': (32, 280, 140),
    'Heading2': (28, 240, 120),  # Five numbered questions: 14 pt
    'Heading3': (24, 200, 100),  # Topic subsections: 12 pt
    'Heading4': (22, 140, 80),   # Steps and detailed labels: 11 pt
    'Heading5': (21, 120, 60),
    'Heading6': (21, 120, 60),
}

def child(parent, name, **attrs):
    item = parent.find(f'{{{W}}}{name}')
    if item is None:
        item = ET.SubElement(parent, f'{{{W}}}{name}')
    for key, value in attrs.items():
        item.set(f'{{{W}}}{key}', str(value))
    return item


def apply_layout(path: Path, payload: dict, template_path: Path):
    with zipfile.ZipFile(template_path) as archive:
        template = ET.fromstring(archive.read('word/document.xml'))
    with zipfile.ZipFile(path) as archive:
        entries = {name: archive.read(name) for name in archive.namelist()}
    document = ET.fromstring(entries['word/document.xml'])
    body = document.find('w:body', NS)
    table = deepcopy(template.find('.//w:tbl', NS))
    rows = table.findall('w:tr', NS)

    def fill(cell, text):
        paragraph = cell.find('w:p', NS)
        props = deepcopy(paragraph.find('w:pPr', NS))
        run_props = paragraph.find('w:r/w:rPr', NS)
        run_props = deepcopy(run_props) if run_props is not None else ET.Element(f'{{{W}}}rPr')
        for element in list(cell):
            if element.tag != f'{{{W}}}tcPr':
                cell.remove(element)
        paragraph = ET.SubElement(cell, f'{{{W}}}p')
        if props is not None:
            paragraph.append(props)
        run = ET.SubElement(paragraph, f'{{{W}}}r')
        child(run_props, 'color', val='000000')
        run.append(run_props)
        ET.SubElement(run, f'{{{W}}}t').text = str(text or '')

    fill(rows[1].find('w:tc', NS), payload.get('title'))
    fields = rows[3].findall('w:tc', NS)
    fill(fields[0], '、'.join(payload.get('inventors', [])))
    fill(fields[1], payload.get('department'))
    fill(rows[4].findall('w:tc', NS)[1], payload.get('first_inventor_id'))
    existing = body.find('w:tbl', NS)
    if existing is None:
        raise ValueError('生成文档缺少模板首页信息表')
    body.replace(existing, table)
    section = deepcopy(template.find('.//w:sectPr', NS))
    for old in body.findall('w:sectPr', NS):
        body.remove(old)
    body.append(section)

    # Keep 10.5 pt Songti answers; give headings an explicit bold type ladder.
    styles = ET.fromstring(entries['word/styles.xml'])
    # This supplied form has no Heading2/3/4 definitions. Pandoc can reference
    # absent styles, so editing only existing styles would leave headings flat.
    existing_ids = {s.get(f'{{{W}}}styleId') for s in styles.findall('w:style', NS)}
    normal = next((s.get(f'{{{W}}}styleId') for s in styles.findall('w:style', NS)
                   if s.find('w:name', NS) is not None and s.find('w:name', NS).get(f'{{{W}}}val') == 'Normal'), 'Normal')
    for sid in (*HEADING_TOKENS, 'BodyText', 'FirstParagraph', 'Compact'):
        if sid not in existing_ids:
            style = ET.SubElement(styles, f'{{{W}}}style', {f'{{{W}}}type': 'paragraph', f'{{{W}}}styleId': sid})
            child(style, 'name', val=('heading ' + sid[-1]) if sid.startswith('Heading') else sid)
            child(style, 'basedOn', val=normal)
            child(style, 'next', val=normal)
            if sid.startswith('Heading'):
                child(style, 'qFormat')
                child(child(style, 'pPr'), 'outlineLvl', val=int(sid[-1])-1)
    for style in styles.findall('w:style', NS):
        if style.get(f'{{{W}}}type') != 'paragraph':
            continue
        sid = style.get(f'{{{W}}}styleId', '')
        props = child(style, 'rPr')
        font = child(props, 'rFonts')
        font.attrib.clear()
        family = '微软雅黑' if sid.startswith('Heading') else '宋体'
        for key in ('ascii', 'hAnsi', 'eastAsia'):
            font.set(f'{{{W}}}{key}', family)
        size, before, after = HEADING_TOKENS.get(sid, (21, 0, 60))
        child(props, 'sz', val=size)
        child(props, 'szCs', val=size)
        child(props, 'color', val='000000')
        ppr = child(style, 'pPr')
        child(ppr, 'spacing', before=before, after=after, line=288, lineRule='auto')
        child(ppr, 'jc', val='left')
        if sid.startswith('Heading'):
            child(props, 'b', val=1)
            child(props, 'bCs', val=1)
            child(props, 'i', val=0)
            child(props, 'iCs', val=0)
            child(ppr, 'keepNext', val=1)
            child(ppr, 'keepLines', val=1)
            child(ppr, 'pageBreakBefore', val=0)
            child(ppr, 'ind', left=0, right=0, firstLine=0)
        child(ppr, 'widowControl')

    # Use actual Word numbering for the five questions, matching the template.
    numbering = ET.fromstring(entries['word/numbering.xml'])
    abstract_id = 1 + max([int(x.get(f'{{{W}}}abstractNumId')) for x in numbering.findall('w:abstractNum', NS)] or [0])
    num_id = 1 + max([int(x.get(f'{{{W}}}numId')) for x in numbering.findall('w:num', NS)] or [0])
    abstract = ET.SubElement(numbering, f'{{{W}}}abstractNum', {f'{{{W}}}abstractNumId': str(abstract_id)})
    level = child(abstract, 'lvl', ilvl=0)
    child(level, 'start', val=1)
    child(level, 'numFmt', val='decimal')
    child(level, 'lvlText', val='%1、')
    num = ET.SubElement(numbering, f'{{{W}}}num', {f'{{{W}}}numId': str(num_id)})
    child(num, 'abstractNumId', val=abstract_id)
    for paragraph in body.findall('w:p', NS):
        ppr = child(paragraph, 'pPr')
        style = ppr.find('w:pStyle', NS)
        if style is not None and style.get(f'{{{W}}}val') in HEADING_TOKENS:
            # Imported template direct formatting must not flatten heading styles.
            for rpr in paragraph.findall('.//w:rPr', NS):
                for name in ('rFonts', 'sz', 'szCs', 'b', 'bCs', 'i', 'iCs', 'color'):
                    for old in rpr.findall(f'w:{name}', NS):
                        rpr.remove(old)
        if style is not None and style.get(f'{{{W}}}val') == 'Heading2':
            props = child(ppr, 'numPr')
            child(props, 'ilvl', val=0)
            child(props, 'numId', val=num_id)
        extent = paragraph.find('.//{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}extent')
        if extent is not None:
            child(ppr, 'jc', val='center')
            child(ppr, 'keepNext')
            cx, cy = int(extent.get('cx')), int(extent.get('cy'))
            ratio = min(1, 5040000/cx, 6480000/cy)
            for el in paragraph.iter():
                if ET.QName(el).localname in ('extent', 'ext') and el.get('cx') == str(cx) and el.get('cy') == str(cy):
                    el.set('cx', str(int(cx*ratio)))
                    el.set('cy', str(int(cy*ratio)))
    for name, tree in [('word/document.xml', document), ('word/styles.xml', styles), ('word/numbering.xml', numbering)]:
        entries[name] = ET.tostring(tree, encoding='UTF-8', xml_declaration=True)
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, data in entries.items():
            archive.writestr(name, data)
