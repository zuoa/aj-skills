<script setup lang="ts">
import { defineAsyncComponent, onBeforeUnmount, ref, shallowRef, watch } from 'vue'
import type { Binding, Cell, Metric, MetricResult } from '../contracts/types'
import { validateRegions, validateLayer, type Regions, type SpatialLayer } from '../geo/geometry'
import SceneHalo from './SceneHalo.vue'
import type { Ornament } from '../display/framework.mjs'
const ThreeRegion = defineAsyncComponent(() => import('./ThreeRegion.vue'))
const OpenLayersMap = defineAsyncComponent(() => import('./OpenLayersMap.vue'))
const GeoSvg = defineAsyncComponent(() => import('./GeoSvg.vue'))
const props = defineProps<{ binding: Binding; metric: Metric; result: MetricResult; reduced: boolean; paused: boolean; ornament?: Ornament }>()
const emit = defineEmits<{ select: [filter: string, value: Cell] }>()
const geo = shallowRef<Regions>(), error = ref(''), loading = ref(false)
const layers = shallowRef<SpatialLayer[]>([]), layerError = ref('')
let controller: AbortController | undefined, revision = 0
async function load(): Promise<void> {
  controller?.abort(); const active = ++revision, config = props.binding.geography!
  controller = new AbortController(); const request = controller
  const timeout = window.setTimeout(() => request.abort(), 20000)
  geo.value = undefined; layers.value = []; layerError.value = ''; error.value = ''; loading.value = true
  try {
    const response = await fetch(new URL(config.source, document.baseURI), { signal: request.signal, credentials: 'same-origin' })
    if (!response.ok) throw new Error(`边界读取失败（${response.status}）`)
    const data = validateRegions(await response.json(), config)
    const loaded = await Promise.allSettled((config.overlays || []).map(async layer => {
      const response = await fetch(new URL(layer.source, document.baseURI), { signal: request.signal, credentials: 'same-origin' })
      if (!response.ok) throw new Error(`${layer.kind} 图层读取失败（${response.status}）`)
      return validateLayer(await response.json(), layer, config.coordinateSystem)
    }))
    if (active === revision) {
      layers.value = loaded.flatMap(r => r.status === 'fulfilled' ? [r.value] : [])
      layerError.value = loaded.some(r => r.status === 'rejected') ? '部分空间图层读取失败，保留已加载边界与图层' : ''
      geo.value = data
    }
  } catch (e) { if (active === revision) error.value = request.signal.aborted ? '边界读取超时，可重试或检查资源路径' : (e instanceof Error ? e.message : '边界读取失败') }
  finally { clearTimeout(timeout); if (active === revision) loading.value = false }
}
watch(() => [props.binding.geography?.source, props.binding.geography?.coordinateSystem, props.binding.geography?.idProperty, props.binding.geography?.nameProperty, props.binding.geography?.basemap, props.binding.geography?.overlays], load, { immediate: true })
onBeforeUnmount(() => { revision++; controller?.abort() })
</script>
<template>
  <div class="geo-stage" :data-renderer="binding.geography!.renderer">
    <SceneHalo v-if="geo && !error" :kind="ornament" />
    <div v-if="error" class="geo-message" role="status"><p>{{ error }}</p><button @click="load">重试边界</button><p>可展开面板数据查看业务指标</p></div>
    <p v-else-if="loading" class="geo-message">正在读取辖区边界…</p>
    <component v-else-if="geo" :is="binding.geography!.renderer === 'three' ? ThreeRegion : binding.geography!.renderer === 'openlayers' ? OpenLayersMap : GeoSvg"
      :key="binding.geography!.renderer" :geo="geo" :layers="layers" :binding="binding" :metric="metric" :result="result" :reduced="reduced" :paused="paused" @select="(filter: string, value: Cell) => emit('select', filter, value)" />
    <span v-if="layerError" class="geo-layer-error" role="status">{{ layerError }}</span>
  </div>
</template>
