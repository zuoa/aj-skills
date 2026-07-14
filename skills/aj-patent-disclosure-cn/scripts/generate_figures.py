#!/usr/bin/env python3
"""
专利技术图表生成脚本

用于生成符合专利规范的技术图表：
- 系统架构图
- 流程图
- 数据结构图
- UML类图/时序图
"""

import argparse
import json
import os
import signal
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


# Matplotlib and Fontconfig may otherwise try to write under the user's home
# directory, which fails in sandboxed skill runtimes. Keep caches disposable.
_CACHE_ROOT = Path(tempfile.gettempdir()) / "aj-patent-figure-cache"
_MPL_CACHE = _CACHE_ROOT / "matplotlib"
_XDG_CACHE = _CACHE_ROOT / "xdg"
_MPL_CACHE.mkdir(parents=True, exist_ok=True)
_XDG_CACHE.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(_MPL_CACHE))
os.environ.setdefault("XDG_CACHE_HOME", str(_XDG_CACHE))
os.environ.setdefault("MPLBACKEND", "Agg")


class FigureTimeoutError(RuntimeError):
    pass


class _time_limit:
    def __init__(self, seconds: int):
        self.seconds = max(1, int(seconds))
        self._enabled = hasattr(signal, "SIGALRM")

    def _handler(self, signum, frame):
        raise FigureTimeoutError(f"figure generation timeout after {self.seconds}s")

    def __enter__(self):
        if self._enabled:
            signal.signal(signal.SIGALRM, self._handler)
            signal.alarm(self.seconds)
        return self

    def __exit__(self, exc_type, exc, tb):
        if self._enabled:
            signal.alarm(0)
        return False


def write_placeholder(output_path: str, reason: str):
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    txt_path = p.with_suffix(".txt")
    txt_path.write_text(
        "附图占位说明\n"
        "====================\n"
        f"目标文件: {p.name}\n"
        f"原因: {reason}\n"
        "建议: 稍后重试生成，或降低图复杂度。\n",
        encoding="utf-8",
    )
    print(f"⚠ 已降级为占位说明: {txt_path}")


def _safe_text(v, default: str = "") -> str:
    if v is None:
        return default
    s = str(v).strip()
    return s if s else default


def _safe_id(text: str) -> str:
    s = "".join(ch if ch.isalnum() else "_" for ch in _safe_text(text, "node"))
    if not s:
        return "node"
    if s[0].isdigit():
        return "n_" + s
    return s


def _build_architecture_mermaid(components: list) -> str:
    components = components or []
    lines = ["flowchart TD"]
    ids = {}
    for comp in components:
        name = _safe_text(comp.get("name"), "未命名组件")
        comp_type = _safe_text(comp.get("type"))
        cid = _safe_id(name)
        ids[name] = cid
        label = f"{name}\\n({comp_type})" if comp_type else name
        lines.append(f'    {cid}["{label}"]')
    for comp in components:
        src = _safe_text(comp.get("name"))
        for dst in comp.get("connections", []) or []:
            if src in ids and dst in ids:
                lines.append(f"    {ids[src]} --> {ids[dst]}")
    if len(lines) == 1:
        lines.append('    sys["系统"]')
    return "\n".join(lines) + "\n"


def _build_flowchart_mermaid(steps: list) -> str:
    steps = steps or []
    lines = ["flowchart TD"]
    ids = {}
    for step in steps:
        sid_raw = _safe_text(step.get("id"), "S")
        sid = _safe_id(sid_raw)
        ids[sid_raw] = sid
        label = _safe_text(step.get("label"), sid_raw)
        stype = _safe_text(step.get("type"), "process")
        if stype in ("start", "end"):
            node = f'{sid}(["{label}"])'
        elif stype == "decision":
            node = f'{sid}{{"{label}"}}'
        else:
            node = f'{sid}["{label}"]'
        lines.append(f"    {node}")
    for step in steps:
        src_raw = _safe_text(step.get("id"))
        edge_label = step.get("edge_label", {}) or {}
        for dst_raw in step.get("next", []) or []:
            if src_raw in ids and dst_raw in ids:
                lbl = _safe_text(edge_label.get(dst_raw))
                if lbl:
                    lines.append(f'    {ids[src_raw]} -->|"{lbl}"| {ids[dst_raw]}')
                else:
                    lines.append(f"    {ids[src_raw]} --> {ids[dst_raw]}")
    if len(lines) == 1:
        lines.append('    s1(["开始"])')
    return "\n".join(lines) + "\n"


def _build_data_structure_mermaid(structure: dict) -> str:
    structure = structure or {"field": "type"}
    lines = ["classDiagram", "    class DataStructure {"]
    for field_name, field_type in structure.items():
        lines.append(f"        +{_safe_text(field_name)}: {_safe_text(field_type)}")
    lines.append("    }")
    return "\n".join(lines) + "\n"


def _render_mermaid_png(mermaid_path: Path, output_png: Path) -> tuple[bool, str]:
    commands = []
    mmdc = shutil.which("mmdc")
    if mmdc:
        commands.append([mmdc, "-i", str(mermaid_path), "-o", str(output_png), "-t", "neutral", "-b", "white"])

    if not commands:
        return False, "未找到 mmdc，无法渲染 Mermaid PNG"

    last_error = ""
    for cmd in commands:
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if output_png.exists():
                return True, ""
        except Exception as e:
            last_error = str(e)
    return False, last_error or "Mermaid 渲染失败"


def _fallback_to_mermaid(output_path: str, reason: str, mermaid_code: str):
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    mmd_path = p.with_suffix(".mmd")
    mmd_path.write_text(mermaid_code, encoding="utf-8")
    ok, msg = _render_mermaid_png(mmd_path, p)
    if ok:
        print(f"⚠ 原图失败，已降级为 Mermaid 并转 PNG: {p}")
        return
    write_placeholder(output_path, f"{reason}; Mermaid 渲染失败: {msg}; 已输出 {mmd_path.name}")


def _setup_matplotlib():
    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        plt.rcParams["font.sans-serif"] = [
            "PingFang SC",
            "Noto Sans CJK SC",
            "Microsoft YaHei",
            "SimHei",
            "Arial Unicode MS",
            "DejaVu Sans",
        ]
        plt.rcParams["axes.unicode_minus"] = False
        return plt, patches
    except ImportError as e:
        raise RuntimeError("需要安装 matplotlib") from e


def _draw_arrow(ax, x1: float, y1: float, x2: float, y2: float):
    ax.annotate(
        "",
        xy=(x2, y2),
        xytext=(x1, y1),
        arrowprops={"arrowstyle": "->", "lw": 1.2, "color": "black"},
    )


def _draw_center_box(ax, patches, x: float, y: float, w: float, h: float, label: str):
    rect = patches.Rectangle(
        (x - w / 2, y - h / 2),
        w,
        h,
        linewidth=1,
        edgecolor="black",
        facecolor="white",
    )
    ax.add_patch(rect)
    ax.text(x, y, label, ha="center", va="center", fontsize=10)


def generate_architecture_diagram(components: list, output_path: str):
    """
    生成系统架构图
    
    Args:
        components: 组件列表，格式 [{'name': '组件名', 'type': '类型', 'connections': ['连接的组件']}]
        output_path: 输出文件路径
    """
    components = components or []
    # Pure Matplotlib is deterministic and avoids Graphviz/Fontconfig
    # process-level failures that cannot be caught in sandboxed runtimes.
    plt, patches = _setup_matplotlib()
    nodes = []
    for comp in components:
        name = _safe_text(comp.get("name"), "未命名组件")
        comp_type = _safe_text(comp.get("type"))
        label = f"{name}\n({comp_type})" if comp_type else name
        nodes.append((name, label, comp.get("connections", []) or []))

    if not nodes:
        nodes = [("系统", "系统", [])]

    node_names = {name for name, _, _ in nodes}
    indegree = {name: 0 for name in node_names}
    for _, _, connections in nodes:
        for destination in connections:
            if destination in indegree:
                indegree[destination] += 1

    levels = {name: 0 for name, degree in indegree.items() if degree == 0}
    queue = list(levels)
    remaining_indegree = dict(indegree)
    connections_by_name = {name: connections for name, _, connections in nodes}
    while queue:
        source = queue.pop(0)
        for destination in connections_by_name.get(source, []):
            if destination not in remaining_indegree:
                continue
            levels[destination] = max(levels.get(destination, 0), levels[source] + 1)
            remaining_indegree[destination] -= 1
            if remaining_indegree[destination] == 0:
                queue.append(destination)

    # Put cyclic or disconnected leftovers on a final layer instead of drawing
    # them on top of another node.
    fallback_level = max(levels.values(), default=-1) + 1
    for name in node_names:
        levels.setdefault(name, fallback_level)

    layers = {}
    for name, _, _ in nodes:
        layers.setdefault(levels[name], []).append(name)

    layer_count = max(layers, default=0) + 1
    max_columns = max((len(items) for items in layers.values()), default=1)
    canvas_width = max(10.0, 4.2 * max_columns)
    fig_height = max(5.0, 2.2 * layer_count + 2.0)
    fig, ax = plt.subplots(figsize=(canvas_width, fig_height))
    ax.set_xlim(0, canvas_width)
    ax.set_ylim(0, layer_count * 2.2 + 2.0)
    ax.axis("off")

    box_width = min(4.2, canvas_width / (max_columns + 1) * 0.9)
    box_height = 0.95
    positions = {}
    for level, names_at_level in sorted(layers.items()):
        y = (layer_count - level) * 2.2
        for index, name in enumerate(names_at_level, start=1):
            x = canvas_width * index / (len(names_at_level) + 1)
            positions[name] = (x, y)

    def boundary_points(source: tuple[float, float], destination: tuple[float, float]):
        source_x, source_y = source
        destination_x, destination_y = destination
        dx = destination_x - source_x
        dy = destination_y - source_y
        if dx == 0 and dy == 0:
            return source, destination
        source_scale = min(
            box_width / 2 / abs(dx) if dx else float("inf"),
            box_height / 2 / abs(dy) if dy else float("inf"),
        )
        destination_scale = source_scale
        start = (source_x + dx * source_scale, source_y + dy * source_scale)
        end = (
            destination_x - dx * destination_scale,
            destination_y - dy * destination_scale,
        )
        return start, end

    # Draw edges first so node boxes mask any line endpoints.
    for name, _, conns in nodes:
        for dst in conns:
            if dst not in positions:
                continue
            start, end = boundary_points(positions[name], positions[dst])
            _draw_arrow(ax, start[0], start[1], end[0], end[1])

    for name, label, _ in nodes:
        x, y = positions[name]
        _draw_center_box(ax, patches, x, y, box_width, box_height, label)

    ax.set_title("系统架构图", fontsize=14, pad=14)
    plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="white", edgecolor="none")
    plt.close()
    print(f"✓ 系统架构图已生成: {output_path}")


def generate_flowchart(steps: list, output_path: str):
    """
    生成流程图
    
    Args:
        steps: 步骤列表，格式 [{'id': '步骤ID', 'label': '步骤描述', 'type': 'start/process/decision/end', 'next': ['下一步ID']}]
        output_path: 输出文件路径
    """
    steps = steps or []
    plt, patches = _setup_matplotlib()
    n = max(1, len(steps))
    fig_h = max(5, min(14, 1.4 * n + 2))
    fig, ax = plt.subplots(figsize=(10, fig_h))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, n * 2 + 2)
    ax.axis("off")

    normalized = []
    for step in steps:
        sid = _safe_text(step.get("id"), "S?")
        label = _safe_text(step.get("label"), sid)
        stype = _safe_text(step.get("type"), "process")
        nxt = step.get("next", []) or []
        edge_label = step.get("edge_label", {}) or {}
        normalized.append((sid, label, stype, nxt, edge_label))

    if not normalized:
        normalized = [("S1", "开始", "start", [], {})]

    positions = {}
    top_y = len(normalized) * 2
    for i, (sid, label, stype, _, _) in enumerate(normalized):
        y = top_y - i * 2
        positions[sid] = (5.0, float(y), stype)
        if stype in ("start", "end"):
            ell = patches.Ellipse((5.0, float(y)), width=3.2, height=0.95, linewidth=1, edgecolor="black", facecolor="white")
            ax.add_patch(ell)
        elif stype == "decision":
            diamond = patches.Polygon(
                [[5.0, y + 0.6], [6.6, y], [5.0, y - 0.6], [3.4, y]],
                closed=True,
                linewidth=1,
                edgecolor="black",
                facecolor="white",
            )
            ax.add_patch(diamond)
        else:
            _draw_center_box(ax, patches, 5.0, float(y), 3.6, 0.95, "")
        ax.text(5.0, float(y), label, ha="center", va="center", fontsize=9)

    for sid, _, _, nxt, edge_label in normalized:
        src_x, src_y, _ = positions[sid]
        for next_id in nxt:
            if next_id not in positions:
                continue
            dst_x, dst_y, _ = positions[next_id]
            _draw_arrow(ax, src_x, src_y - 0.5, dst_x, dst_y + 0.5)
            lbl = _safe_text(edge_label.get(next_id))
            if lbl:
                ax.text((src_x + dst_x) / 2 + 0.2, (src_y + dst_y) / 2, lbl, fontsize=8)

    ax.set_title("流程图", fontsize=14, pad=14)
    plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="white", edgecolor="none")
    plt.close()
    print(f"✓ 流程图已生成(matplotlib fallback): {output_path}")


def generate_data_structure_diagram(structure: dict, output_path: str):
    """
    生成数据结构示意图
    
    Args:
        structure: 数据结构描述
        output_path: 输出文件路径
    """
    plt, patches = _setup_matplotlib()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')
    
    # 示例：绘制简单的数据结构框图
    structure = structure or {"field": "type"}
    y_pos = 5
    for field_name, field_type in structure.items():
        rect = patches.Rectangle((1, y_pos), 4, 0.5, 
                                  linewidth=1, edgecolor='black', 
                                  facecolor='white')
        ax.add_patch(rect)
        ax.text(3, y_pos + 0.25, f"{field_name}: {field_type}", 
                ha='center', va='center', fontsize=10)
        y_pos -= 0.7
    
    plt.title("数据结构示意图", fontsize=14, pad=20)
    plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    
    print(f"✓ 数据结构图已生成: {output_path}")


def generate_uml_sequence_diagram(interactions: list, output_path: str):
    """
    生成UML时序图
    
    Args:
        interactions: 交互列表，格式 [{'from': '对象A', 'to': '对象B', 'message': '消息内容'}]
        output_path: 输出文件路径
    """
    # 使用 PlantUML 语法生成时序图
    plantuml_code = "@startuml\n"
    plantuml_code += "skinparam monochrome true\n"
    plantuml_code += "skinparam shadowing false\n\n"
    
    # 提取所有参与者
    interactions = interactions or []
    participants = set()
    for interaction in interactions:
        participants.add(_safe_text(interaction.get('from'), "对象A"))
        participants.add(_safe_text(interaction.get('to'), "对象B"))
    
    for participant in participants:
        plantuml_code += f"participant \"{participant}\"\n"
    
    plantuml_code += "\n"
    
    for interaction in interactions:
        msg_from = _safe_text(interaction.get('from'), "对象A")
        msg_to = _safe_text(interaction.get('to'), "对象B")
        message = _safe_text(interaction.get('message'), "消息")
        plantuml_code += f"\"{msg_from}\" -> \"{msg_to}\": {message}\n"
    
    plantuml_code += "@enduml"
    
    # 保存为文本文件（实际生成图片需要 PlantUML 环境）
    txt_path = output_path.replace('.png', '_plantuml.txt')
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(plantuml_code)
    
    print(f"✓ UML时序图代码已生成: {txt_path}")
    print(f"  提示：可使用在线工具 https://www.plantuml.com/plantuml 生成图片")


def _sample_payload() -> dict:
    return {
        "components": [
            {"name": "用户层", "type": "接口层", "connections": ["应用层"]},
            {"name": "应用层", "type": "业务逻辑", "connections": ["服务层"]},
            {"name": "服务层", "type": "核心服务", "connections": ["数据层"]},
            {"name": "数据层", "type": "数据存储", "connections": []},
        ],
        "steps": [
            {"id": "S1", "label": "开始", "type": "start", "next": ["S2"]},
            {"id": "S2", "label": "接收用户请求", "type": "process", "next": ["S3"]},
            {"id": "S3", "label": "数据有效?", "type": "decision", "next": ["S4", "S5"], "edge_label": {"S4": "是", "S5": "否"}},
            {"id": "S4", "label": "处理数据", "type": "process", "next": ["S6"]},
            {"id": "S5", "label": "返回错误", "type": "process", "next": ["S7"]},
            {"id": "S6", "label": "返回结果", "type": "process", "next": ["S7"]},
            {"id": "S7", "label": "结束", "type": "end", "next": []},
        ],
        "structure": {
            "user_id": "String",
            "timestamp": "Long",
            "features": "Array",
            "prediction": "Float",
        },
        "interactions": [
            {"from": "用户", "to": "前端", "message": "发起请求"},
            {"from": "前端", "to": "后端API", "message": "调用接口"},
            {"from": "后端API", "to": "业务逻辑", "message": "处理请求"},
            {"from": "业务逻辑", "to": "数据库", "message": "查询数据"},
            {"from": "数据库", "to": "业务逻辑", "message": "返回数据"},
            {"from": "业务逻辑", "to": "后端API", "message": "返回结果"},
            {"from": "后端API", "to": "前端", "message": "响应"},
            {"from": "前端", "to": "用户", "message": "显示结果"},
        ],
    }


def _run_one(
    name: str,
    fn,
    args: tuple,
    timeout_sec: int,
    output_path: str,
    mermaid_code: str,
    require_png: bool = True,
) -> str:
    try:
        with _time_limit(timeout_sec):
            fn(*args)
        if require_png and not Path(output_path).exists():
            _fallback_to_mermaid(output_path, f"{name} 未生成 PNG 文件", mermaid_code)
            return "image" if Path(output_path).exists() else "fallback"
        return "image" if require_png else "code"
    except FigureTimeoutError as e:
        _fallback_to_mermaid(output_path, str(e), mermaid_code)
        return "image" if Path(output_path).exists() else "fallback"
    except Exception as e:
        _fallback_to_mermaid(output_path, f"{name} 生成失败: {e}", mermaid_code)
        return "image" if Path(output_path).exists() else "fallback"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate patent figures with timeout and fallback")
    parser.add_argument("--output-dir", default="figures", help="Output directory")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--input-json",
        help="JSON payload with figure_plan or components/steps/structure/interactions",
    )
    source.add_argument(
        "--demo",
        action="store_true",
        help="Generate generic demonstration figures (never use for a real disclosure)",
    )
    parser.add_argument("--timeout-sec", type=int, default=90, help="Per-figure timeout seconds")
    return parser.parse_args()


def load_payload(input_json: str | None, demo: bool = False) -> dict:
    if demo:
        return _sample_payload()
    if not input_json:
        raise ValueError("--input-json is required unless --demo is used")
    p = Path(input_json)
    raw = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("figure input must be a JSON object")

    plan = raw.get("figure_plan", raw)
    if not isinstance(plan, dict):
        raise ValueError("figure_plan must be an object")

    normalized = {
        "components": plan.get("components", []),
        "steps": plan.get("steps", []),
        "structure": plan.get("structure", {}),
        "interactions": plan.get("interactions", []),
    }

    # A disclosure JSON can reuse its confirmed solution steps for a simple
    # sequential flowchart without inventing new labels or branches.
    if not normalized["steps"]:
        invention = raw.get("invention", {})
        source_steps = invention.get("solution_steps", []) if isinstance(invention, dict) else []
        if source_steps:
            derived_steps = []
            for index, step in enumerate(source_steps):
                if not isinstance(step, dict):
                    continue
                step_id = _safe_text(step.get("id"), f"S{index + 1}")
                next_id = ""
                if index + 1 < len(source_steps) and isinstance(source_steps[index + 1], dict):
                    next_id = _safe_text(source_steps[index + 1].get("id"), f"S{index + 2}")
                derived_steps.append(
                    {
                        "id": step_id,
                        "label": f"{step_id} {_safe_text(step.get('action') or step.get('description'), step_id)}",
                        "type": "process",
                        "next": [next_id] if next_id else [],
                    }
                )
            normalized["steps"] = derived_steps

    return normalized


def write_figure_source(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        payload = load_payload(args.input_json, demo=args.demo)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"附图输入错误: {exc}", file=sys.stderr)
        return 2

    components = payload.get("components", []) or []
    steps = payload.get("steps", []) or []
    structure = payload.get("structure", {}) or {}
    interactions = payload.get("interactions", []) or []

    if not any((components, steps, structure, interactions)):
        print(
            "附图输入没有可绘制的已确认内容；请提供 figure_plan，或在 disclosure JSON 中提供 solution_steps。",
            file=sys.stderr,
        )
        return 2

    source_dir = output_dir / "figure_sources"
    figure_no = 1

    image_ok_count = 0
    image_total = sum(bool(item) for item in (components, steps, structure))
    code_ok_count = 0
    code_total = 1 if interactions else 0

    if components:
        stem = f"fig{figure_no}_architecture"
        figure_no += 1
        source = _build_architecture_mermaid(components)
        write_figure_source(source_dir / f"{stem}.mmd", source)
        if _run_one(
            "系统架构图",
            generate_architecture_diagram,
            (components, str(output_dir / f"{stem}.png")),
            args.timeout_sec,
            str(output_dir / f"{stem}.png"),
            source,
        ) == "image":
            image_ok_count += 1

    if steps:
        stem = f"fig{figure_no}_flowchart"
        figure_no += 1
        source = _build_flowchart_mermaid(steps)
        write_figure_source(source_dir / f"{stem}.mmd", source)
        if _run_one(
            "流程图",
            generate_flowchart,
            (steps, str(output_dir / f"{stem}.png")),
            args.timeout_sec,
            str(output_dir / f"{stem}.png"),
            source,
        ) == "image":
            image_ok_count += 1

    if structure:
        stem = f"fig{figure_no}_datastructure"
        figure_no += 1
        source = _build_data_structure_mermaid(structure)
        write_figure_source(source_dir / f"{stem}.mmd", source)
        if _run_one(
            "数据结构图",
            generate_data_structure_diagram,
            (structure, str(output_dir / f"{stem}.png")),
            args.timeout_sec,
            str(output_dir / f"{stem}.png"),
            source,
        ) == "image":
            image_ok_count += 1

    if interactions:
        stem = f"fig{figure_no}_sequence"
        if _run_one(
            "UML时序图",
            generate_uml_sequence_diagram,
            (interactions, str(source_dir / f"{stem}.png")),
            args.timeout_sec,
            str(output_dir / f"{stem}.png"),
            "",
            require_png=False,
        ) == "code":
            code_ok_count += 1

    print(
        f"图表生成完成: 图片 {image_ok_count}/{image_total} 成功, "
        f"UML代码 {code_ok_count}/{code_total} 成功"
    )
    return 0 if image_ok_count > 0 or code_ok_count > 0 else 2


if __name__ == "__main__":
    sys.exit(main())
