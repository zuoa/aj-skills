#!/usr/bin/env python3
"""Import AMap district boundaries without exposing the server-side API key."""
import argparse
import json
import math
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen


def area(ring):
    return sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(ring, ring[1:])) / 2


def inside(point, ring):
    x, y = point
    hit = False
    for a, b in zip(ring, ring[1:]):
        if (a[1] > y) != (b[1] > y) and x < a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1]):
            hit = not hit
    return hit


def parse_polyline(polyline):
    if not isinstance(polyline, str) or not polyline.strip():
        raise ValueError('该结果没有边界；高德不返回街道/乡镇边界，请换区县或提供自定义 GeoJSON')
    rings = []
    for part in polyline.split('|'):
        try:
            ring = [[float(v) for v in point.split(',')] for point in part.split(';') if point.strip()]
        except ValueError:
            raise ValueError('边界含无效坐标') from None
        if any(len(p) != 2 or not all(math.isfinite(v) for v in p) or abs(p[0]) > 180 or abs(p[1]) > 85 for p in ring):
            raise ValueError('边界不是有效的经纬度')
        if len(ring) < 3:
            raise ValueError('边界环至少需要三个不同的顶点')
        if ring[-1] != ring[0]:
            ring.append(ring[0])
        if abs(area(ring)) < 1e-12:
            raise ValueError('边界环面积为零')
        rings.append(ring)
    # Detached parts form MultiPolygon; nested parts become holes / islands.
    rings.sort(key=lambda r: abs(area(r)), reverse=True)
    parents, depths = [], []
    for i, ring in enumerate(rings):
        containers = [j for j in range(i) if inside(ring[0], rings[j])]
        parent = min(containers, key=lambda j: abs(area(rings[j]))) if containers else None
        parents.append(parent); depths.append(0 if parent is None else depths[parent] + 1)
    polygons, by_ring = [], {}
    for i, ring in enumerate(rings):
        outer = depths[i] % 2 == 0
        oriented = ring if (area(ring) > 0) == outer else ring[::-1]
        if outer:
            by_ring[i] = [oriented]; polygons.append(by_ring[i])
        else:
            by_ring[parents[i]].append(oriented)
    return {'type': 'Polygon', 'coordinates': polygons[0]} if len(polygons) == 1 else {'type': 'MultiPolygon', 'coordinates': polygons}


def convert_response(response, keywords, adcode=None):
    if not isinstance(response, dict):
        raise ValueError('高德响应需要 JSON 对象')
    if str(response.get('status')) != '1' or str(response.get('infocode', '10000')) != '10000':
        # API payload/error URLs can contain keys. Only emit the bounded status code.
        code = str(response.get('infocode', 'unknown'))
        raise ValueError('高德查询失败，状态码 ' + (code if code.isdigit() and len(code) <= 6 else 'unknown'))
    districts = response.get('districts', [])
    if not isinstance(districts, list):
        raise ValueError('高德返回的辖区列表无效')
    candidates = [d for d in districts if isinstance(d, dict) and ((str(d.get('adcode')) == str(adcode)) if adcode else (d.get('name') == keywords or str(d.get('adcode')) == keywords))]
    if not candidates and len(districts) == 1 and not adcode:
        candidates = districts
    if len(candidates) != 1:
        raise ValueError('辖区名称无结果或存在歧义，请使用唯一 adcode 指定辖区')
    district = candidates[0]
    return {
        'type': 'FeatureCollection', 'coordinateSystem': 'GCJ02',
        'source': 'AMap district API', 'fetchedAt': datetime.now(timezone.utc).isoformat(),
        'features': [{'type': 'Feature', 'properties': {'adcode': str(district['adcode']), 'name': district['name'], 'level': district.get('level'), 'coordinateSystem': 'GCJ02', 'source': 'AMap district API'}, 'geometry': parse_polyline(district.get('polyline'))}],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--keywords', required=True, help='辖区名或 adcode；推荐 adcode')
    parser.add_argument('--adcode', help='核对并指定唯一结果')
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--response-json', type=Path, help='从保存的 API 响应离线导入')
    parser.add_argument('--force', action='store_true', help='覆盖已有输出')
    args = parser.parse_args()
    try:
        if args.output.exists() and not args.force:
            raise ValueError('输出已存在；换路径或明确使用 --force')
        if args.response_json:
            response = json.loads(args.response_json.read_text())
        else:
            key = os.environ.get('AMAP_WEB_SERVICE_KEY')
            if not key:
                raise ValueError('请在服务端环境设置 AMAP_WEB_SERVICE_KEY（Web 服务 API Key），或使用 --response-json')
            params = urlencode({'key': key, 'keywords': args.adcode or args.keywords, 'subdistrict': 0, 'extensions': 'all', 'output': 'JSON'})
            try:
                with urlopen('https://restapi.amap.com/v3/config/district?' + params, timeout=20) as result:
                    response = json.load(result)
            except (URLError, TimeoutError, OSError):
                raise ValueError('高德请求失败，请检查网络、Key 权限及配额；不输出包含 Key 的请求 URL') from None
        geo = convert_response(response, args.keywords, args.adcode)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(geo, ensure_ascii=False, indent=2) + '\n')
        print(f'已保存 {args.output}；坐标系 GCJ02；关联字段 adcode，名称字段 name')
    except (ValueError, OSError, KeyError, TypeError):
        # Only our own diagnostic strings are safe to display; JSON decoder context may contain credentials.
        error = sys.exc_info()[1]
        message = str(error) if type(error) is ValueError else '导入失败，请检查输入文件和输出路径'
        print(message, file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
