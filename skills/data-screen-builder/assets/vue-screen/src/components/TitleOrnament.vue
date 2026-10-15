<script setup lang="ts">
import { useId } from 'vue'
import type { Ornament } from '../display/framework.mjs'
defineProps<{ kind: Ornament }>()
const id = `title-metal-${useId().replace(/[^a-zA-Z0-9_-]/g, '')}`
</script>

<template>
  <svg class="title-art" :data-title-art="kind" viewBox="0 0 1200 150" preserveAspectRatio="none" aria-hidden="true" focusable="false">
    <defs><linearGradient :id="id" x1="0" y1="0" x2="0" y2="1"><stop class="metal-bright" offset="0"/><stop class="metal-dark" offset=".35"/><stop class="metal-mid" offset=".7"/><stop class="metal-bright" offset="1"/></linearGradient></defs>
    <template v-if="kind === 'mecha'">
      <path d="M 0 52 H 180 L 220 15 H 980 L 1020 52 H 1200 V 76 H 1020 L 970 130 H 230 L 180 76 H 0 Z" :fill="`url(#${id})`" class="title-armor"/>
      <path d="M 230 24 H 970 L 1000 54 V 76 L 962 117 H 238 L 200 76 V 54 Z" class="title-inlay"/>
      <path d="M 0 63 H 180 L 232 126 H 968 L 1020 63 H 1200 M 266 135 H 490 l 16 9 H 694 l 16 -9 H 934" class="title-energy optical-glow"/>
      <g v-for="n in 6" :key="n" class="title-fins"><path :d="`M ${35+n*22} 39 l 16 0 l 20 14 h -16 Z M ${1165-n*22} 39 h -16 l -20 14 h 16 Z`"/></g>
      <path d="M 240 126 H 960" pathLength="1000" class="title-stream fx optical-glow"/>
    </template>
    <template v-else-if="kind === 'hologram'">
      <path d="M 60 40 H 210 L 250 12 H 950 L 990 40 H 1140 L 1100 100 H 970 L 935 130 H 265 L 230 100 H 100 Z" class="title-crystal"/>
      <path d="M 90 51 H 220 L 260 22 H 940 L 980 51 H 1110 M 140 110 H 250 L 275 139 H 925 L 950 110 H 1060" class="title-energy optical-glow"/>
      <path d="M 270 34 H 930 M 270 114 H 930 M 300 143 H 900" class="title-thin"/>
      <path d="M 300 139 H 900" pathLength="1000" class="title-stream fx optical-glow"/>
      <g v-for="x in [225,975]" :key="x" :transform="`translate(${x},75)`" class="title-crystal-gem optical-glow"><path d="M -18 0 L 0 -25 L 18 0 L 0 25 Z"/><path d="M -7 0 L 0 -11 L 7 0 L 0 11 Z"/></g>
    </template>
    <template v-else-if="kind === 'astral'">
      <ellipse cx="600" cy="76" rx="580" ry="55" class="title-orbit"/>
      <ellipse cx="600" cy="76" rx="460" ry="66" class="title-orbit title-orbit-outer"/>
      <path d="M 180 69 Q 600 -33 1020 69 M 180 83 Q 600 185 1020 83" class="title-energy optical-glow"/>
      <path d="M 45 76 H 170 M 1030 76 H 1155 M 600 4 V 17 M 600 135 V 148" class="title-thin"/>
      <g v-for="x in [180,1020]" :key="x" :transform="`translate(${x},76)`" class="optical-glow"><circle r="9" class="ornament-gem"/><circle r="17" class="title-thin"/></g>
      <path d="M 180 83 Q 600 185 1020 83" pathLength="1000" class="title-stream fx optical-glow"/>
    </template>
    <template v-else-if="kind === 'luminous'">
      <path d="M 70 107 Q 230 127 370 135 H 830 Q 970 127 1130 107" class="luminous-title-shadow"/>
      <path d="M 90 87 Q 310 117 470 115 H 730 Q 890 117 1110 87 L 1050 116 Q 885 145 730 142 H 470 Q 315 145 150 116 Z" class="luminous-title-glass"/>
      <path d="M 50 101 Q 285 149 465 135 H 735 Q 915 149 1150 101" class="title-energy optical-glow"/>
      <path d="M 310 21 Q 600 -8 890 21 M 340 14 Q 600 -6 860 14" class="luminous-title-crown"/>
      <path d="M 200 127 Q 440 146 600 138 Q 760 146 1000 127" pathLength="1000" class="title-stream fx optical-glow"/>
      <path d="M 64 92 L 78 99 L 64 106 L 50 99 Z M 1136 92 L 1150 99 L 1136 106 L 1122 99 Z" class="luminous-title-jewel"/>
    </template>
    <template v-else-if="kind === 'gilded'">
      <path d="M 70 55 H 170 Q 210 55 240 23 H 530 L 600 6 L 670 23 H 960 Q 990 55 1030 55 H 1130 V 95 H 1030 Q 990 95 960 127 H 670 L 600 144 L 530 127 H 240 Q 210 95 170 95 H 70 Z" :fill="`url(#${id})`" class="title-armor"/>
      <path d="M 250 32 H 525 L 600 15 L 675 32 H 950 Q 965 75 950 118 H 675 L 600 135 L 525 118 H 250 Q 235 75 250 32 Z" class="title-inlay"/>
      <g v-for="side in [1,-1]" :key="side" :transform="side===1 ? '' : 'translate(1200,0) scale(-1,1)'" class="title-filigree"><path d="M 80 75 H 220 M 120 58 Q 155 15 205 40 Q 240 60 220 75 Q 193 89 188 63 Q 195 48 211 56 M 120 92 Q 155 135 205 110 Q 240 90 220 75 M 30 75 L 48 60 L 66 75 L 48 90 Z"/><path d="M 255 20 H 520 M 255 130 H 520"/></g>
      <path d="M 255 127 H 530 L 600 144 L 670 127 H 945" pathLength="1000" class="title-stream fx optical-glow"/>
    </template>
  </svg>
</template>
