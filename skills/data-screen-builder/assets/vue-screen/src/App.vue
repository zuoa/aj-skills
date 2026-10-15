<script setup lang="ts">
import { computed, defineAsyncComponent, onBeforeUnmount, ref, watch } from 'vue'
import catalogJson from './config/metrics.json'
import screenJson from './config/screen.json'
import designsJson from './config/designs.json'
import frameworkJson from './config/framework.json'
import layoutsJson from './config/layouts.json'
import palettesJson from './config/palettes.json'
import stylesJson from './config/styles.json'
import { bindFramework, resolveFramework, resolveStyle, type Framework, type FrameLayout, type FramePalette, type FrameStyle, type EffectIntensity, type Library } from './display/framework.mjs'
import type { Catalog, Screen, Cell } from './contracts/types'
import { assertConfig } from './contracts/validate.mjs'
import { QueryClient } from './data/client'
import { LocalReports } from './data/local-reports'
import { createMockProvider } from './data/mock'
import { createHttpProvider } from './data/http'
import { withContext } from './data/context'
import { areaNames } from './data/fixtures.mjs'
import Panel from './components/Panel.vue'
import ScreenEffects from './components/ScreenEffects.vue'
import ScreenViewport from './components/ScreenViewport.vue'
import TitleFrame from './components/TitleFrame.vue'
import ScreenIcon from './components/ScreenIcon.vue'
import { componentTypes } from './components/registry'
import { applyTheme } from './theme'
import { withDesign, type DesignProfile } from './display/design'
import type { Geography } from './contracts/types'

const props = defineProps<{ showcase?: boolean }>()
const showcase = Boolean(props.showcase && __DATA_PROVIDER__ === 'mock')
const frame = frameworkJson as Framework
const layouts = layoutsJson as Library<FrameLayout>, palettes = palettesJson as Library<FramePalette>
const styles = stylesJson as Library<FrameStyle>
const framework = resolveFramework(frame, layouts, palettes, styles)
const usingFramework = !showcase && Object.keys(frame.bindings).length > 0
const catalog = catalogJson as Catalog
const screen = usingFramework ? bindFramework(screenJson as Screen, frame, layouts, palettes) : screenJson as Screen
assertConfig(catalog, screen, componentTypes())
const isMock = __DATA_PROVIDER__ === 'mock'
const reports = new LocalReports(screen.id, catalog)
const client = new QueryClient(isMock ? createMockProvider(catalog) : createHttpProvider(import.meta.env.VITE_METRICS_ENDPOINT || '/api/metrics/query'), catalog, 8000, reports)
const MetricReport = defineAsyncComponent(() => import('./components/MetricReport.vue'))
const reporting = ref(new URLSearchParams(location.search).get('view') === 'report')
function reportShortcut(event: KeyboardEvent): void {
  if (event.repeat || event.altKey || !(event.ctrlKey || event.metaKey) || !event.shiftKey || event.code !== 'KeyE') return
  event.preventDefault(); reporting.value = true
}
function closeReport(): void {
  reporting.value = false
  const url = new URL(location.href)
  if (url.searchParams.get('view') === 'report') { url.searchParams.delete('view'); history.replaceState(null, '', url) }
}
function reportStorage(event: StorageEvent): void { if (event.key === reports.storageKey || event.key === null) reports.reload() }
window.addEventListener('keydown', reportShortcut)
window.addEventListener('storage', reportStorage)
const area = ref(''), hours = ref(24), paused = ref(false), anchor = ref(Date.now()), now = ref(Date.now())
const mode = ref(screen.mode)
const designs = designsJson.profiles as DesignProfile[]
const designId = ref(designsJson.default)
const design = computed(() => designs.find(d => d.id === designId.value) || designs[0])
const previewParams = new URLSearchParams(window.location.search)
const previewStyle = styles.presets.find(item => item.id === previewParams.get('style'))
const previewPalette = palettes.presets.find(item => item.id === previewParams.get('palette'))
const styleId = ref(showcase ? previewStyle?.id || 'luminous-gallery' : usingFramework ? framework.style.id : 'executive-metal')
const paletteId = ref(showcase ? previewPalette?.id || previewStyle?.recommendedPalettes[0] || 'midnight-cyan' : 'midnight-cyan')
const showcasePalette = computed(() => palettes.presets.find(p => p.id === paletteId.value)!)
const style = computed(() => resolveStyle({ styleId: styleId.value, customStyle: frame.customStyle }, styles))
const conceptScene = computed(() => showcase && ['luminous','hologram','astral','gilded'].includes(style.value.ornament || ''))
const styleChoices = [...styles.presets, ...(frame.customStyle ? [frame.customStyle] : [])]
const visualStyle = computed(() => style.value.effects)
const intensity = ref<EffectIntensity>(usingFramework ? frame.effectIntensity || style.value.defaultIntensity || 'medium' : style.value.defaultIntensity || screen.visuals?.intensity || 'medium')
watch(style, value => { if (!usingFramework) intensity.value = value.defaultIntensity || 'medium' })
const renderer = ref<Geography['renderer']>(design.value.renderer)
watch(design, value => {
  if (!usingFramework) { renderer.value = value.renderer; if (!showcase) styleId.value = value.id === 'analysis' ? 'editorial-light' : value.id === 'ecology' ? 'aurora-ops' : 'executive-metal' }
}, { immediate: true })
watch([design, style, showcasePalette], ([value, appearance, selectedPalette]) => applyTheme({ ...appearance.tokens, ...(showcase ? selectedPalette.tokens : usingFramework ? framework.palette.tokens : value.tokens) }), { immediate: true })
const designedScreen = computed(() => {
  const result = usingFramework ? screen : withDesign(screen, design.value, renderer.value)
  if(conceptScene.value) {
    const names:Record<string,string>={hologram:'区域经营 · 全息展陈',astral:'区域经营 · 星穹展陈',gilded:'区域经营 · 建筑展陈'}
    const map=result.components.find(item=>item.type==='map')
    if(map && names[style.value.ornament || '']) map.title=names[style.value.ornament!]
  }
  assertConfig(catalog, result, componentTypes()); return result
})
const overviewRow = computed(() => style.value.ornament && style.value.ornament !== 'none' ? 144 : 116)
const gridTemplateRows = computed(() => usingFramework
  ? framework.layout.rows === 1 ? 'minmax(0, 1fr)' : `${overviewRow.value}px repeat(${framework.layout.rows - 1}, minmax(0, 1fr))`
  : design.value.gridRows.replace('116px', `${overviewRow.value}px`))
const effectsPaused = ref(false)
const showDisplaySettings = ref(false)
const gridRows = computed(() => Math.max(...designedScreen.value.components.map(binding => binding.layout.row + binding.layout.height - 1)))
const media = window.matchMedia('(prefers-reduced-motion: reduce)')
const reducedSetting = ref(media.matches || screen.mode === 'monitoring')
const systemReduced = ref(media.matches)
const reduced = computed(() => systemReduced.value || reducedSetting.value || mode.value === 'monitoring')
const onMotion = (e: MediaQueryListEvent) => systemReduced.value = e.matches
media.addEventListener('change', onMotion)
const clock = setInterval(() => { now.value = Date.now(); if (!paused.value && now.value - anchor.value >= 60000) anchor.value = now.value }, 1000)
const queries = computed(() => Object.fromEntries(Object.entries(screen.queries).map(([id, query]) => [id, withContext(query, area.value ? { area: area.value } : {}, hours.value, anchor.value)])))
watch(hours, () => anchor.value = Date.now())
function select(filter: string, value: Cell): void { if (filter === 'area') area.value = area.value === value ? '' : String(value ?? '') }
function togglePause(): void { paused.value = !paused.value; client.setPaused(paused.value); if (!paused.value) anchor.value = Date.now() }
function refresh(): void { anchor.value = Date.now() }
async function fullscreen(): Promise<void> { try { if (!document.fullscreenElement) await document.documentElement.requestFullscreen(); else await document.exitFullscreen() } catch { fullscreenError.value = '当前浏览器不支持全屏，请使用浏览器全屏功能' } }
const fullscreenError = ref('')
const clockTime = computed(() => new Intl.DateTimeFormat('zh-CN', { timeZone: 'Asia/Shanghai', timeStyle: 'medium', hourCycle: 'h23' }).format(now.value))
const clockDate = computed(() => new Intl.DateTimeFormat('zh-CN', { timeZone: 'Asia/Shanghai', dateStyle: 'medium' }).format(now.value))
onBeforeUnmount(() => { clearInterval(clock); client.dispose(); media.removeEventListener('change', onMotion); window.removeEventListener('keydown', reportShortcut); window.removeEventListener('storage', reportStorage) })
</script>

<template>
  <ScreenViewport :width="screen.canvas.width" :height="screen.canvas.height" v-slot="{ fitted }">
  <main class="screen" :style="{ '--grid-rows': gridRows }" :data-style="style.id" :data-ornament="style.ornament || 'none'" :data-layout="fitted ? 'canvas' : 'flow'" :class="{ reduced, monitoring: mode === 'monitoring', cinematic: visualStyle === 'cinematic', 'effects-paused': effectsPaused || paused }" :data-intensity="mode === 'monitoring' ? 'low' : intensity" @keydown.esc="showDisplaySettings = false">
    <ScreenEffects v-if="visualStyle === 'cinematic'" :ornament="style.ornament" />
    <header class="masthead">
      <div class="masthead-brand" data-visual-zone="header-brand"><span class="brand-sigil"><ScreenIcon kind="metric" /></span><div><strong>园区 <em>OPERATIONS</em></strong><small>园区运行与经营监测</small></div></div>
      <TitleFrame :ornament="style.ornament" :title="showcase ? '未来园区 · 智能指挥中心' : screen.title" subtitle="PARK OPERATIONS INTELLIGENCE CENTER" />
      <div class="masthead-status" data-visual-zone="header-actions"><div class="live-clock"><time>{{ clockTime }}</time><small>{{ clockDate }} · 上海</small></div><button class="icon-button" @click="fullscreen" aria-label="全屏" title="全屏"><ScreenIcon kind="fullscreen" /></button><button class="icon-button" @click="showDisplaySettings = !showDisplaySettings" :aria-expanded="showDisplaySettings" aria-label="显示设置" title="显示设置"><ScreenIcon kind="settings" /></button></div>
    </header>
    <nav class="toolbar" aria-label="大屏控制">
      <div class="screen-context"><span class="context-dot"></span><strong>园区运营监测</strong><span class="context-slash">/</span><span>{{ area ? areaNames[area as keyof typeof areaNames] : '全域视角' }}</span><span class="source-badge">{{ isMock ? '示例数据' : '业务数据' }}</span><span v-if="paused" class="warning">已暂停</span></div>
      <div class="toolbar-actions">
      <label>区域 <select v-model="area" aria-label="区域"><option value="">全部区域</option><option v-for="(name, id) in areaNames" :key="id" :value="id">{{ name }}</option></select></label>
      <label>时间 <select v-model="hours" aria-label="时间范围"><option :value="24">最近 24 小时</option><option :value="168">最近 7 天</option></select></label>
      <button @click="area = ''" :disabled="!area">重置区域</button>
      <button @click="togglePause">{{ paused ? '恢复更新' : '暂停更新' }}</button><button class="primary-action" @click="refresh" :disabled="paused">立即刷新</button>
      </div>
    </nav>
    <section v-if="showDisplaySettings" class="display-settings" aria-label="显示设置">
      <header><strong>显示设置</strong><button @click="showDisplaySettings = false" aria-label="关闭显示设置">×</button></header>
      <p v-if="usingFramework">当前使用已配置框架：{{ framework.layout.name }} · {{ framework.palette.name }} · {{ style.name }}</p>
      <label v-else-if="!showcase">内容方案 <select v-model="designId" aria-label="内容方案"><option v-for="item in designs" :key="item.id" :value="item.id">{{ item.name }}</option></select></label>
      <label v-if="showcase">配色 <select v-model="paletteId" aria-label="视觉配色"><option v-for="item in palettes.presets" :key="item.id" :value="item.id">{{ item.name }}</option></select></label>
      <label v-if="!usingFramework && !conceptScene">空间视图 <select v-model="renderer" aria-label="空间视图"><option value="three">立体辖区</option><option value="openlayers">二维地图</option><option value="svg">平面边界</option></select></label>
      <label>模式 <select v-model="mode" aria-label="模式"><option value="presentation">业务展示</option><option value="monitoring">值守监控</option></select></label>
      <label v-if="!usingFramework">风格 <select v-model="styleId" aria-label="视觉风格"><option v-for="item in styleChoices" :key="item.id" :value="item.id">{{ item.name }}</option></select></label>
      <button v-if="showcase" @click="paletteId = style.recommendedPalettes[0]">使用推荐配色</button>
      <label v-if="visualStyle === 'cinematic'">光效 <select v-model="intensity" aria-label="光效强度" :disabled="mode === 'monitoring'"><option value="off">关闭</option><option value="low">低</option><option value="medium">中</option><option value="high">高</option></select></label>
      <label class="motion-control"><input v-model="reducedSetting" type="checkbox" :disabled="systemReduced || mode === 'monitoring'" /> 减少动效</label><button v-if="visualStyle === 'cinematic'" @click="effectsPaused = !effectsPaused">{{ effectsPaused ? '恢复光效' : '暂停光效' }}</button>
    </section>
    <p v-if="fullscreenError" class="fullscreen-error error" role="status">{{ fullscreenError }}</p>
    <section class="panel-grid" aria-label="运营指标" :style="fitted ? { gridTemplateRows } : {}">
      <Panel v-for="binding in designedScreen.components" :key="binding.id" :binding="binding" :metric="catalog.metrics.find(m => m.id === screen.queries[binding.queryId].metricId)!" :query="queries[binding.queryId]" :client="client" :reduced="reduced" :paused="paused" :cinematic="visualStyle === 'cinematic'" :now="now" :effects-paused="effectsPaused || intensity === 'off'" :ornament="style.ornament" :concept-scene="conceptScene" @select="select" />
    </section>
    <footer class="screen-footer"><span><i class="context-dot"></i> {{ isMock ? '示例数据 · 辖区边界为虚构演示' : '业务接口 · 以生产指标口径为准' }}</span><span class="footer-mode">{{ mode === 'monitoring' ? '值守监控' : '运营总览' }}</span><span>时区 Asia/Shanghai</span></footer>
  </main>
  </ScreenViewport>
  <MetricReport v-if="reporting" :catalog="catalog" :screen="screen" :queries="queries" :client="client" :reports="reports" @close="closeReport" />
</template>
