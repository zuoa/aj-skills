import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { QueryClient, queryKey, type QueryState } from '../src/data/client'
import { createMockProvider } from '../src/data/mock'
import { createHttpProvider } from '../src/data/http'
import { withContext } from '../src/data/context'
import { canRetainWindow, isResultStale } from '../src/data/retention'
import { fixtureResult } from '../src/data/fixtures.mjs'
import { assertConfig, assertQuery, assertResult } from '../src/contracts/validate.mjs'
import catalogJson from '../src/config/metrics.json'
import screenJson from '../src/config/screen.json'
import manifest from '../src/config/component-types.json'
import type { Catalog, Screen, MetricResult, Provider } from '../src/contracts/types'

const catalog = catalogJson as Catalog, screen = screenJson as Screen
const query = screen.queries.enterprises
const metric = catalog.metrics.find(m => m.id === query.metricId)!
const result = (): MetricResult => fixtureResult(metric, query)
const types = [...manifest.builtin, ...manifest.custom]
const clients: QueryClient[] = []
function client(provider: Provider, timeout = 8000) { const c = new QueryClient(provider, catalog, timeout); clients.push(c); return c }
beforeEach(() => { vi.useFakeTimers(); vi.setSystemTime(new Date('2026-10-12T00:00:00Z')) })
afterEach(() => { for (const c of clients) c.dispose(); clients.length = 0; vi.useRealTimers() })

describe('shared querying and failures', () => {
  it('shares equivalent queries and keeps the request alive until the last subscriber leaves', async () => {
    const queryFn = vi.fn(async () => result())
    const c = client({ query: queryFn })
    const a = c.subscribe(query, () => {}), b = c.subscribe(structuredClone(query), () => {})
    await vi.advanceTimersByTimeAsync(0)
    expect(queryFn).toHaveBeenCalledTimes(1)
    a(); await vi.advanceTimersByTimeAsync(metric.refreshMs)
    expect(queryFn).toHaveBeenCalledTimes(2)
    b(); expect(vi.getTimerCount()).toBe(0)
  })
  it('retains last successful data on failure, marks age stale and recovers', async () => {
    const queryFn = vi.fn().mockResolvedValueOnce(result()).mockRejectedValueOnce(new Error('network down')).mockResolvedValue(result())
    let state!: QueryState
    const c = client({ query: queryFn })
    c.subscribe(query, s => state = s)
    await vi.advanceTimersByTimeAsync(metric.refreshMs)
    expect(state.result?.rows[0].value).toBe(368)
    expect(state.error).toBe('network down')
    c.setPaused(true)
    await vi.advanceTimersByTimeAsync(metric.staleAfterMs)
    expect(state.stale).toBe(true)
    c.setPaused(false); await vi.advanceTimersByTimeAsync(0)
    expect(state.error).toBeUndefined()
  })
  it('times out non-cooperative adapters and releases loading', async () => {
    let state!: QueryState
    const c = client({ query: () => new Promise(() => {}) }, 1000)
    c.subscribe(query, s => state = s)
    await vi.advanceTimersByTimeAsync(1000)
    expect(state.loading).toBe(false)
    expect(state.error).toContain('超时')
  })
  it('aborts unsubscribed requests and a late response cannot update the new filter', async () => {
    let resolveOld!: (value: MetricResult) => void
    let oldSignal!: AbortSignal
    const c = client({ query: vi.fn().mockImplementationOnce((_q, signal) => { oldSignal = signal; return new Promise(resolve => resolveOld = resolve) }).mockResolvedValue({ ...result(), rows: [{ value: 132 }] }) })
    const old = c.subscribe(query, () => {})
    old()
    let state!: QueryState
    c.subscribe({ ...query, filters: { area: 'north' } }, s => state = s)
    await vi.advanceTimersByTimeAsync(0)
    resolveOld(result()); await vi.advanceTimersByTimeAsync(0)
    expect(oldSignal.aborted).toBe(true)
    expect(state.result?.rows[0].value).toBe(132)
  })
  it('pause cancels in-flight work and resume fetches current data', async () => {
    let signal!: AbortSignal
    const queryFn = vi.fn().mockImplementationOnce((_q, s) => { signal = s; return new Promise(() => {}) }).mockResolvedValue(result())
    let state!: QueryState
    const c = client({ query: queryFn })
    c.subscribe(query, s => state = s)
    c.setPaused(true)
    expect(signal.aborted).toBe(true)
    await vi.advanceTimersByTimeAsync(60000)
    expect(queryFn).toHaveBeenCalledTimes(1)
    c.setPaused(false); await vi.advanceTimersByTimeAsync(0)
    expect(state.result).toBeDefined()
  })
  it('does not repeatedly retry authentication failures', async () => {
    const queryFn = vi.fn().mockRejectedValue(new Error('HTTP 401'))
    const c = client({ query: queryFn })
    c.subscribe(query, () => {})
    await vi.advanceTimersByTimeAsync(600000)
    expect(queryFn).toHaveBeenCalledTimes(1)
    c.refresh(); await vi.advanceTimersByTimeAsync(0)
    expect(queryFn).toHaveBeenCalledTimes(2)
  })
  it('rejects malformed results instead of exposing them as valid data', async () => {
    let state!: QueryState
    const c = client({ query: async () => ({ ...result(), metricId: 'wrong.metric' }) })
    c.subscribe(query, s => state = s)
    await vi.advanceTimersByTimeAsync(0)
    expect(state.result).toBeUndefined()
    expect(state.error).toContain('mismatch')
  })
})

describe('contract and adapter', () => {
  it('retains a moving window only for the same scope, and evaluates its actual data age', () => {
    const q = withContext(query, {}, 24, Date.now())
    const next = withContext(query, {}, 24, Date.now() + 60000)
    expect(canRetainWindow(q, next)).toBe(true)
    expect(canRetainWindow(q, withContext(query, { area: 'north' }, 24, Date.now()))).toBe(false)
    expect(canRetainWindow(q, withContext(query, {}, 168, Date.now()))).toBe(false)
    expect(isResultStale(result(), metric.staleAfterMs, Date.now() + metric.staleAfterMs)).toBe(true)
  })
  it('all shipped fixtures satisfy their declared query and result shapes', async () => {
    assertConfig(catalog, screen, types)
    const provider = createMockProvider(catalog)
    for (const q of Object.values(screen.queries)) {
      const m = catalog.metrics.find(m => m.id === q.metricId)!
      expect(() => assertResult(m, q, fixtureResult(m, q))).not.toThrow()
      await expect(provider.query(q, new AbortController().signal)).resolves.toHaveProperty('metricId', q.metricId)
    }
  })
  it('HTTP accepts the identical protocol with query, credentials and cancellation', async () => {
    const fetcher = vi.fn(async () => new Response(JSON.stringify(result()), { status: 200 }))
    const controller = new AbortController()
    const provider = createHttpProvider('/api/metrics/query', fetcher)
    const data = await provider.query(query, controller.signal)
    assertResult(metric, query, data)
    expect(fetcher).toHaveBeenCalledWith('/api/metrics/query', expect.objectContaining({ method: 'POST', credentials: 'same-origin', body: JSON.stringify(query), signal: controller.signal }))
  })
  it('HTTP failures do not fall back to mock and do not display upstream secrets', async () => {
    const provider = createHttpProvider('/api/metrics/query', vi.fn(async () => new Response('private upstream token', { status: 503 })))
    await expect(provider.query(query, new AbortController().signal)).rejects.toThrow('HTTP 503')
    await expect(provider.query(query, new AbortController().signal)).rejects.not.toThrow('private')
    expect(() => createHttpProvider('//other-host/path')).toThrow()
    expect(() => createHttpProvider('/\\other-host/path')).toThrow()
  })
  it('zero, missing value, and no records are distinct', () => {
    for (const rows of [[{ value: 0 }], [{ value: null }], []]) expect(() => assertResult(metric, query, { ...result(), rows })).not.toThrow()
    expect(() => assertResult(metric, query, { ...result(), rows: [{}] })).toThrow()
    expect(() => assertResult(metric, query, { ...result(), rows: [{ value: '0' }] })).toThrow()
    expect(() => assertResult(metric, query, { ...result(), rows: [{ value: Infinity }] })).toThrow()
  })
  it('validates dimensions, granularity, window order and timezone', () => {
    expect(() => assertQuery(metric, { ...query, dimensions: ['unknown'] })).toThrow()
    expect(() => assertQuery(metric, { ...query, granularity: 'hour' })).toThrow()
    expect(() => assertQuery(metric, { ...query, filters: { area: 42 } })).toThrow()
    expect(() => assertQuery(metric, { ...query, timeRange: { ...query.timeRange, timezone: 'wrong/zone' } })).toThrow()
    expect(() => assertQuery(metric, { ...query, timeRange: { ...query.timeRange, from: query.timeRange.to } })).toThrow()
  })
  it('preserves gaps and rejects impossible result timestamps', () => {
    const q = screen.queries.energy, m = catalog.metrics.find(m => m.id === q.metricId)!
    const data = fixtureResult(m, q)
    expect(data.rows.some(row => row.value === null)).toBe(true)
    data.rows[0].time = '2026-02-30T00:00:00Z'
    expect(() => assertResult(m, q, data)).toThrow()
  })
  it('does not recalculate ratio or distinct values when selecting regions', () => {
    const q = screen.queries.occupancy, m = catalog.metrics.find(m => m.id === q.metricId)!
    expect(m.aggregation).toBe('ratio')
    expect(fixtureResult(m, { ...q, filters: { area: 'north' } }).rows[0].value).toBe(86.4)
    expect(metric.aggregation).toBe('distinct')
  })
  it('canonical keys include filters, window, timezone, ordering, limit and granularity', () => {
    expect(queryKey({ ...query, filters: { a: '1', b: '2' } })).toBe(queryKey({ ...query, filters: { b: '2', a: '1' } }))
    for (const q of [{ ...query, filters: { area: 'north' } }, { ...query, limit: 1 }, { ...query, orderBy: { field: 'value', direction: 'desc' as const } }, { ...query, granularity: 'hour' as const }, { ...query, timeRange: { ...query.timeRange, timezone: 'UTC' } }]) expect(queryKey(q)).not.toBe(queryKey(query))
  })
  it('context selection affects every query and maintains a half-open UTC window with IANA interpretation', () => {
    const now = Date.now()
    for (const q of Object.values(screen.queries)) {
      const next = withContext(q, { area: 'north' }, 24, now)
      expect(next.filters.area).toBe('north')
      expect(Date.parse(next.timeRange.to) - Date.parse(next.timeRange.from)).toBe(86400000)
      expect(next.timeRange.timezone).toBe('Asia/Shanghai')
    }
  })
  it('rejects broken bindings, overlaps, IDs and unregistered components', () => {
    for (const mutate of [
      (s: Screen) => s.components[0].queryId = 'missing',
      (s: Screen) => s.components[0].fields.value = 'unknown',
      (s: Screen) => s.components[0].layout.width = 12,
      (s: Screen) => s.components[1].id = s.components[0].id,
      (s: Screen) => s.components[0].type = 'unregistered',
    ]) { const s = structuredClone(screen); mutate(s); expect(() => assertConfig(catalog, s, types)).toThrow() }
  })
})
