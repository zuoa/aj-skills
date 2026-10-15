<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import frameJson from './config/framework.json'
import layoutsJson from './config/layouts.json'
import palettesJson from './config/palettes.json'
import stylesJson from './config/styles.json'
import { resolveFramework, type Framework, type FrameLayout, type FramePalette, type FrameStyle, type Library } from './display/framework.mjs'
import { applyTheme } from './theme'
import ScreenViewport from './components/ScreenViewport.vue'
import TitleFrame from './components/TitleFrame.vue'
import ScreenEffects from './components/ScreenEffects.vue'
import FrameOrnament from './components/FrameOrnament.vue'

const layouts = layoutsJson as Library<FrameLayout>, palettes = palettesJson as Library<FramePalette>
const styles = stylesJson as Library<FrameStyle>
const frame = ref<Framework>(structuredClone(frameJson) as Framework)
const resolved = computed(() => resolveFramework(frame.value, layouts, palettes, styles))
frame.value.styleId = resolved.value.style.id
watch(resolved, value => applyTheme({ ...value.style.tokens, ...value.palette.tokens }), { immediate: true })
const showOptions = ref(false), notice = ref(''), effectsPaused = ref(false)
const intensity = computed(() => frame.value.effectIntensity || resolved.value.style.defaultIntensity || 'medium')
const layoutChoices = [...layouts.presets, ...(frame.value.customLayout ? [frame.value.customLayout] : [])]
const paletteChoices = [...palettes.presets, ...(frame.value.customPalette ? [frame.value.customPalette] : [])]
const styleChoices = [...styles.presets, ...(frame.value.customStyle ? [frame.value.customStyle] : [])]
function exportCandidate(): void {
  // Candidate selections invalidate content mapping; approval stays in the brief.
  const candidate = { ...frame.value, bindings: {} }
  const url = URL.createObjectURL(new Blob([JSON.stringify(candidate, null, 2) + '\n'], { type: 'application/json' }))
  const link = document.createElement('a')
  link.href = url; link.download = 'framework.candidate.json'; link.click()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
  notice.value = '候选配置已导出，等待确认后应用'
}
</script>

<template>
  <ScreenViewport :width="frame.canvas.width" :height="frame.canvas.height" v-slot="{ fitted }">
    <main class="screen framework-preview" :data-layout="fitted ? 'canvas' : 'flow'" :data-style="resolved.style.id" :data-ornament="resolved.style.ornament || 'none'" :data-intensity="intensity" :class="{ cinematic: resolved.style.effects === 'cinematic', 'effects-paused': effectsPaused }" :data-framework-layout="frame.layoutId" :data-framework-palette="frame.paletteId">
      <ScreenEffects v-if="resolved.style.effects === 'cinematic'" :ornament="resolved.style.ornament" />
      <header class="masthead">
        <div class="frame-stage"><span class="frame-stage-line"></span><strong>框架预览</strong><small>等待结构确认</small></div>
        <TitleFrame :ornament="resolved.style.ornament" :title="frame.title" subtitle="" />
        <div class="masthead-status"><button @click="showOptions = !showOptions" :aria-expanded="showOptions">比较方案</button><button @click="exportCandidate">导出候选配置</button></div>
      </header>
      <nav class="toolbar" aria-label="框架信息"><div class="screen-context"><strong>{{ resolved.layout.name }}</strong><span>/</span><span>{{ resolved.palette.name }}</span><span>/</span><span>{{ resolved.style.name }}</span></div><span class="frame-note">仅展示结构 · 不含业务内容</span></nav>
      <section v-if="showOptions" class="display-settings" aria-label="框架方案">
        <header><strong>比较方案</strong><button @click="showOptions = false" aria-label="关闭方案">×</button></header>
        <label>布局 <select v-model="frame.layoutId" aria-label="框架布局"><option v-for="item in layoutChoices" :key="item.id" :value="item.id">{{ item.name }}</option></select></label>
        <label>配色 <select v-model="frame.paletteId" aria-label="框架配色"><option v-for="item in paletteChoices" :key="item.id" :value="item.id">{{ item.name }}</option></select></label>
        <label>风格 <select v-model="frame.styleId" aria-label="框架风格"><option v-for="item in styleChoices" :key="item.id" :value="item.id">{{ item.name }}</option></select></label>
        <p>{{ resolved.style.description }}</p>
        <label v-if="resolved.style.effects === 'cinematic'">光效 <select :value="intensity" @change="frame.effectIntensity = ($event.target as HTMLSelectElement).value as Framework['effectIntensity']" aria-label="框架光效强度"><option value="off">关闭</option><option value="low">低</option><option value="medium">中</option><option value="high">高</option></select></label>
        <button v-if="resolved.style.effects === 'cinematic'" @click="effectsPaused = !effectsPaused">{{ effectsPaused ? '恢复光效' : '暂停光效' }}</button>
        <p>切换仅供比较，确认结果在对话中记录。自定义方案可直接描述给制作助手。</p>
      </section>
      <section class="panel-grid frame-grid" aria-label="空框架" :style="fitted ? { gridTemplateRows: resolved.layout.rows === 1 ? 'minmax(0, 1fr)' : `${resolved.style.ornament && resolved.style.ornament !== 'none' ? 144 : 116}px repeat(${resolved.layout.rows - 1}, minmax(0, 1fr))` } : {}">
        <article v-for="(slot, index) in resolved.layout.slots" :key="slot.id" class="frame-slot" :class="`frame-slot-${slot.role}`" :data-slot="slot.id" :data-slot-role="slot.role" :style="{ gridColumn: `${slot.layout.col} / span ${slot.layout.width}`, gridRow: `${slot.layout.row} / span ${slot.layout.height}` }">
          <FrameOrnament v-if="resolved.style.ornament && resolved.style.ornament !== 'none'" :kind="resolved.style.ornament" />
          <div class="frame-slot-label"><span class="frame-slot-index">{{ String(index + 1).padStart(2, '0') }}</span><h2>{{ slot.label }}</h2></div>
          <div v-if="slot.role === 'map' || slot.role === 'main'" class="frame-crosshair" aria-hidden="true"><i></i><i></i></div>
          <span class="frame-corner" aria-hidden="true"></span>
        </article>
      </section>
      <footer class="screen-footer"><span>请确认区域比例、阅读顺序、风格、配色与留白</span><span role="status">{{ notice }}</span><span>{{ frame.canvas.width }} × {{ frame.canvas.height }}</span></footer>
    </main>
  </ScreenViewport>
</template>

<style scoped>
.frame-stage { display: grid; grid-template-columns: 2px 1fr; gap: 6px 14px; align-items: center; }
.frame-stage-line { grid-row: span 2; background: var(--accent); height: 36px; }
.frame-stage strong { font-size: 17px; font-weight: 500; letter-spacing: 2px; }
.frame-stage small, .frame-note { font-size: 11px; color: var(--muted); }
.frame-slot { min-width: 0; min-height: 0; position: relative; border: 1px solid var(--border); background: color-mix(in srgb, var(--surface) 80%, var(--background)); overflow: hidden; }
.frame-slot-main, .frame-slot-map { border-color: color-mix(in srgb, var(--accent) 65%, var(--border)); background: repeating-linear-gradient(135deg, transparent, transparent 20px, color-mix(in srgb, var(--accent) 3%, transparent) 20px, color-mix(in srgb, var(--accent) 3%, transparent) 21px), var(--surface); }
.frame-slot-label { position: absolute; left: 20px; top: 17px; display: flex; align-items: center; gap: 13px; }
.frame-slot-index { font: 12px var(--dataFont); color: var(--accent); font-variant-numeric: tabular-nums; }
.frame-slot-label h2 { color: var(--muted); font-size: 13px; font-weight: 400; }
.frame-slot-metric .frame-slot-label { top: 50%; transform: translateY(-50%); }
.frame-corner { position: absolute; right: 10px; bottom: 10px; width: 6px; height: 6px; border-right: 1px solid var(--accent); border-bottom: 1px solid var(--accent); opacity: .5; }
.frame-crosshair { position: absolute; top: 50%; left: 50%; width: 32px; height: 32px; transform: translate(-50%, -50%); opacity: .4; }
.frame-crosshair i { position: absolute; background: var(--accent); }
.frame-crosshair i:first-child { top: 15px; width: 32px; height: 1px; }
.frame-crosshair i:last-child { left: 15px; width: 1px; height: 32px; }
.display-settings p { font-size: 12px; color: var(--muted); line-height: 1.7; }
.framework-preview[data-layout=flow] .frame-slot { grid-column: auto !important; grid-row: auto !important; height: 180px; }
.framework-preview[data-layout=flow] .frame-slot-metric { height: 100px; }
.framework-preview[data-layout=flow] .frame-slot-main, .framework-preview[data-layout=flow] .frame-slot-map { height: 320px; }
.framework-preview[data-layout=flow] .frame-stage { display: none; }
.framework-preview[data-layout=flow] .masthead { min-height: 115px; }
.framework-preview[data-layout=flow] .masthead-status { grid-column: 2; }
.framework-preview[data-layout=flow] .frame-note { font-size: 9px; }
</style>
