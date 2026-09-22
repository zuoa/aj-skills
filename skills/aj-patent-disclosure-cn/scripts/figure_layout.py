"""Local patent diagrams: typed layout, print sizing and editable draw.io export.

Only Graphviz is required. Generated geometry is inspected mechanically; semantic
and visual approval remain separate from this report.
"""
from __future__ import annotations

import json
import math
import platform
import shutil
import subprocess
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

FONT_SIZE = 13
EDGE_SIZE = 11
MAX_WIDTH_CM = 14
MAX_HEIGHT_CM = 18
SHAPES = {'process': 'box', 'decision': 'diamond', 'start': 'ellipse',
          'end': 'ellipse', 'storage': 'cylinder', 'input': 'parallelogram',
          'output': 'parallelogram', 'subprocess': 'box', 'point': 'point'}
PORTS = {'n', 's', 'e', 'w', 'ne', 'nw', 'se', 'sw'}


def quote(value):
    return json.dumps(str(value), ensure_ascii=False)


def wrap_label(value, width=24):
    """Keep explicit line breaks; measure CJK as two columns, ASCII as one."""
    lines = []
    for paragraph in str(value).split('\n'):
        line, used = '', 0
        for char in paragraph:
            size = 0 if unicodedata.combining(char) else (2 if unicodedata.east_asian_width(char) in 'WF' else 1)
            if line and used + size > width:
                lines.append(line.strip())
                line, used = '', 0
            line += char
            used += size
        lines.append(line.strip())
    return '\n'.join(lines)


def select_font():
    candidates = ['PingFang SC', 'Noto Sans CJK SC', 'Microsoft YaHei', 'WenQuanYi Zen Hei']
    if shutil.which('fc-list'):
        try:
            fonts = subprocess.run(['fc-list', ':lang=zh', 'family'], capture_output=True,
                                   text=True, check=True, timeout=10).stdout
            for name in candidates:
                if name in fonts:
                    return name
        except (OSError, subprocess.SubprocessError):
            pass
    return 'PingFang SC' if platform.system() == 'Darwin' else 'sans-serif'


def build_dot(nodes, edges, spec=None):
    spec = spec or {}
    layout = spec.get('layout', {})
    direction = layout.get('direction', 'LR' if spec.get('kind') == 'architecture' else 'TB')
    routing = layout.get('routing', 'spline')
    if direction not in {'TB', 'LR'} or routing not in {'polyline', 'ortho', 'spline'}:
        raise ValueError('layout.direction 仅支持 TB/LR，routing 仅支持 polyline/ortho/spline')
    width = layout.get('label_columns', 24)
    if not isinstance(width, int) or not 12 <= width <= 48:
        raise ValueError('label_columns 必须为 12–48 的整数')
    spacing = {}
    for name, default in (('nodesep', 0.55), ('ranksep', 0.6)):
        value = layout.get(name, default)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0.2 <= value <= 2:
            raise ValueError(f'{name} 必须为 0.2–2 英寸的有限数值')
        spacing[name] = value
    ids = [str(n['id']) for n in nodes]
    if not ids or len(ids) != len(set(ids)):
        raise ValueError('图节点不能为空，且 id 必须唯一')
    groups = spec.get('groups', [])
    gids = [str(g['id']) for g in groups]
    if len(gids) != len(set(gids)):
        raise ValueError('分组 id 必须唯一')
    group_map = {str(g['id']): g for g in groups}
    for g in groups:
        chain, current = set(), str(g['id'])
        while current is not None:
            if current not in group_map or current in chain:
                raise ValueError('分组 parent 不存在或形成循环')
            chain.add(current)
            parent = group_map[current].get('parent')
            current = str(parent) if parent is not None else None
    for n in nodes:
        if n.get('group') is not None and str(n['group']) not in group_map:
            raise ValueError(f'节点 {n["id"]} 引用了不存在的分组')
        if n.get('type', 'process') not in SHAPES:
            raise ValueError(f'不支持的节点类型: {n.get("type")}')
    font = select_font()
    lines = ['digraph G {',
             f'graph [rankdir={direction}, splines={routing}, bgcolor=white, pad=0.18, '
             f'nodesep={spacing["nodesep"]}, ranksep={spacing["ranksep"]}, newrank=true, outputorder=edgesfirst];',
             f'node [shape=box, fontname={quote(font)}, fontsize={FONT_SIZE}, color=black, '
             'fillcolor=white, style=filled, penwidth=1.1, margin="0.18,0.12", width=1.35, height=0.5];',
             f'edge [fontname={quote(font)}, fontsize={EDGE_SIZE}, color=black, penwidth=1, arrowsize=0.7];']

    def emit_group(parent=None):
        for n in nodes:
            if (str(n['group']) if n.get('group') is not None else None) == parent:
                label = wrap_label(n.get('label', n['id']), width)
                if n.get('ref') is not None:
                    label += '\n' + str(n['ref'])
                extra = ', peripheries=2' if n.get('type') == 'subprocess' else ''
                lines.append(f'{quote(n["id"])} [label={quote(label)}, shape={SHAPES[n.get("type", "process")]}{extra}];')
        for i, g in enumerate(groups):
            if (str(g['parent']) if g.get('parent') is not None else None) == parent:
                lines.append(f'subgraph cluster_{i} {{')
                lines.append(f'graph [label={quote(wrap_label(g.get("label", g["id"]), width))}, '
                             f'fontname={quote(font)}, fontsize=13, color=black, penwidth=1, '
                             'style=solid, margin=18, labelloc=t, labeljust=l];')
                emit_group(str(g['id']))
                lines.append('}')
    emit_group()
    for rank in layout.get('same_rank', []):
        if not isinstance(rank, list) or any(str(n) not in ids for n in rank):
            raise ValueError('same_rank 必须是现有节点 id 的列表数组')
        lines.append('{ rank=same; ' + '; '.join(quote(n) for n in rank) + '; }')
    for edge in edges:
        src, dst = str(edge['from']), str(edge['to'])
        if src not in ids or dst not in ids:
            raise ValueError(f'附图连线引用不存在的节点: {src} -> {dst}')
        label = wrap_label(edge.get('label', ''), 28)
        # Orthogonal routing does not handle normal edge labels in Graphviz.
        attrs = [f'{"xlabel" if routing == "ortho" else "label"}={quote(label)}']
        if edge.get('feedback'):
            attrs += ['constraint=false', 'minlen=2']
        if edge.get('style', 'solid') not in {'solid', 'dashed'}:
            raise ValueError('连线 style 仅支持 solid/dashed')
        attrs.append('style=' + edge.get('style', 'solid'))
        for option in ('tailport', 'headport'):
            if option in edge:
                if edge[option] not in PORTS:
                    raise ValueError(f'{option} 必须是方向端口')
                attrs.append(f'{option}={edge[option]}')
        lines.append(f'{quote(src)} -> {quote(dst)} [{", ".join(attrs)}];')
    lines.append('}')
    return '\n'.join(lines)


def build_sequence_dot(spec):
    """Fixed actor columns and ordered event rows, rendered by neato -n2."""
    actors, messages = spec.get('participants', []), spec.get('messages', [])
    ids = [str(a['id']) for a in actors]
    if len(ids) < 2 or len(ids) != len(set(ids)) or not messages:
        raise ValueError('时序图至少需要两个唯一参与者和一条消息')
    font = select_font()
    # Make spacing reflect message text and actor label lengths.
    gap, row = 190, 76
    height = 90 + row * len(messages)
    lines = ['digraph G {', 'graph [bgcolor=white, pad=0.2, splines=line, outputorder=edgesfirst];',
             f'node [fontname={quote(font)}, fontsize=13, shape=box, penwidth=1.1];',
             f'edge [fontname={quote(font)}, fontsize=11, arrowsize=0.7];']
    for i, actor in enumerate(actors):
        x = 90 + i * gap
        lines.append(f'"actor_{i}" [pos="{x},{height}!", width=1.8, height=0.6, label={quote(wrap_label(actor.get("label", actor["id"]), 22))}];')
        for j in range(len(messages)+1):
            y = height - 55 - j * row
            lines.append(f'"a{i}_{j}" [pos="{x},{y}!", shape=point, width=0.01, height=0.01, label="", style=invis];')
        lines.append(f'"actor_{i}" -> "a{i}_{len(messages)}" [style=dashed, arrowhead=none, color=black];')
    for j, message in enumerate(messages):
        src, dst = str(message['from']), str(message['to'])
        if src not in ids or dst not in ids or src == dst:
            raise ValueError('时序消息必须连接两个不同的已声明参与者；自调用请拆为子流程或提供已有图像')
        label = wrap_label(message.get('label', ''), 28)
        if len(label.splitlines()) > 3:
            raise ValueError('时序消息过长，请缩短标签并将细节放入正文')
        style = message.get('style', 'solid')
        if style not in {'solid', 'dashed'}:
            raise ValueError('时序消息 style 仅支持 solid/dashed')
        x = 90 + (ids.index(src) + ids.index(dst)) * gap / 2
        y = height - 55 - j * row
        lines.append(f'"a{ids.index(src)}_{j}" -> "a{ids.index(dst)}_{j}" [label={quote(label)}, lp="{x},{y+20}", style={style}];')
    lines.append('}')
    return '\n'.join(lines)


def fit_to_page(width_pt, height_pt):
    if min(width_pt, height_pt) <= 0 or not all(math.isfinite(v) for v in (width_pt, height_pt)):
        raise ValueError('附图尺寸无效')
    scale = min(1.0, MAX_WIDTH_CM / 2.54 * 72 / width_pt, MAX_HEIGHT_CM / 2.54 * 72 / height_pt)
    return {'width_cm': round(width_pt * scale / 72 * 2.54, 3),
            'height_cm': round(height_pt * scale / 72 * 2.54, 3), 'scale': scale}


def export_drawio(graph, path):
    """Preserve Graphviz geometry as native editable cells, not an SVG image."""
    box = [float(v) for v in graph['bb'].split(',')]
    top = box[3]
    # Graphviz pt -> draw.io CSS px.
    factor = 96 / 72
    xml = ET.Element('mxfile', host='app.diagrams.net')
    diagram = ET.SubElement(xml, 'diagram', id='patent-figure', name=path.stem)
    model = ET.SubElement(diagram, 'mxGraphModel', grid='1', gridSize='10', page='0')
    root = ET.SubElement(model, 'root')
    ET.SubElement(root, 'mxCell', id='0')
    ET.SubElement(root, 'mxCell', id='1', parent='0')
    objects = graph.get('objects', [])
    groups = [o for o in objects if 'bb' in o and 'pos' not in o]
    parents = {}
    for obj in objects:
        candidates = [g for g in groups if g is not obj and
                      obj['_gvid'] in (g.get('nodes', []) + g.get('subgraphs', []))]
        if candidates:
            # Select the immediate (smallest) enclosing cluster.
            def area(group):
                l, b, r, t = map(float, group['bb'].split(','))
                return (r-l)*(t-b)
            parents[obj['_gvid']] = min(candidates, key=area)
    font = select_font()
    base = f'html=0;whiteSpace=wrap;fillColor=#FFFFFF;strokeColor=#000000;fontColor=#000000;fontFamily={font};fontSize={FONT_SIZE*factor};'
    for obj in objects:
        oid = 'v' + str(obj['_gvid'])
        if 'pos' in obj:
            x, y = [float(v) for v in obj['pos'].split(',')]
            w, h = float(obj['width'])*72, float(obj['height'])*72
            x, y = x - w/2, top-y-h/2
            shape = {'diamond': 'rhombus', 'ellipse': 'ellipse', 'cylinder': 'cylinder',
                     'parallelogram': 'parallelogram'}.get(obj.get('shape'), 'rectangle')
            style = base + f'shape={shape};'
            if obj.get('peripheries') == '2':
                style += 'shape=process;'
            if obj.get('style') == 'invis':
                style += 'opacity=0;'
        elif 'bb' in obj:
            left, bottom, right, upper = map(float, obj['bb'].split(','))
            x, y, w, h = left, top-upper, right-left, upper-bottom
            style = base + 'fillColor=none;verticalAlign=top;align=left;spacing=8;'
        else:
            continue
        parent = parents.get(obj['_gvid'])
        if parent:
            left, _, _, upper = map(float, parent['bb'].split(','))
            x, y = x-left, y-(top-upper)
        cell = ET.SubElement(root, 'mxCell', id=oid, parent='v'+str(parent['_gvid']) if parent else '1', vertex='1',
                             value=obj.get('label', obj.get('name', '')).replace('\\n', '\n'), style=style)
        ET.SubElement(cell, 'mxGeometry', x=str(x*factor), y=str(y*factor),
                      width=str(w*factor), height=str(h*factor), **{'as': 'geometry'})
    for i, edge in enumerate(graph.get('edges', [])):
        style = f'html=0;rounded=0;strokeColor=#000000;fontColor=#000000;fontFamily={font};fontSize={EDGE_SIZE*factor};endArrow=classic;'
        if edge.get('style') == 'dashed':
            style += 'dashed=1;'
        if edge.get('arrowhead') == 'none':
            style += 'endArrow=none;'
        cell = ET.SubElement(root, 'mxCell', id=f'e{i}', parent='1', edge='1',
                             source='v'+str(edge['tail']), target='v'+str(edge['head']),
                             value=edge.get('label', edge.get('xlabel', '')).replace('\\n', '\n'), style=style)
        geometry = ET.SubElement(cell, 'mxGeometry', relative='1', **{'as': 'geometry'})
        points = ET.SubElement(geometry, 'Array', **{'as': 'points'})
        # Control points retain routed corridors; editable copy may need local refinement.
        for drawing in edge.get('_draw_', []):
            if drawing['op'] in {'b', 'B', 'L'}:
                for x, y in drawing['points'][1:-1]:
                    ET.SubElement(points, 'mxPoint', x=str(x*factor), y=str((top-y)*factor))
    ET.indent(xml)
    ET.ElementTree(xml).write(path, encoding='utf-8', xml_declaration=True)


def inspect_geometry(graph):
    """Detect overlapping node boxes; labels/routes still require visual review."""
    boxes = []
    for node in graph.get('objects', []):
        if 'pos' not in node or node.get('style') == 'invis':
            continue
        x, y = map(float, node['pos'].split(','))
        w, h = float(node['width'])*72, float(node['height'])*72
        boxes.append((node['name'], x-w/2, y-h/2, x+w/2, y+h/2))
    overlaps = []
    for i, a in enumerate(boxes):
        for b in boxes[i+1:]:
            if min(a[3], b[3])-max(a[1], b[1]) > 0.5 and min(a[4], b[4])-max(a[2], b[2]) > 0.5:
                overlaps.append([a[0], b[0]])
    broken_edges = []
    for edge in graph.get('edges', []):
        paths = [op['points'] for op in edge.get('_draw_', []) if op['op'] in {'b', 'B', 'L'}]
        arrows = [op['points'] for op in edge.get('_hdraw_', []) if op['op'] in {'P', 'p'}]
        if paths and arrows:
            end = paths[-1][-1]
            distance = min(math.dist(end, p) for polygon in arrows for p in polygon)
            if distance > 5:
                broken_edges.append({'tail': edge['tail'], 'head': edge['head'], 'gap_pt': round(distance, 2)})
    return {'node_count': len(boxes), 'overlapping_node_boxes': overlaps, 'disconnected_arrowheads': broken_edges,
            'not_checked': ['连线穿框/交叉', '边标签重叠', '技术语义', 'Word实际分页']}


def render_patent_graph(nodes, edges, output, source, spec=None):
    spec = spec or {}
    sequence = spec.get('kind') == 'sequence'
    engine = 'neato' if sequence else 'dot'
    if not shutil.which(engine):
        raise RuntimeError(f'需要 Graphviz {engine} 绘制附图')
    dot = build_sequence_dot(spec) if sequence else build_dot(nodes, edges, spec)
    source.parent.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    source.write_text(dot, encoding='utf-8')
    command = [engine] + (['-n2'] if sequence else [])
    data = subprocess.run(command + ['-Tjson', str(source)], check=True, capture_output=True, text=True, timeout=60)
    graph = json.loads(data.stdout)
    geometry = inspect_geometry(graph)
    if geometry['overlapping_node_boxes']:
        raise ValueError('附图节点发生重叠: ' + str(geometry['overlapping_node_boxes']))
    if geometry['disconnected_arrowheads']:
        raise ValueError('Graphviz 生成了与线段断开的箭头；请移除同层边的显式端口或调整布局: '
                         + str(geometry['disconnected_arrowheads']))
    x0, y0, x1, y1 = map(float, graph['bb'].split(','))
    # pad is 0.18/0.2 inches on each side, also included by the SVG renderer.
    padding = (0.2 if sequence else 0.18) * 72 * 2
    sizing = fit_to_page(x1-x0+padding, y1-y0+padding)
    sizes = [op['size'] for obj in graph.get('objects', []) + graph.get('edges', [])
             for op in obj.get('_ldraw_', []) + obj.get('_xldraw_', []) if op['op'] == 'F']
    minimum = min(sizes or [FONT_SIZE]) * sizing['scale']
    warnings = []
    if minimum < 7.5:
        warnings.append(f'按Word尺寸缩放后标签约{minimum:.1f}pt；应拆分子图或减少节点文字')
    for suffix in ('png', 'svg', 'pdf'):
        target = output.with_suffix('.'+suffix)
        subprocess.run(command + ['-T'+suffix] + (['-Gdpi=300'] if suffix == 'png' else []) + [str(source), '-o', str(target)],
                       check=True, capture_output=True, timeout=60)
        if not target.is_file() or target.stat().st_size == 0:
            raise RuntimeError(f'附图未生成: {target}')
    export_drawio(graph, output.with_suffix('.drawio'))
    report = {'font': select_font(), 'print_size': sizing, 'estimated_min_font_pt': round(minimum, 2),
              'warnings': warnings, 'geometry': geometry, 'visual_review': 'required',
              'drawio_note': '原生可编辑副本；曲线转折线、标签及容器编辑后需重新查看，非像素一致副本'}
    output.with_suffix('.layout.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return report
