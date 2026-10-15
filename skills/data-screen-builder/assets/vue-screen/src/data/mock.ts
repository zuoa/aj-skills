import type { Catalog, Provider } from '../contracts/types'
import { assertQuery } from '../contracts/validate.mjs'
import { fixtureResult } from './fixtures.mjs'

export function createMockProvider(catalog: Catalog): Provider {
  return {
    async query(query, signal) {
      signal.throwIfAborted()
      const metric = catalog.metrics.find(m => m.id === query.metricId)!
      assertQuery(metric, query)
      return fixtureResult(metric, query)
    },
  }
}
