import type { MetricQuery, MetricResult, Provider } from '../contracts/types'

export function createHttpProvider(endpoint: string, fetcher: typeof fetch = fetch): Provider {
  if (!endpoint.startsWith('/') || endpoint.startsWith('//') || endpoint.includes('\\')) throw new Error('Use a same-origin metrics gateway path')
  return {
    async query(query: MetricQuery, signal: AbortSignal): Promise<MetricResult> {
      // Adapt existing business routes/fields here, keeping the Provider interface.
      const response = await fetcher(endpoint, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, credentials: 'same-origin',
        body: JSON.stringify(query), signal,
      })
      if (!response.ok) throw new Error(`数据读取失败 · HTTP ${response.status}`)
      return await response.json() as MetricResult
    },
  }
}
