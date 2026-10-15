import type { Geography } from '../contracts/types'

export type Position = [number, number]
export type Rings = Position[][]
export interface RegionFeature {
  type: 'Feature'; properties: Record<string, unknown>
  geometry: { type: 'Polygon'; coordinates: Rings } | { type: 'MultiPolygon'; coordinates: Rings[] }
}
export interface Regions { type: 'FeatureCollection'; coordinateSystem?: Geography['coordinateSystem']; features: RegionFeature[] }
export interface ProjectedRegion { id: string; name: string; polygons: Rings[]; anchor: Position }
export interface SpatialLayer {
  config: NonNullable<Geography['overlays']>[number]
  data: { type: 'FeatureCollection'; coordinateSystem?: Geography['coordinateSystem']; features: { type: 'Feature'; properties: Record<string, unknown>; geometry: { type: string; coordinates: any } }[] }
}
export function validateLayer(raw: unknown, config: SpatialLayer['config'], coordinateSystem: Geography['coordinateSystem']): SpatialLayer {
  const data = raw as SpatialLayer['data']
  if (config.coordinateSystem !== coordinateSystem || (data?.coordinateSystem && data.coordinateSystem !== coordinateSystem)) throw new Error('空间图层坐标系不一致')
  if (data?.type !== 'FeatureCollection' || !Array.isArray(data.features)) throw new Error('空间图层需要 FeatureCollection')
  const kinds = config.kind === 'roads' ? ['LineString', 'MultiLineString'] : config.kind === 'water' ? ['Polygon', 'MultiPolygon'] : ['Point']
  const coordinates = (v: unknown): void => {
    if (!Array.isArray(v) || !v.length) throw new Error('空间图层坐标为空')
    if (typeof v[0] === 'number') {
      if (v.length < 2 || !Number.isFinite(v[0]) || !Number.isFinite(v[1]) || Math.abs(v[0]) > 180 || Math.abs(v[1]) > 85) throw new Error('空间图层经纬度无效')
    } else v.forEach(coordinates)
  }
  for (const f of data.features) {
    if (f.type !== 'Feature' || !kinds.includes(f.geometry?.type)) throw new Error(`空间图层 ${config.kind} 的几何类型不匹配`)
    coordinates(f.geometry.coordinates)
    if (config.kind === 'water') {
      const polygons = f.geometry.type === 'Polygon' ? [f.geometry.coordinates] : f.geometry.coordinates
      for (const rings of polygons) for (const ring of rings) {
        if (ring.length < 4 || ring[0][0] !== ring.at(-1)[0] || ring[0][1] !== ring.at(-1)[1]) throw new Error('水系面环必须闭合')
      }
    }
    if (config.kind === 'roads') {
      const lines = f.geometry.type === 'LineString' ? [f.geometry.coordinates] : f.geometry.coordinates
      if (lines.some((line: unknown[]) => line.length < 2)) throw new Error('道路至少需要两个点')
    }
  }
  return { config, data: { ...data, features: data.features.map(f => ({ ...f, properties: f.properties || {} })) } }
}

export function validateRegions(raw: unknown, config: Geography): Regions {
  const data = raw as Regions
  if (!data || data.type !== 'FeatureCollection' || !Array.isArray(data.features) || !data.features.length) throw new Error('GeoJSON 需要非空 FeatureCollection')
  if (data.coordinateSystem && data.coordinateSystem !== config.coordinateSystem) throw new Error('GeoJSON 与配置的坐标系不一致')
  if (config.basemap && config.basemap.coordinateSystem !== config.coordinateSystem) throw new Error('底图与边界坐标系不一致')
  const ids = new Set<string>(), longitudes: number[] = []
  for (const f of data.features) {
    const id = f?.properties?.[config.idProperty]
    if ((typeof id !== 'string' && typeof id !== 'number') || String(id).trim() === '' || ids.has(String(id))) throw new Error('辖区需要唯一且非空的关联 ID')
    ids.add(String(id))
    if (typeof f.properties[config.nameProperty] !== 'string') throw new Error(`辖区 ${id} 缺少名称`)
    if (f.type !== 'Feature' || !['Polygon', 'MultiPolygon'].includes(f.geometry?.type)) throw new Error(`辖区 ${id} 仅支持 Polygon / MultiPolygon`)
    const polygons = f.geometry.type === 'Polygon' ? [f.geometry.coordinates] : f.geometry.coordinates
    if (!Array.isArray(polygons) || !polygons.length) throw new Error(`辖区 ${id} 无多边形`)
    for (const rings of polygons) {
      if (!Array.isArray(rings) || !rings.length) throw new Error(`辖区 ${id} 无外环`)
      for (const ring of rings) {
        if (!Array.isArray(ring) || ring.length < 4) throw new Error(`辖区 ${id} 的环至少需要四个闭合坐标`)
        for (const p of ring) {
          if (!Array.isArray(p) || p.length < 2 || !Number.isFinite(p[0]) || !Number.isFinite(p[1]) || Math.abs(p[0]) > 180 || Math.abs(p[1]) > 85) throw new Error('坐标必须为有限的经纬度，纬度在 ±85° 内')
          longitudes.push(p[0])
        }
        const first = ring[0], last = ring[ring.length - 1]
        if (first[0] !== last[0] || first[1] !== last[1]) throw new Error('GeoJSON 环必须闭合')
        if (Math.abs(ringArea(ring)) < 1e-12) throw new Error('GeoJSON 环面积为零')
      }
    }
  }
  // This local jurisdiction renderer does not unwrap antimeridian polygons.
  let min = Infinity, max = -Infinity
  for (const lon of longitudes) { min = Math.min(min, lon); max = Math.max(max, lon) }
  if (max - min > 180) throw new Error('跨日期变更线的边界需要先分割，不能用本地辖区投影直接渲染')
  return data
}
export function ringArea(ring: Position[]): number {
  return ring.reduce((a, p, i) => { const q = ring[(i + 1) % ring.length]; return a + p[0] * q[1] - q[0] * p[1] }, 0) / 2
}
export function mercator([lon, lat]: Position): Position {
  // Projection only. GCJ-02 stays GCJ-02; this is not a datum conversion.
  const radius = 6378137, rad = Math.PI / 180
  return [radius * lon * rad, radius * Math.log(Math.tan(Math.PI / 4 + lat * rad / 2))]
}
export function interiorAnchor(rings: Rings): Position {
  const outer = rings[0], ys = outer.map(p => p[1]), y = (Math.min(...ys) + Math.max(...ys)) / 2 + 1e-7
  const cuts: number[] = []
  for (const ring of rings) for (let i = 1; i < ring.length; i++) {
    const a = ring[i - 1], b = ring[i]
    if ((a[1] > y) !== (b[1] > y)) cuts.push(a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1]))
  }
  cuts.sort((a, b) => a - b)
  let best: Position = outer[0], width = -1
  for (let i = 0; i + 1 < cuts.length; i += 2) if (cuts[i + 1] - cuts[i] > width) { width = cuts[i + 1] - cuts[i]; best = [(cuts[i] + cuts[i + 1]) / 2, y] }
  return best
}
export function regionProjector(data: Regions): (position: Position) => Position {
  let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity
  for (const f of data.features) for (const rings of (f.geometry.type === 'Polygon' ? [f.geometry.coordinates] : f.geometry.coordinates)) for (const ring of rings) for (const p of ring) {
    const [x, y] = mercator(p); x0 = Math.min(x0, x); y0 = Math.min(y0, y); x1 = Math.max(x1, x); y1 = Math.max(y1, y)
  }
  const scale = 100 / Math.max(x1 - x0, y1 - y0), cx = (x0 + x1) / 2, cy = (y0 + y1) / 2
  return p => { const [x, y] = mercator(p); return [(x - cx) * scale, (y - cy) * scale] }
}
export function projectRegions(data: Regions, config: Geography): ProjectedRegion[] {
  const project = regionProjector(data)
  const features = data.features.map(f => ({ id: String(f.properties[config.idProperty]), name: String(f.properties[config.nameProperty]), polygons: f.geometry.type === 'Polygon' ? [f.geometry.coordinates] : f.geometry.coordinates }))
  return features.map(f => {
    const polygons = f.polygons.map(rings => rings.map(ring => ring.map(project)))
    const largest = [...polygons].sort((a, b) => Math.abs(ringArea(b[0])) - Math.abs(ringArea(a[0])))[0]
    return { ...f, polygons, anchor: interiorAnchor(largest) }
  })
}
