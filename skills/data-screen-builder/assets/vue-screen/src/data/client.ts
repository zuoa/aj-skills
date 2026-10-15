import { assertQuery, assertResult } from '../contracts/validate.mjs'
import type { Catalog, Metric, MetricQuery, MetricResult, Provider } from '../contracts/types'
import { queryKey } from './query-key'
import type { LocalReports } from './local-reports'
export { queryKey } from './query-key'

export interface QueryState { loading: boolean; result?: MetricResult; error?: string; stale: boolean; local?: boolean }
type Listener = (state: QueryState) => void
interface Entry {
  query: MetricQuery; metric: Metric; state: QueryState; listeners: Set<Listener>
  due: number; failures: number; generation: number; controller?: AbortController
}
export class QueryClient {
  private entries = new Map<string, Entry>()
  private timer?: ReturnType<typeof setInterval>
  private paused = false
  private stopReports?: () => void
  constructor(private provider: Provider, private catalog: Catalog, private timeoutMs = 8000, private reports?: LocalReports) {
    this.stopReports = reports?.subscribe(() => {
      for (const entry of this.entries.values()) {
        const local = reports.get(entry.query)
        if (!local && !entry.state.local) continue
        entry.generation++; entry.controller?.abort(); entry.controller = undefined
        entry.state = { loading: false, stale: false, result: local, local: Boolean(local) }
        entry.failures = 0; entry.due = local ? Infinity : 0
        this.publish(entry)
      }
      this.tick()
    })
  }

  subscribe(query: MetricQuery, listener: Listener): () => void {
    const metric = this.catalog.metrics.find(m => m.id === query.metricId)!
    assertQuery(metric, query)
    const key = queryKey(query)
    let entry = this.entries.get(key)
    if (!entry) {
      const local = this.reports?.get(query)
      entry = { query: structuredClone(query), metric, state: { loading: false, stale: false, result: local, local: Boolean(local) }, listeners: new Set(), due: local ? Infinity : 0, failures: 0, generation: 0 }
      this.entries.set(key, entry)
    }
    entry.listeners.add(listener)
    listener({ ...entry.state })
    if (!this.timer) this.timer = setInterval(() => this.tick(), 250)
    this.tick()
    return () => {
      entry!.listeners.delete(listener)
      if (!entry!.listeners.size) {
        entry!.generation++
        entry!.controller?.abort()
        this.entries.delete(key)
      }
      if (!this.entries.size && this.timer) { clearInterval(this.timer); this.timer = undefined }
    }
  }
  setPaused(paused: boolean): void {
    this.paused = paused
    for (const entry of this.entries.values()) {
      if (paused) {
        entry.generation++; entry.controller?.abort(); entry.controller = undefined
        entry.state.loading = false; this.publish(entry)
      } else entry.due = 0
    }
    this.tick()
  }
  refresh(): void { for (const entry of this.entries.values()) entry.due = 0; this.tick() }
  dispose(): void {
    this.stopReports?.()
    for (const entry of this.entries.values()) { entry.generation++; entry.controller?.abort() }
    this.entries.clear()
    if (this.timer) clearInterval(this.timer)
    this.timer = undefined
  }
  private publish(entry: Entry): void {
    for (const listener of entry.listeners) listener({ ...entry.state })
  }
  private tick(): void {
    const now = Date.now()
    for (const entry of this.entries.values()) {
      const stale = Boolean(entry.state.result && (entry.state.result.quality === 'stale' || now - Date.parse(entry.state.result.dataAsOf) >= entry.metric.staleAfterMs))
      if (stale !== entry.state.stale) { entry.state.stale = stale; this.publish(entry) }
      if (!this.paused && !entry.state.local && !entry.state.loading && entry.due <= now) void this.fetch(entry)
    }
  }
  private async fetch(entry: Entry): Promise<void> {
    const controller = new AbortController()
    const generation = ++entry.generation
    entry.controller = controller
    entry.state.loading = true
    this.publish(entry)
    let timeout: ReturnType<typeof setTimeout> | undefined
    let detachAbort = () => {}
    try {
      // Race cancellation too: a non-cooperative adapter cannot pin loading forever.
      const cancelled = new Promise<never>((_, reject) => {
        const onAbort = () => reject(new Error('请求已取消或超时'))
        controller.signal.addEventListener('abort', onAbort, { once: true })
        detachAbort = () => controller.signal.removeEventListener('abort', onAbort)
        timeout = setTimeout(() => controller.abort(), this.timeoutMs)
      })
      const result = await Promise.race([this.provider.query(entry.query, controller.signal), cancelled])
      if (generation !== entry.generation) return
      assertResult(entry.metric, entry.query, result)
      entry.state.result = result
      entry.state.error = undefined
      entry.failures = 0
    } catch (error) {
      if (generation !== entry.generation) return
      entry.state.error = error instanceof Error ? error.message : '数据读取失败'
      entry.failures++
    } finally {
      clearTimeout(timeout); detachAbort()
      if (generation === entry.generation) {
        entry.state.loading = false; entry.controller = undefined
        const status = entry.state.error?.match(/HTTP (\d+)/)?.[1]
        entry.due = status === '401' || status === '403' ? Infinity : Date.now() + Math.min(entry.metric.refreshMs * 2 ** entry.failures, 300000)
        entry.state.stale = Boolean(entry.state.result && (entry.state.result.quality === 'stale' || Date.now() - Date.parse(entry.state.result.dataAsOf) >= entry.metric.staleAfterMs))
        this.publish(entry)
      }
    }
  }
}
