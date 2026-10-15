<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'
import { CSS2DRenderer, CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js'
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js'
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js'
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js'
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js'
import type { Binding, Cell, Metric, MetricResult } from '../contracts/types'
import { projectRegions, regionProjector, type Regions, type SpatialLayer, type Position, type Rings } from '../geo/geometry'
import { theme } from '../theme'

const props = defineProps<{ geo: Regions; layers: SpatialLayer[]; binding: Binding; metric: Metric; result: MetricResult; reduced: boolean; paused: boolean }>()
const emit = defineEmits<{ select: [filter: string, value: Cell] }>()
const host = ref<HTMLDivElement>(), error = ref('')
const scene = new THREE.Scene(), camera = new THREE.OrthographicCamera(-100, 100, 60, -60, .1, 1000)
const model = new THREE.Group(), meshes: THREE.Mesh[] = [], labels: { id: string; button: HTMLButtonElement; value: HTMLElement }[] = []
const poiLabels: HTMLElement[] = []
const top = new THREE.MeshStandardMaterial({ color: theme.sceneTop, roughness: theme.sceneRoughness, metalness: theme.sceneMetalness, emissive: theme.sceneGlow, emissiveIntensity: theme.sceneEmission })
const side = new THREE.MeshStandardMaterial({ color: theme.sceneSide, roughness: theme.sceneSideRoughness, metalness: theme.sceneSideMetalness })
const outline = new THREE.LineBasicMaterial({ color: new THREE.Color(theme.sceneEdge).multiplyScalar(2), transparent: true, opacity: .85, toneMapped: false })
const roads = new THREE.LineBasicMaterial({ color: theme.sceneRoad, transparent: true, opacity: .6 })
const water = new THREE.MeshBasicMaterial({ color: theme.sceneWater, side: THREE.DoubleSide })
const poiMaterial = new THREE.MeshBasicMaterial({ color: theme.sceneEdge, toneMapped: false })
let renderer: THREE.WebGLRenderer | undefined, labelRenderer: CSS2DRenderer | undefined, controls: OrbitControls | undefined
let composer: EffectComposer | undefined, bloom: UnrealBloomPass | undefined, observer: ResizeObserver | undefined
let frame = 0, lastFrame = 0, disposed = false, pointerStart: { x: number; y: number } | undefined
const ray = new THREE.Raycaster(), pointer = new THREE.Vector2()
const resources: THREE.BufferGeometry[] = []
function select(id: string): void {
  const interaction = props.binding.interaction, row = props.result.rows.find(r => String(r[props.binding.fields.label!]) === id)
  if (interaction && row) emit('select', interaction.filter, row[interaction.field])
}
function updateValues(): void {
  for (const item of labels) {
    const row = props.result.rows.find(r => String(r[props.binding.fields.label!]) === item.id), value = row?.[props.binding.fields.value!]
    item.value.textContent = typeof value === 'number' ? `${value.toLocaleString('zh-CN', { maximumFractionDigits: props.metric.precision })} ${props.metric.unit}` : '暂无数据'
    item.button.disabled = !row || !props.binding.interaction
  }
  invalidate()
}
function paint(): void {
  if (disposed || !renderer || !labelRenderer) return
  composer?.render(); labelRenderer.render(scene, camera)
  // Hide clipped / overlapping labels after camera movement; the panel's data view stays available.
  const parent = host.value!.getBoundingClientRect(), accepted: DOMRect[] = []
  for (const button of [...labels.map(item => item.button), ...poiLabels]) {
    button.style.visibility = 'visible'
    const box = button.getBoundingClientRect()
    const outside = box.left < parent.left || box.right > parent.right || box.top < parent.top || box.bottom > parent.bottom
    const overlap = accepted.some(r => box.left < r.right + 4 && box.right > r.left - 4 && box.top < r.bottom + 4 && box.bottom > r.top - 4)
    button.style.visibility = outside || overlap ? 'hidden' : 'visible'
    if (!outside && !overlap) accepted.push(box)
  }
}
function loop(time: number): void {
  frame = 0
  if (disposed) return
  if (time - lastFrame > 32) { lastFrame = time; controls?.update(); outline.opacity = .8 + .12 * Math.sin(time / 2800); paint() }
  if (!props.paused && !props.reduced) frame = requestAnimationFrame(loop)
}
function invalidate(): void {
  if (disposed) return
  if (props.paused || props.reduced) { if (frame) cancelAnimationFrame(frame); frame = 0; paint() }
  else if (!frame) frame = requestAnimationFrame(loop)
}
function resize(): void {
  if (!host.value || !renderer) return
  const w = host.value.clientWidth, h = host.value.clientHeight
  if (!w || !h) return
  const aspect = w / h, half = 38 * Math.max(1, 1 / aspect)
  camera.left = -half * aspect; camera.right = half * aspect; camera.top = half; camera.bottom = -half; camera.updateProjectionMatrix()
  renderer.setSize(w, h); composer?.setSize(w, h); labelRenderer?.setSize(w, h); invalidate()
}
function pick(event: PointerEvent): void {
  if (!pointerStart || Math.hypot(event.clientX - pointerStart.x, event.clientY - pointerStart.y) > 5 || !host.value) return
  const box = host.value.getBoundingClientRect()
  // Use the visible rectangle: the whole screen can be CSS-scaled for a wall display.
  pointer.set((event.clientX - box.left) / box.width * 2 - 1, -(event.clientY - box.top) / box.height * 2 + 1)
  ray.setFromCamera(pointer, camera)
  const hit = ray.intersectObjects(meshes)[0]
  if (hit) select(String(hit.object.userData.regionId))
}
function down(event: PointerEvent): void { pointerStart = { x: event.clientX, y: event.clientY } }
function recolor(): void {
  top.color.set(theme.sceneTop); top.emissive.set(theme.sceneGlow); side.color.set(theme.sceneSide)
  top.roughness=theme.sceneRoughness; top.metalness=theme.sceneMetalness; top.emissiveIntensity=theme.sceneEmission
  side.roughness=theme.sceneSideRoughness; side.metalness=theme.sceneSideMetalness
  if(bloom) bloom.strength=theme.sceneBloom
  outline.color.set(theme.sceneEdge).multiplyScalar(2)
  roads.color.set(theme.sceneRoad); water.color.set(theme.sceneWater); poiMaterial.color.set(theme.sceneEdge)
  invalidate()
}
onMounted(() => {
  if (!host.value) return
  try {
    renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, powerPreference: 'high-performance' })
    renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5)); renderer.outputColorSpace = THREE.SRGBColorSpace
    host.value.appendChild(renderer.domElement)
    renderer.domElement.addEventListener('pointerdown', down); renderer.domElement.addEventListener('pointerup', pick)
    labelRenderer = new CSS2DRenderer(); labelRenderer.domElement.className = 'geo-label-layer'; host.value.appendChild(labelRenderer.domElement)
    camera.position.set(22, 108, 135); camera.lookAt(0, 0, 0)
    controls = new OrbitControls(camera, renderer.domElement); controls.enablePan = false; controls.minZoom = .8; controls.maxZoom = 2.2
    controls.minPolarAngle = .25; controls.maxPolarAngle = 1.1; controls.enableDamping = false; controls.addEventListener('change', invalidate)
    scene.add(new THREE.HemisphereLight('#fff6df', '#3b2925', 2.4))
    const sun = new THREE.DirectionalLight('#fff2da', 2.2); sun.position.set(-35, 90, 30); scene.add(sun); scene.add(model)
    const depth = props.binding.geography!.depth
    for (const region of projectRegions(props.geo, props.binding.geography!)) {
      for (const rings of region.polygons) {
        const vectors = rings[0].map(p => new THREE.Vector2(...p)), shape = new THREE.Shape(vectors)
        shape.holes = rings.slice(1).map(ring => new THREE.Path(ring.map(p => new THREE.Vector2(...p))))
        const geometry = new THREE.ExtrudeGeometry(shape, { depth, bevelEnabled: false, steps: 1, curveSegments: 1 })
        geometry.rotateX(-Math.PI / 2); resources.push(geometry)
        const mesh = new THREE.Mesh(geometry, [top, side]); mesh.userData.regionId = region.id; meshes.push(mesh); model.add(mesh)
        const edges = new THREE.EdgesGeometry(geometry, 30); resources.push(edges); model.add(new THREE.LineSegments(edges, outline))
        // Each real boundary ring follows the top surface; no invented road network.
        for (const ring of rings) {
          const line = new THREE.BufferGeometry().setFromPoints(ring.map(([x, y]) => new THREE.Vector3(x, depth + .12, -y))); resources.push(line)
          model.add(new THREE.Line(line, outline))
        }
      }
      const button = document.createElement('button'); button.className = 'geo-label'; button.setAttribute('aria-label', `选择${region.name}`); button.dataset.region = region.id
      const name = document.createElement('strong'), value = document.createElement('span'); name.textContent = region.name; button.append(name, value)
      button.addEventListener('click', e => { e.stopPropagation(); select(region.id) })
      const object = new CSS2DObject(button); object.position.set(region.anchor[0], depth + 7, -region.anchor[1]); model.add(object); labels.push({ id: region.id, button, value })
    }
    const project = regionProjector(props.geo)
    for (const layer of props.layers) for (const feature of layer.data.features) {
      const geometry = feature.geometry
      if (layer.config.kind === 'roads') {
        const lines: Position[][] = geometry.type === 'LineString' ? [geometry.coordinates] : geometry.coordinates
        for (const line of lines) {
          const geo = new THREE.BufferGeometry().setFromPoints(line.map(p => { const [x,y] = project(p); return new THREE.Vector3(x, depth + .22, -y) }))
          resources.push(geo); model.add(new THREE.Line(geo, roads))
        }
      } else if (layer.config.kind === 'water') {
        const polygons: Rings[] = geometry.type === 'Polygon' ? [geometry.coordinates] : geometry.coordinates
        for (const rings of polygons) {
          const shape = new THREE.Shape(rings[0].map(p => new THREE.Vector2(...project(p))))
          shape.holes = rings.slice(1).map(r => new THREE.Path(r.map(p => new THREE.Vector2(...project(p)))))
          const geo = new THREE.ShapeGeometry(shape); geo.rotateX(-Math.PI / 2); resources.push(geo)
          const mesh = new THREE.Mesh(geo, water); mesh.position.y = depth + .08; model.add(mesh)
        }
      } else {
        const [x,y] = project(geometry.coordinates), geometryPoi = new THREE.CylinderGeometry(.5,.5,4,12)
        resources.push(geometryPoi); const marker = new THREE.Mesh(geometryPoi, poiMaterial); marker.position.set(x,depth + 2,-y); model.add(marker)
        const label = document.createElement('div'); label.className = 'geo-poi'
        const name = document.createElement('span'); name.textContent = String(feature.properties[layer.config.nameProperty || 'name'] || '业务点位'); label.appendChild(name)
        const image = layer.config.imageProperty && feature.properties[layer.config.imageProperty]
        if (typeof image === 'string') {
          try {
            const url = new URL(image, document.baseURI)
            if (['http:', 'https:'].includes(url.protocol)) { const photo = document.createElement('img'); photo.src = url.href; photo.alt = name.textContent; photo.addEventListener('error', () => photo.remove()); label.prepend(photo) }
          } catch { /* Retain the name when the optional photo URL is unavailable. */ }
        }
        const object = new CSS2DObject(label); object.position.set(x,depth + 5,-y); model.add(object); poiLabels.push(label)
      }
    }
    composer = new EffectComposer(renderer); composer.addPass(new RenderPass(scene, camera))
    bloom = new UnrealBloomPass(new THREE.Vector2(1, 1), theme.sceneBloom, .4, 1.2); composer.addPass(bloom); composer.addPass(new OutputPass())
    observer = new ResizeObserver(resize); observer.observe(host.value); resize(); updateValues()
  } catch { error.value = '当前设备无法运行三维视图，请在显示设置中选择二维地图'; renderer?.dispose() }
})
watch(() => props.result, updateValues)
watch(() => [props.reduced, props.paused], invalidate)
watch(() => [theme.sceneTop, theme.sceneSide, theme.sceneEdge, theme.sceneGlow, theme.sceneRoad, theme.sceneWater, theme.sceneRoughness, theme.sceneMetalness, theme.sceneSideRoughness, theme.sceneSideMetalness, theme.sceneEmission, theme.sceneBloom], recolor)
onBeforeUnmount(() => {
  disposed = true; cancelAnimationFrame(frame); observer?.disconnect(); controls?.removeEventListener('change', invalidate); controls?.dispose()
  renderer?.domElement.removeEventListener('pointerdown', down); renderer?.domElement.removeEventListener('pointerup', pick)
  for (const geometry of resources) geometry.dispose()
  top.dispose(); side.dispose(); outline.dispose(); roads.dispose(); water.dispose(); poiMaterial.dispose(); bloom?.dispose(); composer?.dispose(); scene.clear(); renderer?.dispose(); renderer?.forceContextLoss()
  host.value?.replaceChildren()
})
</script>
<template>
  <div ref="host" class="three-region" aria-label="三维辖区，可拖动旋转、滚轮缩放及选择区域"></div>
  <p v-if="error" class="geo-message" role="status">{{ error }}</p>
  <span v-else class="geo-hint">拖动旋转 · 滚轮缩放 · 选择区域</span>
</template>
