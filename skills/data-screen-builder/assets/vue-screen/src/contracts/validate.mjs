import Ajv2020 from 'ajv/dist/2020.js'
import addFormats from 'ajv-formats'
import schema from './contract.schema.json' with { type: 'json' }

const ajv = new Ajv2020({ allErrors: true, strict: true, allowUnionTypes: true })
addFormats(ajv)
ajv.addSchema(schema)
const timestamp = ajv.compile({ type: 'string', format: 'date-time' })
export function assertShape(kind, value) {
  const check = ajv.getSchema(`${schema.$id}#/$defs/${kind}`)
  if (!check || !check(value)) throw new Error(`${kind}: ${ajv.errorsText(check?.errors)}`)
}
function ensure(condition, message) { if (!condition) throw new Error(message) }
function unique(values, context) { ensure(new Set(values).size === values.length, `${context}: duplicate name`) }
function validCell(value, type) {
  return value === null || (type === 'timestamp'
    ? timestamp(value)
    : typeof value === type && (type !== 'number' || Number.isFinite(value)))
}
export function resultFields(metric, query) {
  return [...query.dimensions.map(name => metric.dimensions.find(f => f.name === name)),
    ...(query.granularity === 'none' ? [] : [{ name: 'time', type: 'timestamp' }]), { name: 'value', type: 'number' }]
}
export function assertQuery(metric, query) {
  assertShape('query', query)
  ensure(metric?.id === query.metricId, `unknown metric: ${query.metricId}`)
  ensure(metric.granularities.includes(query.granularity), `${metric.id}: unsupported granularity`)
  ensure(Date.parse(query.timeRange.from) < Date.parse(query.timeRange.to), 'timeRange: from must precede to')
  try { new Intl.DateTimeFormat('en', { timeZone: query.timeRange.timezone }) } catch { throw new Error('invalid IANA timezone') }
  for (const name of [...query.dimensions, ...Object.keys(query.filters)]) {
    ensure(metric.dimensions.some(f => f.name === name), `${metric.id}: unsupported dimension ${name}`)
  }
  for (const [name, value] of Object.entries(query.filters)) {
    const type = metric.dimensions.find(f => f.name === name).type
    ensure((Array.isArray(value) ? value : [value]).every(v => validCell(v, type)), `filter ${name}: invalid ${type}`)
  }
  if (query.orderBy) ensure(resultFields(metric, query).some(f => f.name === query.orderBy.field), 'unknown orderBy field')
}
export function assertResult(metric, query, result) {
  assertQuery(metric, query)
  assertShape('result', result)
  ensure(result.metricId === query.metricId, 'result metricId mismatch')
  unique(result.fields.map(f => f.name), 'result fields')
  const expected = resultFields(metric, query)
  ensure(result.fields.length === expected.length && expected.every(f => result.fields.some(r => r.name === f.name && r.type === f.type)), 'result fields mismatch')
  for (const row of result.rows) {
    ensure(Object.keys(row).length === expected.length && expected.every(f => Object.hasOwn(row, f.name) && validCell(row[f.name], f.type)), 'result row fields or types mismatch')
  }
  ensure(Date.parse(result.dataAsOf) <= Date.parse(result.fetchedAt), 'dataAsOf cannot exceed fetchedAt')
}
export function assertConfig(catalog, screen, componentTypes) {
  assertShape('catalog', catalog)
  assertShape('screen', screen)
  unique(catalog.metrics.map(m => m.id), 'metrics')
  unique(screen.components.map(c => c.id), 'components')
  for (const metric of catalog.metrics) {
    unique(metric.dimensions.map(f => f.name), `${metric.id} dimensions`)
    ensure(!metric.dimensions.some(f => ['value', 'time'].includes(f.name)), `${metric.id}: reserved dimension name`)
    ensure(metric.staleAfterMs >= metric.refreshMs, `${metric.id}: staleAfterMs must be >= refreshMs`)
  }
  for (const query of Object.values(screen.queries)) assertQuery(catalog.metrics.find(m => m.id === query.metricId), query)
  const required = { metric: ['value'], trend: ['x', 'value'], ranking: ['label', 'value'], composition: ['label', 'value'], heatmap: ['x', 'y', 'value'], map: ['label', 'value'], status: ['value'], alerts: ['label'], table: [] }
  for (const binding of screen.components) {
    const query = screen.queries[binding.queryId]
    ensure(query, `${binding.id}: unknown queryId`)
    const metric = catalog.metrics.find(m => m.id === query.metricId)
    const fields = resultFields(metric, query)
    const names = fields.map(f => f.name)
    ensure(componentTypes.includes(binding.type), `${binding.id}: unregistered component ${binding.type}`)
    for (const role of required[binding.type] || []) ensure(binding.fields[role], `${binding.id}: missing ${role} binding`)
    for (const [role, name] of Object.entries(binding.fields)) {
      ensure(names.includes(name), `${binding.id}: unknown field ${name}`)
      if (['value', 'longitude', 'latitude'].includes(role)) ensure(fields.find(f => f.name === name).type === 'number', `${binding.id}: ${role} requires number`)
    }
    if (binding.interaction) {
      ensure(names.includes(binding.interaction.field), `${binding.id}: unknown interaction field`)
      for (const target of Object.values(screen.queries)) {
        const targetMetric = catalog.metrics.find(m => m.id === target.metricId)
        ensure(targetMetric.dimensions.some(f => f.name === binding.interaction.filter), `${binding.id}: interaction filter unsupported by ${target.metricId}`)
      }
    }
    if (binding.thresholds) ensure(binding.thresholds.direction === 'above' ? binding.thresholds.warning <= binding.thresholds.critical : binding.thresholds.warning >= binding.thresholds.critical, `${binding.id}: invalid threshold order`)
    if (binding.geography) {
      ensure(binding.type === 'map', `${binding.id}: geography requires map component`)
      const geo = binding.geography
      ensure(!geo.basemap || geo.basemap.coordinateSystem === geo.coordinateSystem, `${binding.id}: basemap coordinate system mismatch`)
      ensure((geo.overlays || []).every(l => l.coordinateSystem === geo.coordinateSystem), `${binding.id}: overlay coordinate system mismatch`)
    }
    ensure(binding.layout.col + binding.layout.width <= 13, `${binding.id}: layout exceeds 12 columns`)
  }
  for (let i = 0; i < screen.components.length; i++) for (let j = i + 1; j < screen.components.length; j++) {
    const a = screen.components[i].layout, b = screen.components[j].layout
    ensure(!(a.col < b.col + b.width && b.col < a.col + a.width && a.row < b.row + b.height && b.row < a.row + a.height), `overlapping layout: ${screen.components[i].id}, ${screen.components[j].id}`)
  }
}
