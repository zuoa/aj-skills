<script setup lang="ts">
import { useId } from 'vue'
import type { Ornament } from '../display/framework.mjs'
defineProps<{ kind?: Ornament }>()
const metalId=`dais-${useId().replace(/[^a-zA-Z0-9_-]/g,'')}`
</script>
<template>
  <div v-if="kind && kind !== 'none'" class="scene-halo" :data-scene-halo="kind" aria-hidden="true">
    <div class="scene-aura optical-glow"></div>
    <div class="scene-pedestal"><div class="pedestal-rings fx"><i></i><i></i><i></i></div><div class="pedestal-core"></div></div>
    <div class="scene-ray ray-a fx"></div><div class="scene-ray ray-b fx"></div><div class="scene-ray ray-c fx"></div>
    <svg class="scene-reticle" viewBox="0 0 800 500" preserveAspectRatio="none"><path d="M 50 120 V 70 H 100 M 700 70 H 750 V 120 M 50 380 V 430 H 100 M 700 430 H 750 V 380"/><path d="M 400 30 V 48 M 400 452 V 470 M 20 250 H 38 M 762 250 H 780"/></svg>
    <svg v-if="kind==='mecha'" class="mechanical-dais" viewBox="80 80 640 360" preserveAspectRatio="xMidYMid meet"><defs><linearGradient :id="metalId" x1="0" y1="0" x2="0" y2="1"><stop stop-color="var(--border)"/><stop offset=".6" stop-color="var(--background)"/><stop offset="1" stop-color="var(--accent)" stop-opacity=".2"/></linearGradient></defs><path d="M120 225L230 155H570L680 225V310L570 390H230L120 310Z" :fill="`url(#${metalId})`"/><path d="M120 225L230 155H570L680 225L570 305H230Z M120 225V310L230 390V305 M680 225V310L570 390V305 M230 390H570" class="dais-bevel"/><path d="M148 225L240 168H560L652 225L560 292H240Z" class="dais-inset"/><path d="M120 310L230 390H570L680 310" class="dais-energy optical-glow"/><path v-for="n in 12" :key="n" :d="`M${260+n*20} 325V350`" class="dais-vent"/><path d="M145 225L235 162H330 M470 162H565L655 225 M230 380H310 M490 380H570" pathLength="1000" class="perimeter-stream fx"/></svg>
  </div>
</template>
