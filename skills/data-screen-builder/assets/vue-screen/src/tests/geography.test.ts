import { describe, expect, it } from 'vitest'
import geoJson from '../../public/districts.demo.geo.json'
import screenJson from '../config/screen.json'
import catalogJson from '../config/metrics.json'
import designsJson from '../config/designs.json'
import manifest from '../config/component-types.json'
import type { Catalog, Geography, Screen } from '../contracts/types'
import { interiorAnchor, mercator, projectRegions, validateRegions, validateLayer, regionProjector } from '../geo/geometry'
import { withDesign, type DesignProfile } from '../display/design'
import { assertConfig } from '../contracts/validate.mjs'
import { transform } from 'ol/proj.js'
import { lonLatProjection } from '../geo/projection'

const screen = screenJson as Screen, config = screen.components.find(b => b.id === 'map')!.geography!
describe('spatial inputs', () => {
  it('retains holes, detached islands and stable IDs across projection', () => {
    const data = validateRegions(geoJson, config), projected = projectRegions(data, config)
    expect(projected.map(f => f.id)).toEqual(['north', 'east', 'south', 'west'])
    expect(projected[0].polygons[0]).toHaveLength(2)
    expect(projected[2].polygons).toHaveLength(2)
    expect(projected.flatMap(f => f.polygons).flat(2).every(p => p.every(Number.isFinite))).toBe(true)
  })
  it('places an interior label outside a hole', () => {
    const p = interiorAnchor([[[0,0],[10,0],[10,10],[0,10],[0,0]], [[4,4],[6,4],[6,6],[4,6],[4,4]]])
    expect(p[0] < 4 || p[0] > 6).toBe(true)
    expect(p[1]).toBeGreaterThan(0); expect(p[1]).toBeLessThan(10)
  })
  it('projects geographic coordinates without pretending to convert the datum', () => {
    expect(mercator([0,0])[0]).toBe(0); expect(mercator([0,0])[1]).toBeCloseTo(0)
    expect(mercator([1,0])[0]).toBeCloseTo(111319.49, 1)
    expect(() => validateRegions(geoJson, { ...config, coordinateSystem: 'GCJ02' })).toThrow('坐标系')
  })
  it('names the GCJ-02 projection explicitly and keeps coordinates on round trip', () => {
    const projection = lonLatProjection('GCJ02'), point = [121.4,31.2]
    expect(projection.getCode()).toBe('GCJ02:LONLAT')
    const display = transform(point, projection, 'EPSG:3857'), restored = transform(display, 'EPSG:3857', projection)
    expect(display[0]).toBeCloseTo(mercator([121.4,31.2])[0])
    expect(restored[0]).toBeCloseTo(point[0], 6); expect(restored[1]).toBeCloseTo(point[1], 6)
    expect(lonLatProjection('WGS84').getCode()).toBe('EPSG:4326')
  })
  it.each(['duplicate', 'unclosed', 'nonfinite', 'empty', 'wrongGeometry'])('rejects %s rather than making a fake region', failure => {
    const data = structuredClone(geoJson) as any
    if (failure === 'duplicate') data.features[1].properties.area = 'north'
    if (failure === 'unclosed') data.features[0].geometry.coordinates[0].pop()
    if (failure === 'nonfinite') data.features[0].geometry.coordinates[0][0][0] = Infinity
    if (failure === 'empty') data.features = []
    if (failure === 'wrongGeometry') data.features[0].geometry.type = 'LineString'
    expect(() => validateRegions(data, config)).toThrow()
  })
  it('rejects a mismatched tile datum', () => {
    expect(() => validateRegions(geoJson, { ...config, basemap: { url: '/tiles/{z}/{x}/{y}.png', attribution: 'example', coordinateSystem: 'GCJ02' } })).toThrow('坐标系')
  })
  it('uses the boundary projection for roads, water and POIs and rejects invalid layers', () => {
    const data = validateRegions(geoJson, config), project = regionProjector(data)
    const feature = { type: 'Feature', properties: { name: '示例机构' }, geometry: { type: 'Point', coordinates: [121.4,31.2] } }
    const poi = { type: 'FeatureCollection', coordinateSystem: 'WGS84', features: [feature] }
    const layer = { source: '/poi.json', kind: 'poi' as const, coordinateSystem: 'WGS84' as const }
    expect(validateLayer(poi, layer, 'WGS84').data.features).toHaveLength(1)
    expect(project([121.4,31.2]).every(Number.isFinite)).toBe(true)
    expect(() => validateLayer(poi, { ...layer, kind: 'roads' }, 'WGS84')).toThrow('几何类型')
    expect(() => validateLayer(poi, layer, 'GCJ02')).toThrow('坐标系')
    expect(() => validateLayer({ ...poi, features: [{...feature, geometry: {...feature.geometry, coordinates: [NaN,31.2]}}] }, layer, 'WGS84')).toThrow('经纬度')
  })
})
describe('content profiles', () => {
  it('changes composition and palette without changing queries or field bindings', () => {
    const catalog = catalogJson as Catalog
    for (const design of designsJson.profiles as DesignProfile[]) {
      const result = withDesign(screen, design)
      assertConfig(catalog, result, [...manifest.builtin, ...manifest.custom])
      expect(result.queries).toBe(screen.queries)
      expect(result.components.map(b => b.fields)).toEqual(screen.components.map(b => b.fields))
    }
    expect(withDesign(screen, designsJson.profiles[1] as DesignProfile).components.find(b => b.id === 'map')!.layout.col).toBe(1)
    expect(new Set(designsJson.profiles.map(p => p.tokens.background)).size).toBe(3)
  })
  it('does not silently accept layouts that name nonexistent components', () => {
    expect(() => withDesign(screen, { ...designsJson.profiles[0], layouts: { missing: { col: 1, row: 1, width: 1, height: 1 } } } as DesignProfile)).toThrow('未知组件')
  })
  it('rejects geography on non-map widgets and invalid coordinate pairing', () => {
    const edited = structuredClone(screen)
    edited.components[0].geography = config
    expect(() => assertConfig(catalogJson, edited, manifest.builtin)).toThrow('map component')
    const mismatch = structuredClone(screen), geo = mismatch.components.find(b => b.id === 'map')!.geography as Geography
    geo.basemap = { url: '/tiles/{z}/{x}/{y}.png', attribution: 'example', coordinateSystem: 'GCJ02' }
    expect(() => assertConfig(catalogJson, mismatch, manifest.builtin)).toThrow('coordinate system mismatch')
  })
})
