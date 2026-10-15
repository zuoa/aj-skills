import type { MetricQuery, MetricResult } from '../contracts/types'
import { reportKey } from './query-key'

// Retain across a moving window, never across a different region/metric/grain.
export function canRetainWindow(previous: MetricQuery | undefined, next: MetricQuery): boolean {
  if (!previous) return false
  return reportKey(previous) === reportKey(next)
}
export function isResultStale(result: MetricResult | undefined, staleAfterMs: number, now: number): boolean {
  return Boolean(result && (result.quality === 'stale' || now - Date.parse(result.dataAsOf) >= staleAfterMs))
}
