"""Fill the supplied form: preserve original field paragraphs and page settings."""
from copy import deepcopy
from pathlib import Path
import zipfile
from lxml import etree as ET
from template_contract import TITLE, INSTRUCTION, HEADINGS

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS = {'w': W}


def child(parent, name, **attrs):
    item = parent.find(f'{{{W}}}{name}')
    if item is None:
        item = ET.SubElement(parent, f'{{{W}}}{name}')
    for key, value in attrs.items():
        item.set(f'{{{W}}}{key}', str(value))
    return item


def paragraph_text(paragraph):
    return ''.join(t.text or '' for t in paragraph.findall('.//w:t', NS))


def apply_layout(path: Path, payload: dict, template_path: Path):
    with zipfile.ZipFile(template_path) as archive:
        source_entries = {n: archive.read(n) for n in archive.namelist()}
    template = ET.fromstring(source_entries['word/document.xml'])
    source_body = template.find('w:body', NS)
    fixed = {paragraph_text(p): p for p in source_body.findall('.//w:p', NS) if paragraph_text(p)}
    expected = (TITLE, INSTRUCTION, *HEADINGS)
    if tuple(fixed) != expected:
        raise ValueError('转换模板与栏目契约不一致；请同步原模板转换副本及 template_contract.py')
    with zipfile.ZipFile(path) as archive:
        entries = {name: archive.read(name) for name in archive.namelist()}
    document = ET.fromstring(entries['word/document.xml'])
    body = document.find('w:body', NS)

    # Pandoc owns picture/list relationships. Import source numbering under fresh IDs.
    numbering = ET.fromstring(entries.get('word/numbering.xml', f'<w:numbering xmlns:w="{W}"/>'.encode()))
    num_map = {}
    if 'word/numbering.xml' in source_entries:
        source_numbering = ET.fromstring(source_entries['word/numbering.xml'])
        abstract_map = {}
        for tag, attr, mapping in [('abstractNum','abstractNumId',abstract_map), ('num','numId',num_map)]:
            next_id = max([int(e.get(f'{{{W}}}{attr}')) for e in numbering.findall(f'w:{tag}', NS)] or [0])+1
            for element in source_numbering.findall(f'w:{tag}', NS):
                clone = deepcopy(element)
                mapping[element.get(f'{{{W}}}{attr}')] = str(next_id)
                clone.set(f'{{{W}}}{attr}', str(next_id)); next_id += 1
                if tag == 'num':
                    ref = clone.find('w:abstractNumId', NS)
                    ref.set(f'{{{W}}}val', abstract_map[ref.get(f'{{{W}}}val')])
                numbering.append(clone)

    # Use the blank answer paragraph following “具体技术内容” as the body prototype.
    paragraphs = source_body.findall('.//w:p', NS)
    anchor = paragraphs.index(fixed['具体技术内容：'])
    answer = next((p for p in paragraphs[anchor+1:] if not paragraph_text(p)), fixed['具体技术内容：'])
    answer_ppr = answer.find('w:pPr', NS)
    answer_rpr = answer.find('w:r/w:rPr', NS)
    if answer_rpr is None and answer_ppr is not None:
        answer_rpr = answer_ppr.find('w:rPr', NS)
    for paragraph in list(body.findall('w:p', NS)):
        text = paragraph_text(paragraph)
        if text in fixed:
            clone = deepcopy(fixed[text])
            # Preserve the form's actual numbering and all source run typography.
            for num in clone.findall('.//w:numId', NS):
                num.set(f'{{{W}}}val', num_map.get(num.get(f'{{{W}}}val'), num.get(f'{{{W}}}val')))
            if text != INSTRUCTION:
                child(child(clone, 'pPr'), 'keepNext', val=1)
            body.replace(paragraph, clone)
            continue
        ppr = child(paragraph, 'pPr')
        # Template body format, without carrying empty-form numbering to answers.
        for name in ('spacing','ind','jc'):
            original = answer_ppr.find(f'w:{name}', NS) if answer_ppr is not None else None
            existing = ppr.find(f'w:{name}', NS)
            if existing is not None:
                ppr.remove(existing)
            if original is not None:
                ppr.append(deepcopy(original))
        style = ppr.find('w:pStyle', NS)
        if style is not None and style.get(f'{{{W}}}val','').startswith('Heading'):
            raise ValueError('模板外新增标题: '+text)
        child(ppr, 'pStyle', val='Normal')
        child(ppr, 'spacing', before=0, after=0, line=240, lineRule='auto')
        for run in paragraph.findall('w:r', NS):
            rpr = child(run, 'rPr')
            child(rpr, 'color', val='000000')
            for name in ('rFonts','sz','szCs','lang'):
                original = answer_rpr.find(f'w:{name}', NS) if answer_rpr is not None else None
                if original is not None:
                    existing = rpr.find(f'w:{name}', NS)
                    if existing is not None:
                        rpr.remove(existing)
                    rpr.append(deepcopy(original))
        extent = paragraph.find('.//{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}extent')
        if extent is not None:
            child(ppr, 'jc', val='center')
            child(ppr, 'keepNext', val=1)
            cx, cy = int(extent.get('cx')), int(extent.get('cy'))
            ratio = min(1, 5040000/cx, 6480000/cy)
            for element in paragraph.iter():
                if ET.QName(element).localname in ('extent','ext') and element.get('cx') == str(cx) and element.get('cy') == str(cy):
                    element.set('cx', str(int(cx*ratio))); element.set('cy', str(int(cy*ratio)))
    # Keep image and caption in one unbreakable paragraph inside a split table row.
    # Word's keepNext alone is not consistently honored by LibreOffice in cells.
    for paragraph in list(body.findall('w:p', NS)):
        if paragraph.find('.//w:drawing', NS) is None:
            continue
        following = paragraph.getnext()
        if following is not None and following.tag == f'{{{W}}}p' and paragraph_text(following).startswith('图'):
            run = ET.SubElement(paragraph, f'{{{W}}}r')
            ET.SubElement(run, f'{{{W}}}br')
            for item in list(following):
                if item.tag != f'{{{W}}}pPr':
                    paragraph.append(deepcopy(item))
            body.remove(following)
            child(child(paragraph, 'pPr'), 'keepLines', val=1)
    # Insert generated answers into the original eight-row form, retaining tcPr,
    # row minimum heights, borders, grid, original field runs and section setup.
    answers = {h: [] for h in HEADINGS}
    current = None
    for paragraph in body.findall('w:p', NS):
        text = paragraph_text(paragraph)
        if text in HEADINGS:
            current = text
        elif current is not None:
            answers[current].append(deepcopy(paragraph))
    new_body = deepcopy(source_body)
    for cell in new_body.findall('.//w:tc', NS):
        for paragraph in list(cell.findall('w:p', NS)):
            text = paragraph_text(paragraph)
            if not text:
                cell.remove(paragraph)
                continue
            position = cell.index(paragraph)+1
            for answer in answers.get(text, []):
                cell.insert(position, answer); position += 1
    # Source header/footer IDs must map to the generated package's own relations.
    R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
    REL = 'http://schemas.openxmlformats.org/package/2006/relationships'
    rels = ET.fromstring(entries['word/_rels/document.xml.rels'])
    src_rels = ET.fromstring(source_entries['word/_rels/document.xml.rels'])
    content_types = ET.fromstring(entries['[Content_Types].xml'])
    CT = 'http://schemas.openxmlformats.org/package/2006/content-types'
    source_by_id = {r.get('Id'): r for r in src_rels}
    for ref in new_body.findall('w:sectPr/*', NS):
        rid = ref.get(f'{{{R}}}id')
        if rid is None:
            continue
        original = source_by_id[rid]
        part = original.get('Target')
        kind = original.get('Type').rsplit('/', 1)[-1]
        new_part = 'template_' + part
        new_id = 'rIdTemplate' + kind
        ET.SubElement(rels, f'{{{REL}}}Relationship', Id=new_id, Type=original.get('Type'), Target=new_part)
        entries['word/'+new_part] = source_entries['word/'+part]
        ET.SubElement(content_types, f'{{{CT}}}Override', PartName='/word/'+new_part,
                      ContentType='application/vnd.openxmlformats-officedocument.wordprocessingml.'+kind+'+xml')
        ref.set(f'{{{R}}}id', new_id)
    entries['word/_rels/document.xml.rels'] = ET.tostring(rels, encoding='UTF-8', xml_declaration=True)
    entries['[Content_Types].xml'] = ET.tostring(content_types, encoding='UTF-8', xml_declaration=True)
    document = deepcopy(template)
    document.replace(document.find('w:body', NS), new_body)
    entries['word/settings.xml'] = source_entries['word/settings.xml']
    entries['word/document.xml'] = ET.tostring(document, encoding='UTF-8', xml_declaration=True)
    entries['word/numbering.xml'] = ET.tostring(numbering, encoding='UTF-8', xml_declaration=True)
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, data in entries.items():
            archive.writestr(name, data)
