<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, useId } from 'vue'
import type { Ornament } from '../display/framework.mjs'

const props = defineProps<{ kind: Ornament }>()
const element = ref<SVGSVGElement>()
const width = ref(400), height = ref(250)
const uid = useId().replace(/[^a-zA-Z0-9_-]/g, '')
const metal = `frame-metal-${uid}`, glass = `frame-glass-${uid}`
let observer: ResizeObserver | undefined
onMounted(() => {
  observer = new ResizeObserver(([entry]) => {
    width.value = Math.max(80, entry.contentRect.width)
    height.value = Math.max(60, entry.contentRect.height)
  })
  if (element.value) observer.observe(element.value)
})
onBeforeUnmount(() => observer?.disconnect())
const path = computed(() => {
  const w = width.value, h = height.value, c = Math.min(20, h / 5)
  if(props.kind === 'luminous') return `M 18 2 H ${w-18} Q ${w-2} 2 ${w-2} 18 V ${h-18} Q ${w-2} ${h-2} ${w-18} ${h-2} H 18 Q 2 ${h-2} 2 ${h-18} V 18 Q 2 2 18 2 Z`
  if(props.kind === 'astral') return `M 38 2 H ${w-38} Q ${w-2} 2 ${w-2} 36 V ${h-36} Q ${w-2} ${h-2} ${w-38} ${h-2} H 38 Q 2 ${h-2} 2 ${h-36} V 36 Q 2 2 38 2 Z`
  return `M ${c} 2 H ${w - c} L ${w - 2} ${c} V ${h - c} L ${w - c} ${h - 2} H ${c} L 2 ${h - c} V ${c} Z`
})
const inner = computed(() => {
  const w = width.value, h = height.value
  return `M 25 8 H ${w - 25} L ${w - 8} 25 V ${h - 25} L ${w - 25} ${h - 8} H 25 L 8 ${h - 25} V 25 Z`
})
const corner = 'M 0 30 V 12 L 12 0 H 48 M 5 31 V 15 L 15 5 H 40 M 17 13 H 32 M 13 17 V 32'
</script>

<template>
  <svg ref="element" class="frame-art" :data-frame-art="kind" :viewBox="`0 0 ${width} ${height}`" aria-hidden="true" focusable="false">
    <defs>
      <linearGradient :id="metal" x1="0" y1="0" x2="0.8" y2="1"><stop class="metal-bright" offset="0"/><stop class="metal-dark" offset=".22"/><stop class="metal-mid" offset=".5"/><stop class="metal-bright" offset=".74"/><stop class="metal-dark" offset="1"/></linearGradient>
      <linearGradient :id="glass" x1="0" y1="0" x2=".7" y2="1"><stop class="glass-top" offset="0"/><stop class="glass-bottom" offset="1"/></linearGradient>
    </defs>
    <path :d="path" :fill="`url(#${glass})`" class="ornament-shell" />
    <path :d="path" class="ornament-outline optical-glow" />
    <path :d="inner" class="ornament-inner" />
    <template v-if="kind === 'mecha'">
      <path :d="`M 22 1 H ${width * .32} l 12 9 H ${width * .68 - 12} l 12 -9 H ${width - 22} L ${width - 8} 16 H ${width * .7} l -14 8 H ${width * .3 + 14} l -14 -8 H 8 Z`" :fill="`url(#${metal})`" class="armor-plate" />
      <path :d="`M 2 36 H 7 V ${height - 36} H 2 M ${width - 2} 36 H ${width - 7} V ${height - 36} H ${width - 2}`" class="armor-rail optical-glow" />
      <path :d="`M 18 ${height - 2} H ${width * .35} l 8 -6 H ${width * .65 - 8} l 8 6 H ${width - 18}`" class="armor-foot" />
      <g v-for="(x, i) in [22, width - 48]" :key="i" :transform="`translate(${x},${height - 15})`" class="armor-vents"><path v-for="n in 4" :key="n" :d="`M ${n * 5} 0 l -4 5`" /></g>
      <g class="armor-fasteners"><circle v-for="(p,i) in [[14,24],[width-14,24],[14,height-24],[width-14,height-24]]" :key="i" :cx="p[0]" :cy="p[1]" r="2"/></g>
      <path :d="`M 10 25 V ${height-25} M ${width-10} 25 V ${height-25}`" class="armor-engraving"/>
      <path :d="path" pathLength="1000" class="perimeter-stream fx optical-glow" />
    </template>
    <template v-else-if="kind === 'luminous'">
      <path :d="`M 18 3 H ${width*.32} M ${width*.68} 3 H ${width-18} M 3 18 V ${height*.28} M ${width-3} ${height*.72} V ${height-18}`" class="luminous-rim optical-glow"/>
      <path :d="`M 18 ${height-6} H ${width-18} M 10 25 V ${height-25}`" class="luminous-inlay"/>
      <path :d="path" pathLength="1000" class="perimeter-stream fx optical-glow"/>
    </template>
    <template v-else-if="kind === 'hologram'">
      <path :d="`M 2 40 L 12 28 V ${height - 40} l -10 12 Z M ${width - 2} 40 l -10 -12 V ${height - 40} l 10 12 Z`" class="glass-rib optical-glow" />
      <path :d="`M 24 2 H ${width * .4} M ${width * .6} 2 H ${width - 24} M ${width * .25} ${height - 3} H ${width * .75}`" class="hologram-rail optical-glow" />
      <g v-for="(point, i) in [[16,16],[width-16,16],[16,height-16],[width-16,height-16]]" :key="i" :transform="`translate(${point[0]},${point[1]})`"><path d="M -4 0 L 0 -4 L 4 0 L 0 4 Z" class="ornament-gem optical-glow"/></g>
      <path :d="`M 20 8 H ${width-25} L ${width-8} 25 V ${height*.55} M 30 ${height-12} H ${width-30}`" class="crystal-refraction"/>
      <path :d="inner" pathLength="1000" class="perimeter-stream fx optical-glow" />
    </template>
    <template v-else-if="kind === 'astral'">
      <path :d="`M 12 45 Q 12 12 48 12 H ${width * .35} M ${width * .65} 12 H ${width - 48} Q ${width - 12} 12 ${width - 12} 45 M 12 ${height - 45} Q 12 ${height - 12} 48 ${height - 12} H ${width * .35} M ${width * .65} ${height - 12} H ${width - 48} Q ${width - 12} ${height - 12} ${width - 12} ${height - 45}`" class="astral-arc optical-glow" />
      <ellipse :cx="width/2" cy="8" rx="24" ry="5" class="astral-lens optical-glow" />
      <path :d="`M 42 5 Q ${width/2} -1 ${width-42} 5 M 42 ${height-5} Q ${width/2} ${height+1} ${width-42} ${height-5}`" class="astral-optic"/>
      <g v-for="(x,i) in [width*.28,width*.72]" :key="i" :transform="`translate(${x},${height-7})`"><path d="M -12 0 H -4 M 4 0 H 12 M 0 -3 V 3" class="astral-star"/></g>
      <path :d="path" pathLength="1000" class="perimeter-stream fx optical-glow" />
    </template>
    <template v-else-if="kind === 'gilded'">
      <path :d="path" :stroke="`url(#${metal})`" class="gilded-emboss" />
      <path :d="inner" class="gilded-hairline"/>
      <g v-for="(point,i) in [[6,6,1,1],[width-6,6,-1,1],[6,height-6,1,-1],[width-6,height-6,-1,-1]]" :key="i" :transform="`translate(${point[0]},${point[1]}) scale(${point[2]*.48},${point[3]*.48})`" class="gilded-filigree"><path :d="corner"/><path d="M 8 39 Q 16 22 26 22 Q 40 22 38 9 M 16 31 Q 22 30 22 37 Q 18 42 13 36"/><path d="M 5 5 L 11 0 L 17 5 L 11 10 Z" class="ornament-gem"/></g>
      <path :d="`M ${width/2-40} 4 H ${width/2-12} l 12 8 l 12 -8 H ${width/2+40} M ${width/2-50} ${height-4} H ${width/2-12} l 12 -8 l 12 8 H ${width/2+50}`" class="gilded-crest optical-glow" />
      <path :d="path" pathLength="1000" class="perimeter-stream fx optical-glow" />
    </template>
  </svg>
</template>
