<script setup lang="ts">
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import { fitCanvas } from '../display/fit'

const props = withDefaults(defineProps<{ width: number; height: number; reflowBelow?: number }>(), { reflowBelow: 900 })
const root = ref<HTMLDivElement>()
const viewport = ref({ width: window.innerWidth, height: window.innerHeight })
const fitted = computed(() => viewport.value.width >= props.reflowBelow)
const fit = computed(() => fitCanvas(props.width, props.height, Math.max(1, viewport.value.width), Math.max(1, viewport.value.height)))
const canvasStyle = computed(() => fitted.value ? {
  width: `${props.width}px`, height: `${props.height}px`,
  left: `${fit.value.left}px`, top: `${fit.value.top}px`, transform: `scale(${fit.value.scale})`,
} : {})
let observer: ResizeObserver | undefined
onMounted(() => {
  observer = new ResizeObserver(([entry]) => {
    if (entry) viewport.value = { width: entry.contentRect.width, height: entry.contentRect.height }
  })
  if (root.value) observer.observe(root.value)
})
onBeforeUnmount(() => observer?.disconnect())
</script>

<template>
  <div ref="root" class="screen-viewport" :class="{ 'is-flow': !fitted }" :data-display="fitted ? 'fit' : 'flow'">
    <div class="screen-canvas" :style="canvasStyle" :data-scale="fitted ? fit.scale : 1">
      <slot :fitted="fitted" />
    </div>
  </div>
</template>
