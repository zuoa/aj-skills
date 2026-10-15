import Projection from 'ol/proj/Projection.js'
import { addCoordinateTransforms, addProjection, get } from 'ol/proj.js'
import type { Geography } from '../contracts/types'
import { mercator } from './geometry'

export function lonLatProjection(system: Geography['coordinateSystem']): Projection {
  if (system === 'WGS84') return get('EPSG:4326')!
  const code = 'GCJ02:LONLAT', existing = get(code)
  if (existing) return existing
  const projection = new Projection({ code, units: 'degrees', extent: [-180,-85,180,85] })
  addProjection(projection)
  // Keep the datum explicit. These formulas only change the display projection;
  // neither direction removes the GCJ-02 offset.
  addCoordinateTransforms(projection, 'EPSG:3857',
    c => mercator([c[0], c[1]]),
    c => [c[0] / 6378137 * 180 / Math.PI, (2 * Math.atan(Math.exp(c[1] / 6378137)) - Math.PI / 2) * 180 / Math.PI])
  return projection
}
