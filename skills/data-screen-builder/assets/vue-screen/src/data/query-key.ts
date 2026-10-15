import type { MetricQuery } from '../contracts/types'

function canonical(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(canonical)
  if (value && typeof value === 'object') return Object.fromEntries(Object.entries(value).sort(([a], [b]) => a.localeCompare(b)).map(([k, v]) => [k, canonical(v)]))
  return value
}
export function queryKey(query: MetricQuery): string { return JSON.stringify(canonical(query)) }

// Manual reports follow a rolling window of the same length, never another scope.
export function reportKey(query: MetricQuery): string {
  return queryKey({ ...query, timeRange: { ...query.timeRange, from: 'rolling', to: String(Date.parse(query.timeRange.to) - Date.parse(query.timeRange.from)) } })
}
