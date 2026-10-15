<script setup lang="ts">
import { computed } from 'vue'
import type { Binding, Metric, MetricResult } from '../contracts/types'
const props=defineProps<{ binding:Binding;metric:Metric;result:MetricResult }>()
// Descriptive summaries use only observed numeric values, never invented growth/targets.
const summary=computed(()=>{
  if(props.binding.type!=='trend' || props.binding.fields.series) return null
  const values=props.result.rows.map(row=>row[props.binding.fields.value!]).filter((v):v is number=>typeof v==='number' && Number.isFinite(v))
  const x=props.binding.fields.x!, timestamp=props.result.fields.find(f=>f.name===x)?.type==='timestamp'
  const last=timestamp ? props.result.rows.reduce<typeof props.result.rows[number] | undefined>((current,row)=>!current || Date.parse(String(row[x]))>Date.parse(String(current[x])) ? row : current,undefined) : props.result.rows.at(-1)
  return values.length ? {peak:Math.max(...values),latest:last?.[props.binding.fields.value!],count:values.length,label:timestamp ? '最新采样' : '末项数值'} : null
})
const display=(value:unknown)=>typeof value==='number' ? value.toLocaleString('zh-CN',{maximumFractionDigits:props.metric.precision}) : '—'
</script>
<template>
  <div v-if="summary" class="panel-summary"><div><span>{{ summary.label }}</span><strong>{{ display(summary.latest) }} <small>{{ metric.unit }}</small></strong></div><div><span>窗口峰值</span><strong>{{ display(summary.peak) }} <small>{{ metric.unit }}</small></strong></div><div><span>有效采样</span><strong>{{ summary.count }} <small>点</small></strong></div></div>
</template>
