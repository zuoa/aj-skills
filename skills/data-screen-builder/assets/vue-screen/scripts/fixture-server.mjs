import { createServer } from 'node:http'
import { readFile } from 'node:fs/promises'
import { assertQuery, assertResult } from '../src/contracts/validate.mjs'
import { fixtureResult } from '../src/data/fixtures.mjs'

const catalog = JSON.parse(await readFile(new URL('../src/config/metrics.json', import.meta.url), 'utf8'))
const server = createServer(async (req, res) => {
  res.setHeader('Content-Type', 'application/json; charset=utf-8')
  res.setHeader('Cache-Control', 'no-store')
  if (req.method !== 'POST' || req.url !== '/api/metrics/query') { res.writeHead(404); res.end('{"error":"not found"}'); return }
  try {
    let body = ''
    for await (const chunk of req) { body += chunk; if (body.length > 65536) throw new Error('request too large') }
    const query = JSON.parse(body), metric = catalog.metrics.find(m => m.id === query.metricId)
    assertQuery(metric, query)
    const result = fixtureResult(metric, query)
    assertResult(metric, query, result)
    res.end(JSON.stringify(result))
  } catch { res.writeHead(400); res.end('{"error":"invalid fixture query"}') }
})
server.listen(4175, '127.0.0.1', () => console.log('Test fixture gateway: http://127.0.0.1:4175/api/metrics/query (example data only)'))
for (const signal of ['SIGINT', 'SIGTERM']) process.on(signal, () => server.close())
