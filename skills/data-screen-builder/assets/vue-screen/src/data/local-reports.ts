import type { Catalog, Cell, Field, MetricQuery, MetricResult } from '../contracts/types'
import { assertQuery, assertResult, resultFields } from '../contracts/validate.mjs'
import { reportKey } from './query-key'

type StorageAccess = () => Pick<Storage, 'getItem' | 'setItem'>
interface Report { metric: string; result: MetricResult }
interface Document { version: '1'; reports: Record<string, Report> }
const empty = (): Document => ({ version: '1', reports: {} })

export class LocalReports {
  readonly storageKey: string
  error = ''
  private document = empty()
  private listeners = new Set<() => void>()

  constructor(screenId: string, private catalog: Catalog, private storage: StorageAccess = () => window.localStorage, path = window.location.pathname) {
    this.storageKey = `data-screen:reports:v1:${encodeURIComponent(path)}:${encodeURIComponent(screenId)}`
    this.read()
  }
  private read(): void {
    try {
      const raw = this.storage().getItem(this.storageKey)
      const value = raw === null ? empty() : JSON.parse(raw)
      if (value?.version !== '1' || !value.reports || typeof value.reports !== 'object' || Array.isArray(value.reports)) throw new Error('格式错误')
      this.document = value
      this.error = ''
    } catch {
      this.document = empty()
      this.error = '本地填报缓存无法读取，当前使用原始数据。请检查浏览器存储设置或重新保存。'
    }
  }
  get(query: MetricQuery): MetricResult | undefined {
    const report = this.document.reports[reportKey(query)]
    if (!report) return undefined
    try {
      const metric = this.catalog.metrics.find(m => m.id === query.metricId)!
      if (report.metric !== JSON.stringify(metric)) throw new Error('指标定义已变化')
      assertResult(metric, query, report.result)
      return { ...structuredClone(report.result), fetchedAt: new Date(Math.max(Date.now(), Date.parse(report.result.fetchedAt))).toISOString() }
    } catch {
      this.error = '部分填报与当前指标定义不一致，已使用原始数据；请重新填报。'
      return undefined
    }
  }
  save(query: MetricQuery, result: MetricResult): void {
    const metric = this.catalog.metrics.find(m => m.id === query.metricId)!
    assertResult(metric, query, result)
    this.write(query, { metric: JSON.stringify(metric), result: structuredClone(result) })
  }
  remove(query: MetricQuery): void { this.write(query) }
  private write(query: MetricQuery, report?: Report): void {
    // Merge the latest document so another tab's unrelated reports survive.
    this.read()
    const next = structuredClone(this.document)
    if (report) next.reports[reportKey(query)] = report
    else delete next.reports[reportKey(query)]
    try { this.storage().setItem(this.storageKey, JSON.stringify(next)) }
    catch { throw new Error('保存失败：浏览器存储不可用或空间不足，修改尚未生效。') }
    this.document = next
    this.error = ''
    this.emit()
  }
  subscribe(listener: () => void): () => void { this.listeners.add(listener); return () => this.listeners.delete(listener) }
  reload(): void { this.read(); this.emit() }
  private emit(): void { for (const listener of this.listeners) listener() }
}

export function parseReportCell(value: string, field: Field): Cell {
  if (value === '') return null
  if (field.type === 'string') return value
  if (field.type === 'number') {
    const parsed = value.trim() === '' ? NaN : Number(value)
    if (!Number.isFinite(parsed)) throw new Error(`${field.name} 请输入有效数字；未知值请留空。`)
    return parsed
  }
  if (field.type === 'boolean') {
    if (value !== 'true' && value !== 'false') throw new Error(`${field.name} 请选择是、否或未知。`)
    return value === 'true'
  }
  if (!Number.isFinite(Date.parse(value))) throw new Error(`${field.name} 请输入有效时间。`)
  return new Date(value).toISOString()
}

export function createReport(catalog: Catalog, query: MetricQuery, draft: Record<string, string>[], dataAsOf: string): MetricResult {
  const metric = catalog.metrics.find(m => m.id === query.metricId)!
  assertQuery(metric, query)
  const fields = resultFields(metric, query) as Field[]
  if (fields.length === 1 && draft.length > 1) throw new Error('单值指标最多填写一条记录；分组数据请使用带维度的指标。')
  const result: MetricResult = {
    version: '1', metricId: metric.id, fields,
    rows: draft.map(row => Object.fromEntries(fields.map(field => [field.name, parseReportCell(row[field.name] ?? '', field)]))),
    dataAsOf: Number.isFinite(Date.parse(dataAsOf)) ? new Date(dataAsOf).toISOString() : '',
    fetchedAt: new Date().toISOString(), quality: 'ok',
  }
  if (!result.dataAsOf || Date.parse(result.dataAsOf) > Date.now()) throw new Error('数据截至时间应为有效时间，且不能晚于当前时间。')
  assertResult(metric, query, result)
  return result
}
