<script setup lang="ts">
import { computed, useId } from 'vue'
import type { Binding, Cell, Metric, MetricResult } from '../contracts/types'
import { areaNames } from '../data/fixtures.mjs'

const props = defineProps<{ binding: Binding; metric: Metric; result: MetricResult }>()
const emit = defineEmits<{ select: [filter: string, value: Cell] }>()
const uid = `campus-${useId().replace(/[^a-zA-Z0-9_-]/g, '')}`
const iso = (x: number, y: number, z = 0) => [450 + (x - y) * 12.5, 120 + (x + y) * 6.2 - z]
const polygon = (coordinates: number[][]) => coordinates.map(p => iso(p[0], p[1], p[2] || 0).join(',')).join(' ')
// Purpose-built fictional architecture; heights are decorative, never business values.
const blocks = [
  [3,3,3,4,62],[8,3,4,5,100],[3,9,5,3,38],
  [17,3,4,4,68],[23,3,3,5,86],[18,9,7,3,37],
  [3,18,4,4,52],[3,24,6,3,29],[9,19,3,7,65],
  [17,17,5,5,84],[24,18,3,4,49],[18,24,7,3,34],
].sort((a,b) => a[0]+a[1]-b[0]-b[1]).map(([x,y,w,d,h], index) => ({
  index, h, roof: polygon([[x,y,h],[x+w,y,h],[x+w,y+d,h],[x,y+d,h]]),
  roofInset: polygon([[x+.3,y+.3,h+.5],[x+w-.3,y+.3,h+.5],[x+w-.3,y+d-.3,h+.5],[x+.3,y+d-.3,h+.5]]),
  front: polygon([[x,y+d,h],[x+w,y+d,h],[x+w,y+d,0],[x,y+d,0]]),
  side: polygon([[x+w,y,h],[x+w,y+d,h],[x+w,y+d,0],[x+w,y,0]]),
  plinth: polygon([[x-.3,y-.3],[x+w+.3,y-.3],[x+w+.3,y+d+.3],[x-.3,y+d+.3]]),
  crown: polygon([[x+.5,y+.5,h+5],[x+w-.5,y+.5,h+5],[x+w-.5,y+d-.5,h+5],[x+.5,y+d-.5,h+5]]),
  windows: Array.from({length:Math.floor(h/11)*6},(_,i) => {
    const c=i%6, r=Math.floor(i/6), xx=x+.3+c*(w-.6)/6, z=7+r*11
    return { points:polygon([[xx,y+d,z],[xx+(w-.6)/10,y+d,z],[xx+(w-.6)/10,y+d,z+4],[xx,y+d,z+4]]), warm:(i+index*7)%19===0 }
  }),
  mullions: Array.from({length:Math.floor(h/11)},(_,i)=>polygon([[x+w,y,7+i*11],[x+w,y+d,7+i*11]])),
}))
const landscaping = [[2,2,11,11],[16,2,11,11],[2,16,11,12],[16,16,12,12]]
const trees = Array.from({length:28},(_,i)=>({point:iso(i<14?1:28,1+(i%14)*2),size:3+i%3}))
const paths = [polygon([[0,14],[29,14]]),polygon([[14,0],[14,29]]),polygon([[0,0],[29,0],[29,29],[0,29],[0,0]])]
const anchors = { north:[218,130], east:[672,150], south:[208,342], west:[676,360] } as Record<string,number[]>
const zones = computed(() => props.result.rows.flatMap(row => {
  const id=String(row[props.binding.fields.label!]), anchor=anchors[id]
  return anchor ? [{id,x:anchor[0],y:anchor[1],value:row[props.binding.fields.value!]}] : []
}))
function select(id:string):void { if (props.binding.interaction) emit('select',props.binding.interaction.filter,id) }
</script>

<template>
  <div class="exhibition-scene" aria-label="虚构园区建筑概念示意">
    <div class="campus-atmosphere" aria-hidden="true"></div>
    <svg class="campus-model" viewBox="0 0 900 530" role="img" aria-label="园区空间概念模型，建筑高度不代表指标，示意地理不可作实景依据">
      <defs>
        <linearGradient :id="`${uid}-front`" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="var(--accent)" stop-opacity=".45"/><stop offset="1" stop-color="var(--surface)"/></linearGradient>
        <linearGradient :id="`${uid}-side`" x1="0" y1="0" x2="1" y2="1"><stop stop-color="var(--border)"/><stop offset="1" stop-color="var(--background)"/></linearGradient>
        <linearGradient :id="`${uid}-roof`" x1="0" y1="0" x2="1" y2="1"><stop stop-color="var(--text)" stop-opacity=".88"/><stop offset="1" stop-color="var(--accent)" stop-opacity=".48"/></linearGradient>
        <linearGradient :id="`${uid}-ground`" x1="0" y1="0" x2="0" y2="1"><stop stop-color="var(--surface)"/><stop offset="1" stop-color="var(--border)" stop-opacity=".7"/></linearGradient>
        <radialGradient :id="`${uid}-aura`"><stop stop-color="var(--accent)" stop-opacity=".15"/><stop offset="1" stop-color="var(--accent)" stop-opacity="0"/></radialGradient>
      </defs>
      <ellipse cx="450" cy="364" rx="380" ry="145" :fill="`url(#${uid}-aura)`"/>
      <ellipse cx="450" cy="375" rx="371" ry="119" class="campus-orbit"/>
      <ellipse cx="450" cy="375" rx="390" ry="131" class="campus-orbit orbit-dashed fx"/>
      <polygon :points="polygon([[-1,-1,-11],[30,-1,-11],[30,30,-11],[-1,30,-11]])" fill="var(--background)" stroke="var(--border)" stroke-width="2"/>
      <polygon :points="polygon([[0,0],[29,0],[29,29],[0,29]])" :fill="`url(#${uid}-ground)`" class="campus-ground"/>
      <polygon :points="polygon([[0,0],[29,0],[29,29],[0,29]])" fill="none" class="campus-rim"/>
      <g class="campus-gardens"><polygon v-for="([x,y,w,d],i) in landscaping" :key="i" :points="polygon([[x,y],[x+w,y],[x+w,y+d],[x,y+d]])"/><polygon :points="polygon([[10,0],[12,0],[12,12],[10,12]])"/></g>
      <g class="campus-road"><polyline v-for="(path,i) in paths" :key="i" :points="path"/></g>
      <g class="campus-route fx"><polyline v-for="(path,i) in paths.slice(0,2)" :key="i" :points="path" pathLength="1000"/></g>
      <g v-for="b in blocks" :key="b.index" class="campus-building">
        <polygon :points="b.plinth" fill="var(--accent)" fill-opacity=".14"/>
        <polygon :points="b.front" :fill="`url(#${uid}-front)`"/>
        <polygon :points="b.side" :fill="`url(#${uid}-side)`"/>
        <polygon :points="b.roof" :fill="`url(#${uid}-roof)`"/>
        <polygon :points="b.roofInset" fill="var(--surface)" fill-opacity=".68" stroke="var(--accent)" stroke-opacity=".4" stroke-width=".6"/>
        <polygon :points="b.crown" fill="none" stroke="var(--text)" stroke-width=".6" stroke-opacity=".45"/>
        <polygon v-for="(window,i) in b.windows" :key="i" :points="window.points" :class="window.warm ? 'window-warm' : 'window-cool'" stroke="none"/>
        <polyline v-for="(m,i) in b.mullions" :key="`m${i}`" :points="m" stroke="var(--accent)" stroke-opacity=".22" stroke-width=".5" fill="none"/>
      </g>
      <g v-for="(tree,i) in trees" :key="i" :transform="`translate(${tree.point[0]},${tree.point[1]})`" class="campus-tree"><ellipse cy="4" :rx="tree.size+2" ry="2"/><path d="M0 0V5"/><ellipse cy="-2" :rx="tree.size" :ry="tree.size+1"/></g>
      <g v-for="zone in zones" :key="zone.id" :transform="`translate(${zone.x},${zone.y})`" class="campus-zone" role="button" tabindex="0" :aria-label="`选择${areaNames[zone.id as keyof typeof areaNames]}`" @click="select(zone.id)" @keydown.enter="select(zone.id)" @keydown.space.prevent="select(zone.id)">
        <path d="M0 33V49" class="campus-leader"/><circle cy="49" r="3" class="campus-anchor"/>
        <rect x="-72" y="-8" width="144" height="44" rx="5" class="campus-tag"/>
        <rect x="-70" y="-6" width="3" height="38" rx="1" fill="var(--accent)"/>
        <text x="-58" y="8" class="campus-zone-name">{{ areaNames[zone.id as keyof typeof areaNames] }}</text>
        <text x="-58" y="26" class="campus-zone-value">{{ typeof zone.value==='number' ? zone.value.toLocaleString('zh-CN') : '—' }} <tspan class="campus-zone-unit">{{ metric.unit }}</tspan></text>
      </g>
    </svg>
    <p class="campus-note">空间概念示意 · 非实景模型 <span>选择区域联动数据</span></p>
    <div class="campus-scope"><span>当前数据覆盖</span><strong>{{ zones.length }} 个区域</strong></div>
  </div>
</template>
