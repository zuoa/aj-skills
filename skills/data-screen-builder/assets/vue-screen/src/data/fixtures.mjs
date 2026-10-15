import { resultFields } from '../contracts/validate.mjs'

export const areas = ['north', 'east', 'south', 'west']
export const areaNames = { north: '北部智造区', east: '东部研发区', south: '南部服务区', west: '西部创新区' }
const amounts = [32800, 24600, 18700, 12900]
/** @returns {import('../contracts/types').MetricResult} */
export function fixtureResult(metric, query, now = Date.now()) {
  const selected = query.filters.area
  const indices = areas.map((_, i) => i).filter(i => selected === undefined || (Array.isArray(selected) ? selected.includes(areas[i]) : selected === areas[i]))
  const weight = indices.reduce((sum, i) => sum + [0.36, 0.28, 0.22, 0.14][i], 0)
  let rows = []
  if (metric.id === 'park.enterprises') rows = [{ value: Math.round(368 * weight) }]
  else if (metric.id === 'park.occupancy') rows = [{ value: indices.length ? 86.4 : null }]
  else if (metric.id === 'park.investment') rows = query.dimensions.includes('area') ? indices.map(i => ({ area: areas[i], value: amounts[i] })) : [{ value: indices.reduce((sum, i) => sum + amounts[i], 0) }]
  else if (metric.id === 'energy.consumption') {
    const from = Date.parse(query.timeRange.from), to = Date.parse(query.timeRange.to)
    const step = query.granularity === 'hour' ? 3600000 : 86400000
    for (let time = from, i = 0; time < to && i < 10000; time += step, i++) rows.push({ time: new Date(time).toISOString(), value: i === 6 ? null : Math.round((480 + Math.sin(i / 3) * 110 + (i % 5) * 17) * weight * (step / 3600000)) })
  } else if (metric.id === 'park.industries') rows = ['智能制造', '数字科技', '专业服务', '绿色能源'].map((industry, i) => ({ industry, value: Math.round([142, 108, 76, 42][i] * weight) }))
  else if (metric.id === 'park.activity') {
    for (const weekday of ['一', '二', '三', '四', '五', '六', '日']) for (const hour of Array.from({ length: 24 }, (_, i) => String(i).padStart(2, '0'))) rows.push({ weekday, hour, value: Math.round((18 + (hour === '09' || hour === '18' ? 95 : 35) + weekday.charCodeAt(0) % 31) * weight) })
  } else if (metric.id === 'park.alerts') {
    rows = indices.slice(0, 3).map((i, rank) => ({ area: areas[i], message: ['配电设备温度偏高', '机房空调需要巡检', '停车引导设备离线'][rank], severity: rank === 0 ? '严重' : '关注', eventTime: new Date(now - (rank + 1) * 180000).toISOString(), value: rank + 1 }))
    rows = rows.filter(row => Date.parse(row.eventTime) >= Date.parse(query.timeRange.from) && Date.parse(row.eventTime) < Date.parse(query.timeRange.to))
  } else throw new Error(`No fixture for ${metric.id}; implement production adapter`)
  // Fixtures implement the shipped query shapes only, not a semantic calculation engine.
  if (query.orderBy) {
    const { field, direction } = query.orderBy
    rows.sort((a, b) => (typeof a[field] === 'number' ? a[field] - b[field] : String(a[field]).localeCompare(String(b[field]))) * (direction === 'asc' ? 1 : -1))
  }
  if (query.limit) rows = rows.slice(0, query.limit)
  return { version: '1', metricId: metric.id, fields: resultFields(metric, query), rows, dataAsOf: new Date(now).toISOString(), fetchedAt: new Date(now).toISOString(), quality: 'ok' }
}
