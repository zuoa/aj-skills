<script setup lang="ts">
import { computed } from 'vue'
import type { Binding, Cell, Metric, MetricResult } from '../contracts/types'
import { projectRegions, type Regions, type Rings, type SpatialLayer } from '../geo/geometry'
const props = defineProps<{ geo: Regions; layers: SpatialLayer[]; binding: Binding; metric: Metric; result: MetricResult }>()
const emit = defineEmits<{ select: [filter: string, value: Cell] }>()
const regions = computed(() => projectRegions(props.geo, props.binding.geography!))
const path = (polygons: Rings[]) => polygons.map(rings => rings.map(ring => `M${ring.map(p => `${p[0]},${-p[1]}`).join('L')}Z`).join('')).join('')
function select(id: string): void {
  const interaction = props.binding.interaction, row = props.result.rows.find(r => String(r[props.binding.fields.label!]) === id)
  if (interaction && row) emit('select', interaction.filter, row[interaction.field])
}
</script>
<template>
  <svg class="geo-svg" viewBox="-60 -58 120 116" aria-label="辖区边界示意图">
    <g v-for="region in regions" :key="region.id" role="button" tabindex="0" :aria-label="`选择${region.name}`" @click="select(region.id)" @keydown.enter="select(region.id)" @keydown.space.prevent="select(region.id)">
      <path :d="path(region.polygons)" fill-rule="evenodd" fill="var(--sceneTop)" stroke="var(--sceneEdge)" stroke-width=".4" />
      <text :x="region.anchor[0]" :y="-region.anchor[1]" text-anchor="middle" fill="var(--text)" font-size="2.7">{{ region.name }}</text>
    </g>
  </svg>
</template>
