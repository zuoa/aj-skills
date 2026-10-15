<script setup lang="ts">
import type { Ornament } from '../display/framework.mjs'
defineProps<{ ornament?: Ornament }>()
// Deterministic coordinates keep decorative particles stable through data refreshes.
const particles = Array.from({ length: 36 }, (_, i) => ({ x: (i * 47 + 13) % 100, y: (i * 31 + 7) % 100, size: i % 5 === 0 ? 3 : 1.5, delay: -(i % 11), duration: 8 + i % 7 }))
</script>
<template>
  <div class="screen-effects fx" aria-hidden="true">
    <div class="ambient-halo halo-left"></div><div class="ambient-halo halo-right"></div>
    <div class="light-shaft shaft-left"></div><div class="light-shaft shaft-right"></div>
    <div class="perspective-grid"></div><div class="star-field"></div>
    <template v-if="ornament && ornament !== 'none'">
      <div class="nebula-cloud cloud-a"></div><div class="nebula-cloud cloud-b"></div>
      <div class="horizon-flare"></div><div class="showcase-floor"></div>
      <div class="celestial-dome"><i></i><i></i><i></i></div>
      <div class="showcase-particles"><i v-for="(p,i) in particles" :key="i" :style="{ left: `${p.x}%`, top: `${p.y}%`, width: `${p.size}px`, height: `${p.size}px`, animationDelay: `${p.delay}s`, animationDuration: `${p.duration}s` }"></i></div>
      <svg class="screen-chassis" viewBox="0 0 1920 1080" preserveAspectRatio="none"><path class="chassis-shadow" d="M 20 100 V 30 L 40 10 H 420 M 1500 10 H 1880 L 1900 30 V 100 M 20 980 V 1044 L 44 1068 H 680 M 1240 1068 H 1876 L 1900 1044 V 980"/><path class="chassis-light optical-glow" d="M 8 150 V 36 L 36 8 H 330 M 1590 8 H 1884 L 1912 36 V 150 M 8 930 V 1048 L 32 1072 H 520 M 1400 1072 H 1888 L 1912 1048 V 930"/><path class="chassis-ticks" d="M 8 190 V 290 M 14 205 V 250 M 1912 190 V 290 M 1906 205 V 250 M 8 790 V 890 M 1912 790 V 890"/></svg>
    </template>
  </div>
</template>
