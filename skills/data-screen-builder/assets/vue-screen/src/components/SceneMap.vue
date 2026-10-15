<script setup lang="ts">
import { computed } from 'vue'
import type { Binding, Cell, Metric, MetricResult } from '../contracts/types'
import { areaNames } from '../data/fixtures.mjs'
const props = defineProps<{ binding: Binding; metric: Metric; result: MetricResult }>()
const emit = defineEmits<{ select: [filter: string, value: Cell] }>()
const iso = (x: number, y: number, z = 0) => [450 + (x - y) * 12, 135 + (x + y) * 6 - z]
const points = (coords: number[][]) => coords.map(c => iso(c[0], c[1], c[2] || 0).join(',')).join(' ')
const towers = [
  { id: 'north', x: 5, y: 5, w: 6, d: 5, h: 92 },
  { id: 'east', x: 17, y: 5, w: 6, d: 5, h: 75 },
  { id: 'south', x: 5, y: 17, w: 6, d: 5, h: 65 },
  { id: 'west', x: 17, y: 17, w: 6, d: 5, h: 85 },
].map(({id,x,y,w,d,h}) => ({
  id, roof: points([[x,y,h],[x+w,y,h],[x+w,y+d,h],[x,y+d,h]]),
  roofInset: points([[x+.5,y+.5,h+.2],[x+w-.5,y+.5,h+.2],[x+w-.5,y+d-.5,h+.2],[x+.5,y+d-.5,h+.2]]),
  left: points([[x,y+d,h],[x+w,y+d,h],[x+w,y+d,0],[x,y+d,0]]),
  right: points([[x+w,y,h],[x+w,y+d,h],[x+w,y+d,0],[x+w,y,0]]),
  windows: Array.from({length:48},(_,i) => { const u=i%8,v=Math.floor(i/8),wx=x+.4+u*(w-.8)/8,wz=10+v*(h-14)/6; return points([[wx,y+d,wz],[wx+.38,y+d,wz],[wx+.38,y+d,wz+5],[wx,y+d,wz+5]]) }),
  marker: iso(x+w/2,y+d/2,h+10),
}))
const trees = Array.from({length:12},(_,i)=>iso(2+i*2,27))
const zones = computed(() => props.result.rows.map(row => {
  const id=String(row[props.binding.fields.label!]), tower=towers.find(t=>t.id===id)
  return { id, value: row[props.binding.fields.value!], x: tower?.marker[0] || 450, y: tower?.marker[1] || 250 }
}))
function select(id: string): void { if (props.binding.interaction) emit('select', props.binding.interaction.filter, id) }
</script>

<template>
  <div class="scene-map" aria-label="虚构园区示意沙盘">
    <svg class="city-model" viewBox="0 0 900 550" role="img" aria-label="园区建筑和区域的示意空间布局，建筑高度不代表业务指标">
      <defs>
        <linearGradient id="city-roof" x2="1" y2="1"><stop stop-color="var(--sceneTop)"/><stop offset="1" stop-color="var(--sceneTop)"/></linearGradient>
        <linearGradient id="city-wall" x2="0" y2="1"><stop stop-color="var(--sceneTop)"/><stop offset="1" stop-color="var(--sceneTop)"/></linearGradient>
        <linearGradient id="city-beam" x2="0" y2="1"><stop stop-color="var(--accent)" stop-opacity="0"/><stop offset="1" stop-color="var(--accent)" stop-opacity=".32"/></linearGradient>
        <radialGradient id="city-ground"><stop stop-color="var(--sceneTop)" stop-opacity=".7"/><stop offset="1" stop-color="var(--background)" stop-opacity=".4"/></radialGradient>
      </defs>
      <polygon :points="points([[-1,-1,-7],[29,-1,-7],[29,29,-7],[-1,29,-7]])" fill="var(--background)"/>
      <polygon :points="points([[0,0],[28,0],[28,28],[0,28]])" fill="url(#city-ground)" stroke="var(--sceneTop)" stroke-width=".8"/>
      <polygon :points="points([[1,1],[27,1],[27,27],[1,27]])" fill="var(--sceneTop)" stroke="var(--sceneTop)" stroke-width=".6"/>
      <g fill="var(--sceneTop)" stroke="var(--sceneTop)" stroke-width=".5"><polygon :points="points([[1,12],[27,12],[27,14],[1,14]])"/><polygon :points="points([[12,1],[14,1],[14,27],[12,27]])"/></g>
      <g stroke="var(--accent)" stroke-width=".5" stroke-dasharray="3 4" fill="none"><path :d="`M${iso(1,13).join(',')}L${iso(27,13).join(',')}M${iso(13,1).join(',')}L${iso(13,27).join(',')}`"/></g>
      <g v-for="tower in towers" :key="tower.id" stroke="var(--accent)" stroke-width=".7">
        <polygon :points="tower.left" fill="url(#city-wall)"/><polygon :points="tower.right" fill="var(--sceneTop)"/><polygon :points="tower.roof" fill="url(#city-roof)"/>
        <polygon :points="tower.roofInset" fill="var(--sceneTop)" stroke="var(--sceneTop)"/>
        <polygon v-for="(window,index) in tower.windows" :key="index" :points="window" :fill="index%17===0 ? 'var(--warning)' : 'var(--sceneTop)'" stroke="none" :opacity="index%3===0 ? '.8' : '.5'"/>
      </g>
      <g v-for="(tree,index) in trees" :key="index" :transform="`translate(${tree[0]},${tree[1]})`"><path d="M0 -9L-3 -2H-2L-4 2H4L2 -2H3Z" fill="var(--good)"/><path d="M0 2V6" stroke="var(--good)" stroke-width="1"/></g>
      <g class="scene-beams fx" fill="url(#city-beam)" opacity=".25"><path d="M447 173L435 65H465L453 173Z"/></g>
      <g v-for="zone in zones" :key="zone.id" :transform="`translate(${zone.x-52},${zone.y-34})`" class="scene-marker" role="button" tabindex="0" :aria-label="`${areaNames[zone.id as keyof typeof areaNames] || zone.id} ${zone.value} ${metric.unit}`" @click="select(zone.id)" @keydown.enter="select(zone.id)" @keydown.space.prevent="select(zone.id)">
        <rect width="104" height="30" rx="1" fill="var(--background)" stroke="var(--sceneTop)" stroke-width=".6"/>
        <text x="6" y="11" fill="var(--text)" font-size="8">{{ areaNames[zone.id as keyof typeof areaNames] || zone.id }}</text>
        <text x="6" y="23" fill="var(--accent)" font-size="8">{{ typeof zone.value === 'number' ? zone.value.toLocaleString('zh-CN') : '—' }} {{ metric.unit }}</text>
        <path d="M52 30V38" stroke="var(--accent)" stroke-width=".7"/>
      </g>
    </svg>
    <p class="scene-caption">园区布局示意 · 非实景测绘<span>四个区域 · 选择区域联动</span></p>
  </div>
</template>
