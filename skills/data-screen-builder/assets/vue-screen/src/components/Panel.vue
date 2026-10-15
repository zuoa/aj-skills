<script setup lang="ts">
import { computed, onBeforeUnmount, ref, shallowRef, watch } from 'vue'
import type { Binding, Cell, Metric, MetricQuery } from '../contracts/types'
import type { QueryClient, QueryState } from '../data/client'
import ChartView from './ChartView.vue'
import SceneMap from './SceneMap.vue'
import GeoView from './GeoView.vue'
import ScreenIcon from './ScreenIcon.vue'
import { theme } from '../theme'
import { customComponent } from './registry'
import { areaNames } from '../data/fixtures.mjs'
import { canRetainWindow, isResultStale } from '../data/retention'
import FrameOrnament from './FrameOrnament.vue'
import MetricMedallion from './MetricMedallion.vue'
import PanelSummary from './PanelSummary.vue'
import ExhibitionScene from './ExhibitionScene.vue'
import SpectralScene from './SpectralScene.vue'
import type { Ornament } from '../display/framework.mjs'

const props = defineProps<{ binding: Binding; metric: Metric; query: MetricQuery; client: QueryClient; reduced: boolean; paused: boolean; cinematic: boolean; now: number; effectsPaused?: boolean; ornament?: Ornament; conceptScene?: boolean }>()
const emit = defineEmits<{ select: [filter: string, value: Cell] }>()
const state = shallowRef<QueryState>({ loading: false, stale: false })
let stop: (() => void) | undefined
const retainedWindow = ref(false)
watch(() => props.query, (query, previous) => {
  const retained = canRetainWindow(previous, query) ? state.value.result : undefined
  stop?.()
  stop = props.client.subscribe(query, value => {
    retainedWindow.value = Boolean(!value.result && retained)
    state.value = { ...value, result: value.result || retained }
  })
}, { immediate: true })
onBeforeUnmount(() => stop?.())
const value = computed(() => state.value.result?.rows[0]?.[props.binding.fields.value || 'value'])
const custom = computed(() => customComponent(props.binding.type))
const scalar = computed(() => ['metric', 'status'].includes(props.binding.type))
const rich = computed(() => Boolean(props.ornament && props.ornament !== 'none'))
const stale = computed(() => state.value.stale || isResultStale(state.value.result, props.metric.staleAfterMs, props.now))
const quality = computed(() => state.value.error ? '读取失败' : stale.value ? '数据过期' : state.value.result?.quality === 'partial' ? '数据不完整' : props.paused ? '已暂停' : state.value.loading ? '读取中' : '已更新')
const alarm = computed(() => {
  const t = props.binding.thresholds, v = value.value
  if (!t || typeof v !== 'number') return ''
  const beyond = (threshold: number) => t.direction === 'above' ? v >= threshold : v <= threshold
  return beyond(t.critical) ? '严重' : beyond(t.warning) ? '关注' : '正常'
})
function format(value: Cell | undefined, field = ''): string {
  if (value === null || value === undefined) return '—'
  if (typeof value === 'number') return value.toLocaleString('zh-CN', { maximumFractionDigits: props.metric.precision })
  if (field === 'area') return (areaNames as Record<string, string>)[String(value)] || String(value)
  const type = field === 'dataAsOf' ? 'timestamp' : state.value.result?.fields.find(f => f.name === field)?.type
  if (type === 'timestamp') return new Intl.DateTimeFormat('zh-CN', { timeZone: props.query.timeRange.timezone, month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hourCycle: 'h23' }).format(new Date(String(value)))
  return String(value)
}
const select = (filter: string, value: Cell) => emit('select', filter, value)
</script>

<template>
  <article class="panel" :class="{ 'metric-panel': binding.type === 'metric', degraded: state.error || stale }" :aria-label="binding.title" :data-panel="binding.id"
    :style="{ gridColumn: `${binding.layout.col} / span ${binding.layout.width}`, gridRow: `${binding.layout.row} / span ${binding.layout.height}` }">
    <FrameOrnament v-if="ornament && ornament !== 'none'" :kind="ornament" />
    <header class="panel-header"><h2><ScreenIcon :kind="binding.type" />{{ binding.title }}</h2><span v-if="state.local || state.error || stale || state.loading || state.result?.quality === 'partial' || paused" class="quality" :class="{ warning: state.error || stale || state.result?.quality === 'partial' }">{{ state.local ? '本地填报 · ' : '' }}{{ quality }}</span><span v-else-if="binding.type === 'heatmap'" class="heat-key" aria-label="颜色由低到高">低<i :style="{ background: 'linear-gradient(90deg, ' + theme.sequential.join(',') + ')' }"></i>高</span><span v-else-if="!scalar && binding.fields.value" class="panel-unit">{{ metric.unit }}</span></header>
    <p v-if="state.error" class="error" role="status">{{ state.error }}<template v-if="state.result"> · 保留最后成功数据</template></p>
    <p v-if="retainedWindow" class="error">保留上一时间窗口数据，等待当前窗口更新</p>
    <template v-if="state.result">
      <MetricMedallion v-if="rich && scalar && state.result.rows.length" :value="value" :unit="metric.unit" :kind="ornament" />
      <PanelSummary v-if="rich" :binding="binding" :metric="metric" :result="state.result" />
      <component v-if="custom" :is="custom" :binding="binding" :metric="metric" :result="state.result" :reduced="reduced" @select="select" />
      <p v-else-if="!state.result.rows.length" class="empty">当前筛选暂无数据</p>
      <div v-else-if="binding.type === 'metric' || binding.type === 'status'" class="metric-value">
        <strong>{{ format(value) }}</strong><span>{{ metric.unit }}</span><em v-if="alarm" :class="{ warning: alarm !== '正常' }">{{ alarm }}</em>
      </div>
      <ul v-else-if="binding.type === 'alerts'" class="alerts">
        <li class="alerts-overview"><div><strong class="critical-count">{{ state.result.rows.filter(row => row.severity === '严重').length.toString().padStart(2, '0') }}</strong><small>严重 · 列表内</small></div><div><strong class="warning">{{ state.result.rows.filter(row => row.severity === '关注').length.toString().padStart(2, '0') }}</strong><small>关注 · 列表内</small></div><div><strong>{{ state.result.rows.length.toString().padStart(2, '0') }}</strong><small>当前列表记录</small></div></li>
        <li v-for="(row, index) in state.result.rows" :key="index">
          <span class="severity" :class="{ critical: row.severity === '严重' }">{{ row.severity || '事件' }}</span>
          <div><strong>{{ format(row[binding.fields.label!]) }}</strong><small>{{ format(row.area, 'area') }} · 影响 {{ format(row.value) }} {{ metric.unit }}设备</small></div>
          <time>{{ format(row.eventTime, 'eventTime') }}</time>
        </li>
      </ul>
      <div v-else-if="binding.type === 'table'" class="table-scroll"><table>
        <thead><tr><th v-for="field in state.result.fields" :key="field.name">{{ field.name === 'value' ? `${metric.name}（${metric.unit}）` : field.name === 'area' ? '区域' : field.name }}</th></tr></thead>
        <tbody><tr v-for="(row, index) in state.result.rows" :key="index"><td v-for="field in state.result.fields" :key="field.name">{{ format(row[field.name], field.name) }}</td></tr></tbody>
      </table></div>
      <SpectralScene v-else-if="conceptScene && binding.type === 'map' && (ornament==='hologram' || ornament==='astral')" :kind="ornament" :binding="binding" :metric="metric" :result="state.result" @select="select" />
      <ExhibitionScene v-else-if="conceptScene && binding.type === 'map'" :binding="binding" :metric="metric" :result="state.result" @select="select" />
      <GeoView v-else-if="binding.type === 'map' && binding.geography" :binding="binding" :metric="metric" :result="state.result" :reduced="reduced" :paused="paused || !!effectsPaused" :ornament="ornament" @select="select" />
      <SceneMap v-else-if="cinematic && binding.type === 'map'" :binding="binding" :metric="metric" :result="state.result" @select="select" />
      <ChartView v-else :binding="binding" :metric="metric" :result="state.result" :reduced="reduced" :timezone="query.timeRange.timezone" :rich="rich" @select="select" />
      <p v-if="scalar && binding.caption" class="metric-caption">{{ binding.caption }}</p>
      <div v-if="rich && scalar" class="metric-context"><span class="metric-freshness" :class="{ warning: stale || state.error || paused }"><i></i>{{ quality }}</span><span>截至 {{ format(state.result.dataAsOf, 'dataAsOf') }}</span></div>
      <footer v-if="!scalar" class="panel-footer"><span class="panel-caption">{{ binding.caption || (binding.interaction ? '选择区域可联动查看' : `单位 ${metric.unit}`) }}</span><time>截至 {{ format(state.result.dataAsOf, 'dataAsOf') }}</time></footer>
      <details class="data-details">
        <summary :aria-label="`${binding.title}：查看数据与口径`"><ScreenIcon kind="table" /><span>查看数据与口径</span></summary>
        <p>{{ metric.definition }} · 来源：{{ state.local ? '当前浏览器本地填报' : metric.source }} · 负责人：{{ metric.owner }}</p>
        <p>数据截至：{{ state.result.dataAsOf }} · 获取：{{ state.result.fetchedAt }} · 时区：{{ query.timeRange.timezone }} · 单位：{{ metric.unit }}</p>
        <table><thead><tr><th v-for="field in state.result.fields" :key="field.name">{{ field.name }}</th></tr></thead>
          <tbody><tr v-for="(row, index) in state.result.rows" :key="index"><td v-for="field in state.result.fields" :key="field.name">{{ format(row[field.name], field.name) }}</td></tr></tbody>
        </table>
      </details>
    </template>
    <p v-else class="empty">{{ state.loading ? '正在读取数据…' : '暂无可用数据' }}</p>
  </article>
</template>
