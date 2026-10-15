import type { Cell, MetricQuery } from '../contracts/types'

export function withContext(query: MetricQuery, filters: Record<string, Cell>, hours: number, now: number): MetricQuery {
  return { ...query, filters: { ...query.filters, ...filters }, timeRange: {
    from: new Date(now - hours * 3600000).toISOString(), to: new Date(now).toISOString(), timezone: query.timeRange.timezone,
  } }
}
