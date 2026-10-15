export type Cell = string | number | boolean | null
export type FieldType = 'string' | 'number' | 'boolean' | 'timestamp'
export interface Field { name: string; type: FieldType }
export type Granularity = 'none' | 'hour' | 'day' | 'week' | 'month'
export interface Metric {
  id: string; name: string; definition: string; unit: string; precision: number
  aggregation: 'sum' | 'avg' | 'ratio' | 'distinct' | 'last' | 'none'
  positiveDirection: 'up' | 'down' | 'neutral'
  dimensions: Field[]; granularities: Granularity[]
  refreshMs: number; staleAfterMs: number; source: string; owner: string
}
export interface Catalog { version: '1'; metrics: Metric[] }
export interface MetricQuery {
  metricId: string; dimensions: string[]; filters: Record<string, Cell | Cell[]>
  timeRange: { from: string; to: string; timezone: string }
  granularity: Granularity; orderBy?: { field: string; direction: 'asc' | 'desc' }; limit?: number
}
export interface MetricResult {
  version: '1'; metricId: string; fields: Field[]; rows: Record<string, Cell>[]
  dataAsOf: string; fetchedAt: string; quality: 'ok' | 'partial' | 'stale'
}
export type ComponentType = 'metric' | 'trend' | 'ranking' | 'composition' | 'table' | 'heatmap' | 'map' | 'status' | 'alerts'
export interface Geography {
  renderer: 'three' | 'openlayers' | 'svg'
  source: string; coordinateSystem: 'WGS84' | 'GCJ02'
  idProperty: string; nameProperty: string; depth: number
  basemap?: { url: string; attribution: string; coordinateSystem: 'WGS84' | 'GCJ02' }
  overlays?: { kind: 'roads' | 'water' | 'poi'; source: string; coordinateSystem: 'WGS84' | 'GCJ02'; nameProperty?: string; imageProperty?: string }[]
}
export interface Binding {
  id: string; title: string; type: string; queryId: string
  caption?: string
  geography?: Geography
  fields: Partial<Record<'x' | 'y' | 'value' | 'label' | 'series' | 'longitude' | 'latitude', string>>
  layout: { col: number; row: number; width: number; height: number }
  thresholds?: { warning: number; critical: number; direction: 'above' | 'below' }
  interaction?: { field: string; filter: string }
}
export interface Screen {
  version: '1'; id: string; title: string; mode: 'presentation' | 'monitoring'
  canvas: { width: number; height: number }; queries: Record<string, MetricQuery>; components: Binding[]
  visuals?: { style: 'cinematic' | 'restrained'; intensity: 'low' | 'medium' | 'high' }
}
export interface Provider { query(query: MetricQuery, signal: AbortSignal): Promise<MetricResult> }
