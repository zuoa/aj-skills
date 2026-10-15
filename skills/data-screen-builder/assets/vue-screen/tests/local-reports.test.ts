import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import catalogJson from '../src/config/metrics.json'
import screenJson from '../src/config/screen.json'
import type { Catalog, MetricQuery, MetricResult, Screen } from '../src/contracts/types'
import { fixtureResult } from '../src/data/fixtures.mjs'
import { QueryClient, type QueryState } from '../src/data/client'
import { createReport, LocalReports, parseReportCell } from '../src/data/local-reports'
import { withContext } from '../src/data/context'

const catalog = catalogJson as Catalog, screen = screenJson as Screen
const query = screen.queries.enterprises
const metric = catalog.metrics.find(m => m.id === query.metricId)!
const result = (value = 900): MetricResult => ({ ...fixtureResult(metric, query), dataAsOf: new Date().toISOString(), fetchedAt: new Date().toISOString(), rows: [{ value }] })
const clients: QueryClient[] = []
let values: Map<string, string>
const storage = () => ({ getItem: (key: string) => values.get(key) ?? null, setItem: (key: string, value: string) => { values.set(key, value) } })
const reports = (id = 'screen', path = '/') => new LocalReports(id, catalog, storage, path)
beforeEach(() => { values = new Map(); vi.useFakeTimers(); vi.setSystemTime(new Date('2026-10-14T00:00:00Z')) })
afterEach(() => { clients.forEach(c => c.dispose()); clients.length = 0; vi.useRealTimers() })

describe('local metric reports', () => {
  it('persists across reloads and rolling clocks while isolating screens, paths and query context', () => {
    const store = reports()
    const q = withContext(query, {}, 24, Date.now())
    store.save(q, result())
    expect(reports().get(withContext(query, {}, 24, Date.now() + 60000))?.rows[0].value).toBe(900)
    expect(reports('another').get(q)).toBeUndefined()
    expect(reports('screen', '/another/').get(q)).toBeUndefined()
    for (const next of [withContext(query, { area: 'north' }, 24, Date.now()), withContext(query, {}, 168, Date.now()), { ...q, limit: 1 }, { ...q, timeRange: { ...q.timeRange, timezone: 'UTC' } }]) expect(store.get(next)).toBeUndefined()
  })
  it('merges different tabs and reloads saved and removed values', () => {
    const first = reports(), second = reports()
    const north = { ...query, filters: { area: 'north' } }
    first.save(query, result(900)); second.save(north, result(80))
    first.reload()
    expect(first.get(query)?.rows[0].value).toBe(900)
    expect(first.get(north)?.rows[0].value).toBe(80)
    second.remove(query); first.reload()
    expect(first.get(query)).toBeUndefined()
    expect(first.get(north)?.rows[0].value).toBe(80)
  })
  it('rejects malformed results and expires reports when the metric definition changes', () => {
    const store = reports()
    expect(() => store.save(query, { ...result(), rows: [{ value: 'wrong' }] })).toThrow()
    store.save(query, result())
    const changed = structuredClone(catalog); changed.metrics[0].unit = '千家'
    const updated = new LocalReports('screen', changed, storage, '/')
    expect(updated.get(query)).toBeUndefined()
    expect(updated.error).toContain('不一致')
  })
  it('ignores damaged cache and never applies a failed write', () => {
    const store = reports()
    values.set(store.storageKey, '{invalid')
    store.reload()
    expect(store.get(query)).toBeUndefined(); expect(store.error).toContain('无法读取')
    const denied = new LocalReports('screen', catalog, () => ({ getItem: storage().getItem, setItem: () => { throw new Error('quota') } }), '/')
    expect(() => denied.save(query, result())).toThrow('修改尚未生效')
    expect(denied.get(query)).toBeUndefined()
    const unavailable = new LocalReports('screen', catalog, () => { throw new Error('denied') }, '/')
    expect(unavailable.get(query)).toBeUndefined()
    expect(() => unavailable.save(query, result())).toThrow('保存失败')
  })
  it('preserves zero, unknown, negative, decimals, boolean and empty records without aggregation', () => {
    for (const [input, value] of [['0', 0], ['', null], ['-1.25', -1.25]] as const) expect(createReport(catalog, query, [{ value: input }], new Date().toISOString()).rows).toEqual([{ value }])
    expect(() => createReport(catalog, query, [{ value: '1' }, { value: '2' }], new Date().toISOString())).toThrow('单值指标')
    expect(createReport(catalog, query, [], new Date().toISOString()).rows).toEqual([])
    expect(parseReportCell('false', { name: 'flag', type: 'boolean' })).toBe(false)
    expect(() => parseReportCell('Infinity', { name: 'value', type: 'number' })).toThrow()
    expect(() => createReport(catalog, query, [{ value: '5' }], 'tomorrow')).toThrow()
    expect(() => createReport(catalog, query, [{ value: '5' }], new Date(Date.now() + 10000).toISOString())).toThrow()
    const q = screen.queries.energy
    expect(createReport(catalog, q, [{ time: '2026-10-13T01:00:00+08:00', value: '18.2' }], new Date().toISOString()).rows[0]).toEqual({ time: '2026-10-12T17:00:00.000Z', value: 18.2 })
  })
  it('updates all subscribers immediately, cancels a pending response, survives refresh and restores the provider', async () => {
    let resolve!: (value: MetricResult) => void, signal!: AbortSignal
    const provider = vi.fn().mockImplementationOnce((_q, s) => { signal = s; return new Promise(r => { resolve = r }) }).mockResolvedValue(result(368))
    const store = reports(), client = new QueryClient({ query: provider }, catalog, 8000, store)
    clients.push(client)
    let a!: QueryState, b!: QueryState
    client.subscribe(query, state => { a = state }); client.subscribe(query, state => { b = state })
    store.save(query, result(900))
    expect(a.result?.rows[0].value).toBe(900); expect(b.local).toBe(true); expect(signal.aborted).toBe(true)
    resolve(result(1)); await vi.advanceTimersByTimeAsync(0)
    client.refresh(); await vi.advanceTimersByTimeAsync(metric.refreshMs * 2)
    expect(a.result?.rows[0].value).toBe(900); expect(provider).toHaveBeenCalledTimes(1)
    store.remove(query); await vi.advanceTimersByTimeAsync(0)
    expect(a.result?.rows[0].value).toBe(368); expect(a.local).toBe(false)
  })
  it('uses persisted reports without HTTP even while paused and tracks the actual data age', async () => {
    const store = reports(); store.save(query, result())
    const provider = vi.fn().mockRejectedValue(new Error('HTTP 503'))
    const client = new QueryClient({ query: provider }, catalog, 8000, store); clients.push(client)
    client.setPaused(true)
    let state!: QueryState
    client.subscribe(query, s => { state = s })
    expect(state.local).toBe(true); expect(provider).not.toHaveBeenCalled()
    store.save(query, result(0)); expect(state.result?.rows[0].value).toBe(0)
    await vi.advanceTimersByTimeAsync(metric.staleAfterMs)
    expect(state.stale).toBe(true)
    store.remove(query); expect(state.result).toBeUndefined()
    client.setPaused(false); await vi.advanceTimersByTimeAsync(0)
    expect(state.error).toBe('HTTP 503'); expect(state.local).toBe(false)
  })
})
