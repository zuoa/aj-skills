#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import os
import platform
import shutil
import subprocess
from io import BytesIO
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple
from urllib import request

from PIL import Image, ImageDraw, ImageFont, ImageOps
import qrcode


DEFAULT_WIDTH = 1280
PAGE_PADDING = 56
CARD_PADDING = 36
CARD_GAP = 32
MAP_WIDTH = 340
MAP_HEIGHT = 200
QR_SIZE = 100

# 活泼年轻配色方案
BACKGROUND = "#FFF9F0"  # 温暖的奶油白
CARD_BG = "#FFFFFF"  # 纯白卡片
TEXT = "#1A1A2E"  # 深蓝黑，更年轻
MUTED = "#6B7280"  # 现代灰
ACCENT = "#FF6B6B"  # 珊瑚红，活力强调色
ACCENT_SECONDARY = "#4ECDC4"  # 青绿色，辅助强调
ACCENT_TERTIARY = "#FFE66D"  # 明亮黄，装饰用
BORDER = "#E8E8E8"  # 浅灰边框
PLACEHOLDER_BG = "#F3F4F6"

# 类型标签配色
TYPE_COLORS = {
    "讲座": ("#FF6B6B", "#FFE8E8"),
    "分享会": ("#4ECDC4", "#E0F7F5"),
    "工作坊": ("#95E1D3", "#E8FAF7"),
    "训练营": ("#F38181", "#FFE8E8"),
    "路演": ("#AA96DA", "#F0EBF8"),
    "直播": ("#FCBAD3", "#FEF0F5"),
    "闭门会": ("#A8D8EA", "#E8F6FC"),
    "线上": ("#6C5CE7", "#E8E6F9"),
}

# 图标颜色
ICON_COLORS = {
    "time": "#FF6B6B",
    "location": "#4ECDC4",
    "people": "#F9CA24",
    "description": "#6C5CE7",
}


def hex_to_rgb(hex_color: str) -> tuple:
    """将十六进制颜色转换为 RGB 元组"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render activity summary image from activity-structured-geo.json.")
    parser.add_argument("--input", required=True, help="Path to activity-structured-geo.json.")
    parser.add_argument("--output", required=True, help="Path to output PNG.")
    parser.add_argument("--title", default="活动情报速递", help="Poster title.")
    parser.add_argument("--subtitle", default="", help="Optional subtitle.")
    parser.add_argument("--watermark", default="潮匠里", help="Watermark text shown at top-right.")
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH, help="Canvas width in pixels.")
    parser.add_argument("--download-timeout", type=float, default=10.0, help="Timeout for remote images.")
    return parser.parse_args()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _existing_paths(paths: Sequence[str]) -> List[str]:
    result: List[str] = []
    seen = set()
    for item in paths:
        expanded = str(Path(item).expanduser())
        if expanded in seen:
            continue
        if Path(expanded).exists():
            result.append(expanded)
            seen.add(expanded)
    return result


def _fc_match_font(family: str) -> str:
    if not shutil.which("fc-match"):
        return ""
    try:
        result = subprocess.run(
            ["fc-match", "-f", "%{file}\n", family],
            capture_output=True,
            check=True,
            text=True,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    path = result.stdout.strip().splitlines()[0] if result.stdout.strip() else ""
    return path if path and Path(path).exists() else ""


@lru_cache(maxsize=4)
def font_candidates(bold: bool = False) -> Tuple[str, ...]:
    candidates: List[str] = []

    env_keys = ["ACTIVITY_PUSH_FONT_PATH"]
    env_keys.append("ACTIVITY_PUSH_FONT_BOLD_PATH" if bold else "ACTIVITY_PUSH_FONT_REGULAR_PATH")
    for key in env_keys:
        value = os.environ.get(key, "").strip()
        if value:
            candidates.append(value)

    system = platform.system().lower()
    if system == "darwin":
        candidates.extend(
            [
                "/System/Library/Fonts/Supplemental/PingFang.ttc",
                "/System/Library/Fonts/PingFang.ttc",
                "/System/Library/Fonts/Hiragino Sans GB.ttc",
                "/System/Library/Fonts/Supplemental/Songti.ttc",
                "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
            ]
        )
    else:
        candidates.extend(
            [
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc" if bold else "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/opentype/noto/NotoSansCJKsc-Bold.otf" if bold else "/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf",
                "/usr/share/fonts/opentype/noto/NotoSansSC-Bold.otf" if bold else "/usr/share/fonts/opentype/noto/NotoSansSC-Regular.otf",
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc" if bold else "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/truetype/noto/NotoSansSC-Bold.ttf" if bold else "/usr/share/fonts/truetype/noto/NotoSansSC-Regular.ttf",
                "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
                "/usr/share/fonts/truetype/arphic/uming.ttc",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            ]
        )
        family_names = [
            "Noto Sans CJK SC:bold" if bold else "Noto Sans CJK SC",
            "Noto Sans SC:bold" if bold else "Noto Sans SC",
            "Source Han Sans SC Bold" if bold else "Source Han Sans SC",
            "WenQuanYi Zen Hei",
            "DejaVu Sans:style=Bold" if bold else "DejaVu Sans",
            "sans-serif:style=Bold" if bold else "sans-serif",
        ]
        candidates.extend(path for path in (_fc_match_font(name) for name in family_names) if path)

    return tuple(_existing_paths(candidates))


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in font_candidates(bold):
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def text_height(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont | ImageFont.ImageFont) -> int:
    if not text:
        return 0
    box = draw.multiline_textbbox((0, 0), text, font=font, spacing=6)
    return int(math.ceil(box[3] - box[1]))


def wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    max_width: int,
) -> List[str]:
    if not text:
        return []
    lines: List[str] = []
    current = ""
    for char in text:
        candidate = current + char
        box = draw.textbbox((0, 0), candidate, font=font)
        if box[2] - box[0] <= max_width or not current:
            current = candidate
            continue
        lines.append(current)
        current = char
    if current:
        lines.append(current)
    return lines


def wrap_labeled_text(
    draw: ImageDraw.ImageDraw,
    label: str,
    value: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    max_width: int,
) -> str:
    prefix = f"{label}："
    if not value:
        return ""
    lines = wrap_text(draw, value, font, max_width - int(draw.textbbox((0, 0), prefix, font=font)[2]))
    if not lines:
        return ""
    wrapped = [f"{prefix}{lines[0]}"]
    indent = " " * len(prefix)
    wrapped.extend(f"{indent}{line}" for line in lines[1:])
    return "\n".join(wrapped)


def build_meta_lines(
    activity: Dict[str, Any],
    draw: ImageDraw.ImageDraw,
    body_font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    content_width: int,
) -> List[str]:
    time_value = build_time_text(activity)
    fields = [
        ("类型", str(activity.get("activityType", "")).strip()),
        ("时间", time_value),
        ("地点", str(activity.get("activityAddress", "")).strip()),
        ("人数", str(activity.get("activityLimitNum", "")).strip()),
        ("说明", str(activity.get("activityDescription", "")).strip()),
    ]
    lines = [wrap_labeled_text(draw, label, value, body_font, content_width) for label, value in fields if value]
    return [line for line in lines if line]


def build_time_text(activity: Dict[str, Any]) -> str:
    start = str(activity.get("activityStartTime", "")).strip()
    end = str(activity.get("activityEndTime", "")).strip()
    if start and end:
        return f"{start} - {end}"
    if start:
        return start
    if end:
        return end
    return ""

def build_qr_image(content: str, size: int = QR_SIZE) -> Optional[Image.Image]:
    if not content:
        return None
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(content)
    qr.make(fit=True)
    image = qr.make_image(fill_color=TEXT, back_color="white").convert("RGB")
    return ImageOps.fit(image, (size, size), method=Image.Resampling.NEAREST)


def load_image(source: str, timeout: float) -> Optional[Image.Image]:
    if not source:
        return None
    try:
        if source.startswith("file://"):
            return Image.open(source[7:]).convert("RGB")
        local_path = Path(source)
        if local_path.exists():
            return Image.open(local_path).convert("RGB")
        with request.urlopen(source, timeout=timeout) as resp:
            return Image.open(BytesIO(resp.read())).convert("RGB")
    except Exception:
        return None


def has_coordinates(activity: Dict[str, Any]) -> bool:
    lng = str(activity.get("activityLongitudeGCJ02", "")).strip()
    lat = str(activity.get("activityLatitudeGCJ02", "")).strip()
    if not lng or not lat:
        return False
    try:
        float(lng)
        float(lat)
    except ValueError:
        return False
    return True


def require_source_url(activity: Dict[str, Any], index: int) -> str:
    source_url = str(activity.get("sourceUrl", "")).strip()
    if source_url:
        return source_url
    activity_name = str(activity.get("activityName", "")).strip() or f"第 {index} 条活动"
    raise RuntimeError(f"activity {index} missing sourceUrl, cannot render required QR code: {activity_name}")


def draw_qr_block(
    image: Image.Image,
    draw: ImageDraw.ImageDraw,
    link_url: str,
    left: int,
    top: int,
    fonts: Dict[str, ImageFont.FreeTypeFont | ImageFont.ImageFont],
) -> int:
    """绘制更年轻的二维码区块"""
    qr = build_qr_image(link_url, QR_SIZE)
    if qr is None:
        return 0

    # 绘制装饰性背景圆
    bg_size = QR_SIZE + 16
    bg_left = left - 8
    bg_top = top - 8
    draw.ellipse(
        (bg_left, bg_top, bg_left + bg_size, bg_top + bg_size),
        fill="#F3F4F6", outline=BORDER, width=1
    )

    # 粘贴二维码
    qr_box = (left, top, left + QR_SIZE, top + QR_SIZE)
    image.paste(qr, (left, top))

    # 绘制小装饰点
    dot_color = ACCENT_SECONDARY
    draw.ellipse((bg_left - 4, bg_top + bg_size // 2 - 4, bg_left + 4, bg_top + bg_size // 2 + 4), fill=dot_color)
    draw.ellipse((bg_left + bg_size - 4, bg_top + 8, bg_left + bg_size + 4, bg_top + 16), fill=ACCENT_TERTIARY)

    return QR_SIZE + 16


def draw_decorative_elements(
    draw: ImageDraw.ImageDraw,
    width: int,
    top: int,
) -> None:
    """绘制装饰性元素（圆点、线条等）"""
    # 左上角装饰圆点
    draw.ellipse((PAGE_PADDING - 20, top - 10, PAGE_PADDING, top + 10), fill=ACCENT)
    draw.ellipse((PAGE_PADDING + 8, top + 5, PAGE_PADDING + 16, top + 13), fill=ACCENT_SECONDARY)
    draw.ellipse((PAGE_PADDING + 22, top - 5, PAGE_PADDING + 30, top + 3), fill=ACCENT_TERTIARY)

    # 右上角装饰线条
    line_y = top + 20
    for i, color in enumerate([ACCENT, ACCENT_SECONDARY, ACCENT_TERTIARY]):
        offset = i * 12
        draw.line((width - PAGE_PADDING - 100 + offset, line_y - offset,
                  width - PAGE_PADDING - 40 + offset, line_y - offset),
                 fill=color, width=4)


def draw_watermark(
    image: Image.Image,
    width: int,
    watermark: str,
    fonts: Dict[str, ImageFont.FreeTypeFont | ImageFont.ImageFont],
) -> None:
    if not watermark.strip():
        return

    overlay = Image.new("RGBA", (200, 120), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # 更年轻的水印设计 - 圆形徽章风格
    center_x, center_y = 100, 60
    radius = 50

    # 外圈渐变效果（用同心圆模拟）
    for i in range(3):
        alpha = 180 - i * 40
        r = radius - i * 3
        draw.ellipse((center_x - r, center_y - r, center_x + r, center_y + r),
                    outline=(*hex_to_rgb(ACCENT), alpha), width=2)

    # 背景圆形
    draw.ellipse((center_x - radius + 8, center_y - radius + 8,
                 center_x + radius - 8, center_y + radius - 8),
                fill=(*hex_to_rgb(CARD_BG), 200))

    # 文字
    text_box = draw.textbbox((0, 0), watermark, font=fonts["watermark"])
    text_x = center_x - (text_box[2] - text_box[0]) / 2
    text_y = center_y - (text_box[3] - text_box[1]) / 2
    draw.text((text_x, text_y), watermark, fill=(*hex_to_rgb(ACCENT), 220), font=fonts["watermark"])

    # 装饰小点
    draw.ellipse((center_x - radius - 5, center_y - 3, center_x - radius + 3, center_y + 5), fill=ACCENT_SECONDARY)
    draw.ellipse((center_x + radius - 3, center_y - 8, center_x + radius + 5, center_y), fill=ACCENT_TERTIARY)

    rotated = overlay.rotate(-12, resample=Image.Resampling.BICUBIC, expand=True)
    paste_left = width - PAGE_PADDING - rotated.size[0] + 20
    image.paste(rotated, (paste_left, -10), rotated)


def get_type_color(activity_type: str) -> tuple:
    """获取活动类型的颜色配置"""
    for type_key, colors in TYPE_COLORS.items():
        if type_key in activity_type:
            return colors
    return (ACCENT, "#FFE8E8")  # 默认颜色


def draw_shadow_rounded_rectangle(
    draw: ImageDraw.ImageDraw,
    bbox: tuple,
    radius: int,
    fill: str,
    shadow_color: str = "#00000010",
    shadow_offset: int = 4,
) -> None:
    """绘制带阴影的圆角矩形"""
    x1, y1, x2, y2 = bbox
    # 阴影
    shadow_bbox = (x1 + shadow_offset, y1 + shadow_offset, x2 + shadow_offset, y2 + shadow_offset)
    draw.rounded_rectangle(shadow_bbox, radius=radius, fill=shadow_color)
    # 主体
    draw.rounded_rectangle(bbox, radius=radius, fill=fill, outline=BORDER, width=1)


def draw_type_tag(
    draw: ImageDraw.ImageDraw,
    activity_type: str,
    left: int,
    top: int,
    fonts: Dict[str, ImageFont.FreeTypeFont | ImageFont.ImageFont],
) -> int:
    """绘制活动类型标签，返回标签宽度"""
    if not activity_type:
        return 0

    text_color, bg_color = get_type_color(activity_type)
    text_box = draw.textbbox((0, 0), activity_type, font=fonts["small"])
    text_width = text_box[2] - text_box[0]
    tag_width = text_width + 20
    tag_height = 28

    draw.rounded_rectangle(
        (left, top, left + tag_width, top + tag_height),
        radius=14, fill=bg_color
    )
    draw.text(
        (left + 10, top + 4),
        activity_type, fill=text_color, font=fonts["small"]
    )

    return tag_width + 8  # 返回标签宽度 + 间距


def draw_icon_and_text(
    draw: ImageDraw.ImageDraw,
    icon_type: str,
    text: str,
    left: int,
    top: int,
    max_width: int,
    fonts: Dict[str, ImageFont.FreeTypeFont | ImageFont.ImageFont],
) -> int:
    """绘制带图标的文本行，返回下一行的y坐标"""
    if not text:
        return top

    icon_color = ICON_COLORS.get(icon_type, MUTED)
    icon_size = 16

    # 绘制简单图标（圆形背景 + 符号）
    icon_center_x = left + icon_size // 2
    icon_center_y = top + icon_size // 2 + 2
    draw.ellipse(
        (icon_center_x - icon_size // 2, icon_center_y - icon_size // 2,
         icon_center_x + icon_size // 2, icon_center_y + icon_size // 2),
        fill=icon_color
    )

    # 文字区域
    text_left = left + icon_size + 8
    available_width = max_width - icon_size - 8

    # 换行处理
    lines = wrap_text(draw, text, fonts["body"], available_width)
    line_height = text_height(draw, "测试", fonts["body"]) + 8

    for i, line in enumerate(lines):
        draw.text((text_left, top + i * line_height), line, fill=TEXT, font=fonts["body"])

    return top + len(lines) * line_height + 4


def render_card(
    image: Image.Image,
    draw: ImageDraw.ImageDraw,
    activity: Dict[str, Any],
    index: int,
    top: int,
    width: int,
    timeout: float,
    fonts: Dict[str, ImageFont.FreeTypeFont | ImageFont.ImageFont],
) -> int:
    card_left = PAGE_PADDING
    card_right = width - PAGE_PADDING
    card_inner_width = card_right - card_left - CARD_PADDING * 2

    title = str(activity.get('activityName', '')).strip() or '未命名活动'
    activity_type = str(activity.get('activityType', '')).strip()
    source_url = require_source_url(activity, index)

    show_map = has_coordinates(activity) and bool(str(activity.get("activityStaticMapUrl", "")).strip())
    show_qr = True
    show_side_column = show_map or show_qr
    text_width = card_inner_width - MAP_WIDTH - 32 if show_side_column else card_inner_width

    # 计算标题高度（考虑序号圆圈）
    title_prefix_width = 36  # 序号圆圈的宽度 + 间距
    title_lines = wrap_text(draw, title, fonts["title"], text_width - title_prefix_width)
    title_height = text_height(draw, "\n".join(title_lines), fonts["title"])

    # 计算元信息高度
    meta_start_y = 0  # 稍后计算
    meta_total_height = 0

    # 收集需要显示的信息
    time_value = build_time_text(activity)
    address = str(activity.get("activityAddress", "")).strip()
    limit_num = str(activity.get("activityLimitNum", "")).strip()
    description = str(activity.get("activityDescription", "")).strip()

    # 估算元信息区域高度
    line_height = text_height(draw, "测试", fonts["body"]) + 12
    meta_items_count = sum([bool(time_value), bool(address), bool(limit_num), bool(description)])
    meta_total_height = meta_items_count * line_height + 20

    # 计算右侧区域高度
    right_column_height = 0
    if show_map:
        right_column_height += MAP_HEIGHT
    if show_qr:
        if right_column_height:
            right_column_height += 20
        right_column_height += QR_SIZE

    # 计算总高度
    type_tag_height = 32 if activity_type else 0
    content_height = max(type_tag_height + title_height + 24 + meta_total_height, right_column_height + 20)
    card_height = CARD_PADDING * 2 + content_height

    # 绘制带阴影的卡片
    card_box = (card_left, top, card_right, top + card_height)
    draw_shadow_rounded_rectangle(draw, card_box, radius=32, fill=CARD_BG)

    content_left = card_left + CARD_PADDING
    content_top = top + CARD_PADDING
    side_left = card_right - CARD_PADDING - MAP_WIDTH
    side_top = content_top + 10

    # 绘制序号圆圈
    circle_radius = 14
    circle_x = content_left + circle_radius
    circle_y = content_top + circle_radius
    draw.ellipse(
        (circle_x - circle_radius, circle_y - circle_radius,
         circle_x + circle_radius, circle_y + circle_radius),
        fill=ACCENT
    )
    index_text = str(index)
    text_box = draw.textbbox((0, 0), index_text, font=fonts["small"])
    text_width_actual = text_box[2] - text_box[0]
    text_height_actual = text_box[3] - text_box[1]
    draw.text(
        (circle_x - text_width_actual / 2, circle_y - text_height_actual / 2 - 1),
        index_text, fill="white", font=fonts["small"]
    )

    # 绘制类型标签
    current_x = content_left + 36
    if activity_type:
        tag_width = draw_type_tag(draw, activity_type, current_x, content_top + 2, fonts)
        current_x += tag_width

    # 绘制标题
    title_y = content_top + (36 if activity_type else 0)
    draw.multiline_text(
        (content_left + 36, title_y),
        "\n".join(title_lines),
        fill=TEXT,
        font=fonts["title"],
        spacing=8,
    )

    # 绘制元信息（带图标）
    meta_y = title_y + title_height + 20
    if time_value:
        meta_y = draw_icon_and_text(draw, "time", f"时间：{time_value}", content_left, meta_y, text_width, fonts)
    if address:
        meta_y = draw_icon_and_text(draw, "location", f"地点：{address}", content_left, meta_y, text_width, fonts)
    if limit_num:
        meta_y = draw_icon_and_text(draw, "people", f"人数：{limit_num}人", content_left, meta_y, text_width, fonts)
    if description:
        meta_y = draw_icon_and_text(draw, "description", description, content_left, meta_y, text_width, fonts)

    # 绘制右侧地图
    if show_map:
        map_box = (side_left, side_top, side_left + MAP_WIDTH, side_top + MAP_HEIGHT)
        static_map = load_image(str(activity.get("activityStaticMapUrl", "")).strip(), timeout)
        if static_map is not None:
            fitted = ImageOps.fit(static_map, (MAP_WIDTH, MAP_HEIGHT), method=Image.Resampling.LANCZOS)
            # 添加圆角遮罩
            mask = Image.new('L', (MAP_WIDTH, MAP_HEIGHT), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rounded_rectangle((0, 0, MAP_WIDTH, MAP_HEIGHT), radius=20, fill=255)
            image.paste(fitted, (side_left, side_top), mask)
            draw.rounded_rectangle(map_box, radius=20, outline=BORDER, width=1)

    # 绘制二维码
    if show_qr:
        qr_top = side_top + (MAP_HEIGHT + 20 if show_map else 0)
        qr_left = side_left + (MAP_WIDTH - QR_SIZE) // 2  # 居中
        draw_qr_block(image, draw, source_url, qr_left, qr_top, fonts)

    return top + card_height + CARD_GAP


def build_empty_state(
    image: Image.Image,
    draw: ImageDraw.ImageDraw,
    width: int,
    top: int,
    fonts: Dict[str, ImageFont.FreeTypeFont | ImageFont.ImageFont],
) -> int:
    card_box = (PAGE_PADDING, top, width - PAGE_PADDING, top + 240)
    draw_shadow_rounded_rectangle(draw, card_box, radius=32, fill=CARD_BG)

    # 绘制装饰图标（用圆形和线条模拟）
    icon_center_x = PAGE_PADDING + CARD_PADDING + 30
    icon_center_y = top + 70

    # 大圆背景
    draw.ellipse(
        (icon_center_x - 30, icon_center_y - 30, icon_center_x + 30, icon_center_y + 30),
        fill="#FFE8E8"
    )
    # 小圆装饰
    draw.ellipse(
        (icon_center_x - 15, icon_center_y - 15, icon_center_x + 15, icon_center_y + 15),
        fill=ACCENT
    )
    # 表情符号位置的小点
    draw.ellipse(
        (icon_center_x - 5, icon_center_y - 5, icon_center_x + 5, icon_center_y + 5),
        fill="white"
    )

    title = "最近 24 小时未发现新的活动文章"
    body = "可保留这张图作为当天空结果的归档凭证。"

    draw.text((PAGE_PADDING + CARD_PADDING + 80, top + 50), title, fill=TEXT, font=fonts["title"])
    draw.text((PAGE_PADDING + CARD_PADDING + 80, top + 100), body, fill=MUTED, font=fonts["body"])

    # 底部装饰
    decor_y = top + 180
    for i, color in enumerate([ACCENT, ACCENT_SECONDARY, ACCENT_TERTIARY]):
        x = PAGE_PADDING + CARD_PADDING + i * 40
        draw.ellipse((x, decor_y, x + 12, decor_y + 12), fill=color)

    return top + 240


def estimate_total_height(
    activities: Sequence[Dict[str, Any]],
    width: int,
    fonts: Dict[str, ImageFont.FreeTypeFont | ImageFont.ImageFont],
) -> int:
    probe = Image.new("RGB", (width, 10), BACKGROUND)
    draw = ImageDraw.Draw(probe)
    top = PAGE_PADDING + 160  # 增加顶部空间以适应新的 header 设计
    if not activities:
        return build_empty_state(probe, draw, width, top, fonts) + PAGE_PADDING

    for index, activity in enumerate(activities, start=1):
        top = render_card(probe, draw, activity, index, top, width, timeout=0, fonts=fonts)
    return top + PAGE_PADDING


def render_header(
    image: Image.Image,
    draw: ImageDraw.ImageDraw,
    width: int,
    title: str,
    subtitle: str,
    count: int,
    watermark: str,
    fonts: Dict[str, ImageFont.FreeTypeFont | ImageFont.ImageFont],
) -> None:
    # 绘制装饰元素
    draw_decorative_elements(draw, width, PAGE_PADDING + 30)

    # 标题使用渐变色效果（通过多层文字模拟）
    draw.text((PAGE_PADDING, PAGE_PADDING + 25), title, fill=TEXT, font=fonts["headline"])

    # 副标题带图标
    meta = subtitle.strip() if subtitle.strip() else f"共 {count} 条活动"
    draw.text((PAGE_PADDING, PAGE_PADDING + 85), meta, fill=MUTED, font=fonts["body"])

    # 活动数量徽章
    if count > 0:
        badge_text = f"{count}"
        badge_font = fonts["section"]
        text_box = draw.textbbox((0, 0), badge_text, font=badge_font)
        badge_width = text_box[2] - text_box[0] + 24
        badge_height = text_box[3] - text_box[1] + 12
        badge_x = PAGE_PADDING + 320
        badge_y = PAGE_PADDING + 20

        # 圆角徽章
        draw.rounded_rectangle(
            (badge_x, badge_y, badge_x + badge_width, badge_y + badge_height),
            radius=16, fill=ACCENT
        )
        draw.text(
            (badge_x + 12, badge_y + 6),
            badge_text, fill="white", font=badge_font
        )

    draw_watermark(image, width, watermark, fonts)

    # 底部装饰线 - 使用渐变效果
    line_y = PAGE_PADDING + 135
    line_colors = [ACCENT, ACCENT_SECONDARY, ACCENT_TERTIARY]
    segment_width = (width - PAGE_PADDING * 2) // len(line_colors)
    for i, color in enumerate(line_colors):
        x1 = PAGE_PADDING + i * segment_width
        x2 = x1 + segment_width - 4
        draw.line((x1, line_y, x2, line_y), fill=color, width=4)


def run_render(args: argparse.Namespace) -> Path:
    input_path = Path(args.input).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = read_json(input_path)
    if not isinstance(data, list):
        raise RuntimeError("input must be a JSON array")

    fonts = {
        "headline": load_font(48, bold=True),
        "title": load_font(28, bold=True),
        "section": load_font(22, bold=True),
        "body": load_font(18),
        "small": load_font(14),
        "watermark": load_font(32, bold=True),
    }
    height = estimate_total_height(data, args.width, fonts)
    image = Image.new("RGB", (args.width, height), BACKGROUND)
    draw = ImageDraw.Draw(image)

    render_header(
        image,
        draw,
        args.width,
        args.title,
        args.subtitle,
        len(data),
        getattr(args, "watermark", "潮匠里"),
        fonts,
    )
    top = PAGE_PADDING + 160  # 增加顶部空间以适应新的 header 设计
    if not data:
        build_empty_state(image, draw, args.width, top, fonts)
    else:
        for index, activity in enumerate(data, start=1):
            top = render_card(image, draw, activity, index, top, args.width, args.download_timeout, fonts)

    image.save(output_path, format="PNG")
    return output_path


def main() -> int:
    args = parse_args()
    run_render(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
