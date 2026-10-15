<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, watch } from 'vue'
import * as echarts from 'echarts/core'
import { LineChart, BarChart, PieChart, HeatmapChart, MapChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, VisualMapComponent, DatasetComponent, AriaComponent, GraphicComponent } from 'echarts/components'
import { SVGRenderer } from 'echarts/renderers'
import type { Binding, Cell, Metric, MetricResult } from '../contracts/types'
import { areaNames } from '../data/fixtures.mjs'
import { alpha, categoryColor, theme } from '../theme'

echarts.use([LineChart, BarChart, PieChart, HeatmapChart, MapChart, GridComponent, TooltipComponent, LegendComponent, VisualMapComponent, DatasetComponent, AriaComponent, GraphicComponent, SVGRenderer])
const props = defineProps<{ binding: Binding; metric: Metric; result: MetricResult; reduced: boolean; timezone: string; rich?: boolean }>()
const emit = defineEmits<{ select: [filter: string, value: Cell] }>()
const element = ref<HTMLDivElement>()
const mapError = ref('')
let chart: echarts.ECharts | undefined
let observer: ResizeObserver | undefined
let disposed = false
const display = (value: unknown): string => (areaNames as Record<string, string>)[String(value)] || String(value ?? '—')
const timeLabel = (value: unknown): string => Number.isFinite(Date.parse(String(value))) ? new Intl.DateTimeFormat('zh-CN', { timeZone: props.timezone, month: '2-digit', day: '2-digit', hour: '2-digit', hourCycle: 'h23' }).format(new Date(String(value))) : '—'

function render(): void {
  if (!chart) return
  const { binding: b, result: r } = props
  const { x, y, value, label, series: group } = b.fields
  const axis = { axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: theme.muted, fontSize: theme.captionSize, hideOverlap: true }, splitLine: { lineStyle: { color: alpha(theme.border, .5), type: 'dashed' } } }
  const option: any = {
    animation: !props.reduced, animationDuration: theme.duration, animationDurationUpdate: theme.duration,
    textStyle: { fontFamily: theme.bodyFont, color: theme.text, fontSize: theme.captionSize }, aria: { enabled: true },
    color: theme.categories, tooltip: { trigger: 'item', renderMode: 'richText' },
    grid: { left: 45, right: 18, top: 22, bottom: 32 },
  }
  if (b.type === 'trend') {
    const groups = group ? [...new Set(r.rows.map(row => row[group]))] : ['total']
    option.dataset = groups.map(id => ({ source: group ? r.rows.filter(row => row[group] === id) : r.rows }))
    option.tooltip.trigger = 'axis'
    option.xAxis = { ...axis, type: 'category', axisLabel: { ...axis.axisLabel, margin: 14, formatter: (v: unknown) => r.fields.find(f => f.name === x)?.type === 'timestamp' ? timeLabel(v) : display(v), hideOverlap: true } }
    option.yAxis = { ...axis, type: 'value', splitNumber: 3 }
    if (props.rich) { option.grid = { left: 42, right: 14, top: 8, bottom: 24 }; option.xAxis.axisLabel.margin = 8 }
    option.series = groups.map((id, index) => ({ type: 'line', name: group ? display(id) : props.metric.name, datasetIndex: index, encode: { x, y: value }, showSymbol: false, connectNulls: false, smooth: false, lineStyle: { width: theme.chartLineWidth, shadowBlur: props.rich ? 6 : 0, shadowColor: alpha(theme.accent, .2) }, areaStyle: group || !theme.chartAreaOpacity ? undefined : { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: alpha(theme.accent, theme.chartAreaOpacity) }, { offset: 1, color: alpha(theme.accent, 0) }]) }, itemStyle: { color: group ? categoryColor(String(id)) : theme.accent } }))
    if (group) option.legend = { textStyle: { color: theme.muted } }
  } else if (b.type === 'ranking') {
    option.dataset = { source: r.rows }
    option.grid = { left: 108, right: 65, top: 10, bottom: 22 }
    option.xAxis = { ...axis, type: 'value', splitNumber: 3 }
    option.yAxis = { ...axis, type: 'category', inverse: true, axisLabel: { ...axis.axisLabel, formatter: display, interval: 0 }, splitLine: { show: false } }
    option.series = [{ type: 'bar', encode: { x: value, y: label }, barMaxWidth: theme.chartBarWidth, showBackground: true, backgroundStyle: { color: alpha(theme.border, .4), borderRadius: props.rich ? 4 : 0 }, label: { show: true, position: 'right', color: theme.text, fontFamily: theme.dataFont, fontSize: 12, formatter: (p: any) => Number(p.data[value!]).toLocaleString('zh-CN') }, itemStyle: { borderRadius: props.rich ? [0, 4, 4, 0] : 0, color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [{ offset: 0, color: theme.accent }, { offset: 1, color: theme.good }]) } }]
  } else if (b.type === 'composition') {
    option.dataset = { source: r.rows }
    option.legend = { bottom: 2, itemWidth: 7, itemHeight: 7, itemGap: 10, textStyle: { color: theme.muted, fontSize: 10 } }
    option.series = [{ type: 'pie', radius: ['46%', '60%'], center: ['50%', '42%'], encode: { itemName: label, value }, label: { show: false }, itemStyle: { borderColor: theme.surface, borderWidth: 2, color: (p: any) => categoryColor(String(p.data[label!])) } }]
    option.graphic = [{ type: 'text', left: 'center', top: '22%', style: { text: String(r.rows.length), fontSize: 29, fontFamily: theme.dataFont, fontWeight: 600, fill: theme.text } }, { type: 'text', left: 'center', top: '55%', style: { text: '行业类别', fontSize: 9, fill: theme.muted } }]
    if (props.rich && r.rows.length <= 4 && r.rows.every(row => typeof row[value!] === 'number' && Number(row[value!]) >= 0)) {
      const total = r.rows.reduce((sum, row) => sum + Number(row[value!]), 0)
      option.legend = undefined
      option.series[0].center = ['27%', '48%']
      option.series[0].radius = ['48%', '67%']
      option.series[0].itemStyle.borderRadius = 2
      const chartWidth=chart.getWidth(), chartHeight=chart.getHeight(), cx=chartWidth*.27, cy=chartHeight*.48, rowHeight=chartHeight/r.rows.length
      option.graphic = [
        { type:'text',x:cx,y:cy-4,z:10,style:{text:total.toLocaleString('zh-CN'),fontSize:27,fontFamily:theme.dataFont,fontWeight:500,fill:theme.text,textAlign:'center',textVerticalAlign:'middle'} },
        { type:'text',x:cx,y:cy+18,z:10,style:{text:'分类合计',fontSize:9,fill:theme.muted,textAlign:'center',textVerticalAlign:'middle'} },
        ...r.rows.map((row,index)=>({type:'group',x:chartWidth*.51,y:Math.max(0,(rowHeight-27)/2)+index*rowHeight,z:10,children:[
          {type:'circle',shape:{cx:3,cy:6,r:3},style:{fill:categoryColor(String(row[label!]))}},
          {type:'text',x:15,y:0,style:{text:display(row[label!]),fontSize:10,fill:theme.muted}},
          {type:'text',x:15,y:16,style:{text:`${Number(row[value!]).toLocaleString('zh-CN')} ${props.metric.unit}  ·  ${total ? (Number(row[value!])/total*100).toFixed(1) : '—'}%`,fontFamily:theme.dataFont,fontSize:11,fill:theme.text}},
        ]}))
      ]
    }
  } else if (b.type === 'heatmap') {
    const xs = [...new Set(r.rows.map(row => row[x!]))], ys = [...new Set(r.rows.map(row => row[y!]))]
    option.grid = { left: 32, right: 10, top: 8, bottom: 30 }
    option.xAxis = { ...axis, type: 'category', data: xs, axisLabel: { ...axis.axisLabel, interval: 0 } }
    option.yAxis = { ...axis, type: 'category', data: ys, axisLabel: { ...axis.axisLabel, fontSize: 9, lineHeight: 11, interval: 0 } }
    option.visualMap = { min: 0, max: Math.max(1, ...r.rows.map(row => Number(row[value!] ?? 0))), orient: 'horizontal', top: 0, right: 10, text: ['高', '低'], textStyle: { color: theme.muted, fontSize: 9 }, inRange: { color: theme.sequential }, itemWidth: 4, itemHeight: 56, padding: 0, show: false }
    option.series = [{ type: 'heatmap', data: r.rows.map(row => [xs.indexOf(row[x!]), ys.indexOf(row[y!]), row[value!]]), itemStyle: { borderColor: theme.surface, borderWidth: 2 } }]
  } else if (b.type === 'map') {
    option.visualMap = { min: 0, max: Math.max(1, ...r.rows.map(row => Number(row[value!] ?? 0))), orient: 'horizontal', bottom: 0, left: 'center', textStyle: { color: theme.muted }, inRange: { color: theme.sequential }, itemHeight: 100 }
    option.series = [{ type: 'map', map: 'park', roam: false, top: 10, bottom: 48, left: '20%', right: '20%', label: { show: true, color: theme.text, fontSize: 12, formatter: (p: any) => display(p.name) }, itemStyle: { areaColor: theme.background, borderColor: theme.border, borderWidth: 3 }, emphasis: { label: { color: theme.background }, itemStyle: { areaColor: theme.warning } }, data: r.rows.map(row => ({ name: row[label!], value: row[value!], source: row })) }]
  }
  chart.setOption(option, { notMerge: true })
}
onMounted(async () => {
  if (props.binding.type === 'map' && !echarts.getMap('park')) {
    try {
      const response = await fetch(`${import.meta.env.BASE_URL}park.geo.json`)
      if (!response.ok) throw new Error('底图读取失败')
      const geo = await response.json()
      if (disposed) return
      echarts.registerMap('park', geo)
    } catch { mapError.value = '底图暂不可用，可展开数据表查看'; return }
  }
  if (disposed || !element.value) return
  chart = echarts.init(element.value, undefined, { renderer: 'svg' })
  chart.on('click', (params: any) => {
    const interaction = props.binding.interaction
    const row = params.data?.source || (params.data && !Array.isArray(params.data) ? params.data : props.result.rows[params.dataIndex])
    if (interaction && row?.[interaction.field] !== undefined) emit('select', interaction.filter, row[interaction.field])
  })
  observer = new ResizeObserver(() => { chart?.resize(); if(props.rich) render() })
  observer.observe(element.value)
  render()
})
watch(() => [props.result, props.reduced, props.rich, theme.accent, theme.categories, theme.sequential, theme.text, theme.muted, theme.surface, theme.border, theme.chartLineWidth, theme.chartBarWidth, theme.chartAreaOpacity], render)
onBeforeUnmount(() => { disposed = true; observer?.disconnect(); chart?.dispose() })
</script>

<template>
  <p v-if="mapError" class="empty">{{ mapError }}</p>
  <div v-else ref="element" class="chart" role="img" :aria-label="`${binding.title}，可展开数据表查看完整数据`"></div>
</template>
