import { reactive } from 'vue'

// A project can replace every token. Example profiles are not an industry style rule.
const defaults = {
  scheme: 'dark',
  background: '#071321', surface: '#0d2032', border: '#244358', text: '#d5eaf5', muted: '#83a6bb',
  accent: '#49c6e8', good: '#43d8c1', warning: '#eeb976', critical: '#ec939d',
  categories: ['#49c6e8', '#43d8c1', '#8ca9de', '#d5ad76'],
  sequential: ['#142d40', '#24536d', '#3787a0', '#65c3cb'],
  bodyFont: '"PingFang SC", "Microsoft YaHei", system-ui, sans-serif',
  dataFont: '"DIN Alternate", "Avenir Next", Arial, sans-serif',
  titleFont: '"PingFang SC", "Microsoft YaHei", system-ui, sans-serif',
  titleSize: 34, titleWeight: 600, titleTracking: 5,
  panelHeadingSize: 14, bodySize: 12, captionSize: 10, metricSize: 40,
  panelGap: 18, panelInset: 18, titleGlow: '#49c6e820',
  chartLineWidth: 1.8, chartBarWidth: 7, chartAreaOpacity: .1,
  duration: 320,
  sceneTop: '#9a372b', sceneSide: '#611d19', sceneEdge: '#ffd477', sceneGlow: '#ff752d',
  sceneRoad: '#e8d3a7', sceneWater: '#397080',
  sceneRoughness: .76, sceneMetalness: .12, sceneSideRoughness: .65, sceneSideMetalness: .18,
  sceneEmission: .035, sceneBloom: .55,
}
export type Theme = typeof defaults
export const theme = reactive<Theme>({ ...defaults })
export function alpha(color: string, opacity: number): string {
  return `${color.slice(0, 7)}${Math.round(opacity * 255).toString(16).padStart(2, '0')}`
}
export function applyTheme(tokens: Partial<Theme> = {}): void {
  Object.assign(theme, defaults, tokens)
  for (const [key, value] of Object.entries(theme)) {
    if (typeof value === 'string') document.documentElement.style.setProperty(`--${key}`, value)
    if (typeof value === 'number') document.documentElement.style.setProperty(`--${key}`, String(value))
  }
  document.documentElement.style.colorScheme = theme.scheme
}
export function categoryColor(id: string): string {
  const known: Record<string, string> = { '智能制造': theme.categories[0], '数字科技': theme.categories[1], '专业服务': theme.categories[3], '绿色能源': theme.categories[2] }
  if (known[id]) return known[id]
  let hash = 0
  for (const c of id) hash = (hash * 31 + c.charCodeAt(0)) >>> 0
  return theme.categories[hash % theme.categories.length]
}
