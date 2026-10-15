<script setup lang="ts">
import { computed, useId } from 'vue'
import ScreenIcon from './ScreenIcon.vue'
import type { Ornament } from '../display/framework.mjs'
const props=defineProps<{ value: unknown; unit:string; kind?:Ornament }>()
const percent=computed(()=>props.unit==='%' && typeof props.value==='number' && props.value>=0 && props.value<=100 ? props.value : null)
const uid=`medal-${useId().replace(/[^a-zA-Z0-9_-]/g,'')}`
</script>
<template>
  <div class="metric-medallion" :data-medallion="kind || 'luminous'" aria-hidden="true">
    <svg viewBox="0 0 120 120"><defs><radialGradient :id="uid"><stop stop-color="var(--accent)" stop-opacity=".4"/><stop offset="1" stop-color="var(--accent)" stop-opacity="0"/></radialGradient></defs><circle cx="60" cy="60" r="55" :fill="`url(#${uid})`"/>
      <template v-if="kind==='mecha'"><path d="M37 10 H83 L104 32 V76 L83 98 H37 L16 76 V32 Z" class="medallion-armor"/><path d="M39 16 H81 L96 34 V73 L81 89 H39 L24 73 V34 Z" class="medallion-engrave"/><g class="medallion-bolts"><circle v-for="(p,i) in [[26,29],[94,29],[26,79],[94,79]]" :key="i" :cx="p[0]" :cy="p[1]" r="2"/></g></template>
      <template v-else-if="kind==='hologram'"><path d="M60 5 L105 31 V76 L60 101 L15 76 V31 Z" class="medallion-crystal"/><path d="M60 5 V28 M15 31 L31 40 M105 31 L89 40 M60 101 V86" class="medallion-crystal-edge"/><ellipse cx="60" cy="93" rx="45" ry="8" class="medallion-base"/></template>
      <template v-else-if="kind==='astral'"><ellipse cx="60" cy="55" rx="54" ry="17" transform="rotate(-25 60 55)" class="medallion-base"/><ellipse cx="60" cy="55" rx="48" ry="43" class="medallion-constellation"/><path d="M102 29 h8 m-4 -4 v8 M14 76 h8 m-4 -4 v8" class="medallion-traces"/></template>
      <template v-else-if="kind==='gilded'"><path d="M60 4 L69 11 L81 9 L85 20 L96 25 L93 37 L102 46 L97 57 L100 70 L88 76 L83 89 L70 88 L60 99 L50 88 L37 89 L32 76 L20 70 L23 57 L18 46 L27 37 L24 25 L35 20 L39 9 L51 11 Z" class="medallion-seal"/><circle cx="60" cy="52" r="43" class="medallion-engrave"/></template>
      <template v-else><ellipse cx="60" cy="81" rx="42" ry="13" class="medallion-base"/><path v-if="percent===null" d="M29 75 Q60 99 91 75 M27 81 Q60 104 93 81" class="medallion-traces"/></template>
      <circle cx="60" cy="52" r="35" class="medallion-orbit"/><circle v-if="percent !== null" cx="60" cy="52" r="35" class="medallion-value" pathLength="100" :stroke-dasharray="`${percent} ${100-percent}`" transform="rotate(-90,60,52)"/>
    </svg>
    <ScreenIcon :kind="unit==='%' ? 'composition' : 'metric'" />
  </div>
</template>
