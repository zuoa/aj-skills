<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import Map from 'ol/Map.js'
import View from 'ol/View.js'
import GeoJSON from 'ol/format/GeoJSON.js'
import VectorLayer from 'ol/layer/Vector.js'
import TileLayer from 'ol/layer/Tile.js'
import VectorSource from 'ol/source/Vector.js'
import XYZ from 'ol/source/XYZ.js'
import { Fill, Stroke, Style, Text, Circle as CircleStyle } from 'ol/style.js'
import { defaults } from 'ol/control/defaults.js'
import 'ol/ol.css'
import type { Binding, Cell, Metric, MetricResult } from '../contracts/types'
import type { Regions, SpatialLayer } from '../geo/geometry'
import { lonLatProjection } from '../geo/projection'
import { alpha, theme } from '../theme'
const props = defineProps<{ geo: Regions; layers: SpatialLayer[]; binding: Binding; metric: Metric; result: MetricResult }>()
const emit = defineEmits<{ select: [filter: string, value: Cell] }>()
const host = ref<HTMLDivElement>(), tileError = ref(false)
let map: Map | undefined, layer: VectorLayer | undefined, observer: ResizeObserver | undefined
const overlays: VectorLayer[] = []
onMounted(() => {
  if (!host.value) return
  const config = props.binding.geography!
  const dataProjection = lonLatProjection(config.coordinateSystem)
  const features = new GeoJSON().readFeatures(props.geo, { dataProjection, featureProjection: 'EPSG:3857' })
  const source = new VectorSource({ features })
  layer = new VectorLayer({ source, declutter: true, style: feature => {
    const id = String(feature.get(config.idProperty)), row = props.result.rows.find(r => String(r[props.binding.fields.label!]) === id)
    const value = row?.[props.binding.fields.value!]
    return new Style({ fill: new Fill({ color: alpha(theme.accent, row ? .28 : .07) }), stroke: new Stroke({ color: theme.accent, width: 1.6 }), text: new Text({ text: `${feature.get(config.nameProperty)}\n${typeof value === 'number' ? value.toLocaleString('zh-CN') + ' ' + props.metric.unit : '暂无数据'}`, font: '12px sans-serif', overflow: false, fill: new Fill({ color: theme.text }), backgroundFill: new Fill({ color: alpha(theme.surface, .92) }), padding: [7, 9, 7, 9] }) })
  } })
  const tiles = config.basemap ? new XYZ({ url: config.basemap.url, attributions: config.basemap.attribution, crossOrigin: 'anonymous' }) : undefined
  tiles?.on('tileloaderror', () => tileError.value = true)
  for (const item of props.layers) {
    overlays.push(new VectorLayer({ source: new VectorSource({ features: new GeoJSON().readFeatures(item.data, { dataProjection, featureProjection: 'EPSG:3857' }) }), style: feature => new Style({
      stroke: new Stroke({ color: item.config.kind === 'roads' ? theme.sceneRoad : theme.sceneWater, width: 1 }),
      fill: new Fill({ color: theme.sceneWater }),
      image: item.config.kind === 'poi' ? new CircleStyle({ radius: 4, fill: new Fill({ color: theme.accent }), stroke: new Stroke({ color: theme.surface, width: 1 }) }) : undefined,
      text: item.config.kind === 'poi' ? new Text({ text: String(feature.get(item.config.nameProperty || 'name') || '业务点位'), offsetY: -12, font: '11px sans-serif', fill: new Fill({ color: theme.text }), backgroundFill: new Fill({ color: theme.surface }), padding: [3,5,3,5] }) : undefined,
    }), declutter: true }))
  }
  map = new Map({ target: host.value, layers: [...(tiles ? [new TileLayer({ source: tiles })] : []), layer, ...overlays], view: new View({ center: [0, 0], zoom: 1 }), controls: defaults({ rotate: false }) })
  map.on('singleclick', event => {
    const interaction = props.binding.interaction
    const feature = map?.forEachFeatureAtPixel(event.pixel, f => f, { layerFilter: l => l === layer })
    const row = feature && props.result.rows.find(r => String(r[props.binding.fields.label!]) === String(feature.get(config.idProperty)))
    if (interaction && row) emit('select', interaction.filter, row[interaction.field])
  })
  map.on('pointermove', event => { if (host.value) host.value.style.cursor = map?.hasFeatureAtPixel(event.pixel) ? 'pointer' : '' })
  let initialFit = false
  observer = new ResizeObserver(() => { map?.updateSize(); const extent = source.getExtent(); if (!initialFit && host.value?.clientHeight && extent) { map?.getView().fit(extent, { padding: [35, 45, 40, 45], duration: 0, maxZoom: 14 }); initialFit = true } })
  observer.observe(host.value)
})
watch(() => props.result, () => layer?.changed())
watch(() => [theme.accent, theme.surface, theme.text, theme.sceneRoad, theme.sceneWater], () => { layer?.changed(); overlays.forEach(l => l.changed()) })
onBeforeUnmount(() => { observer?.disconnect(); map?.setTarget(undefined); map?.dispose() })
</script>
<template>
  <div ref="host" class="ol-region" aria-label="辖区地图，可拖动、缩放及选择区域"></div>
  <span class="geo-hint">{{ tileError ? '底图读取失败，保留辖区边界' : binding.geography?.basemap ? '选择区域联动' : '辖区边界 · 未配置影像底图' }}</span>
</template>
