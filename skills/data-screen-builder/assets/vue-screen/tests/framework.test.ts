import { describe, expect, it } from 'vitest'
import frameJson from '../src/config/framework.json'
import layouts from '../src/config/layouts.json'
import palettes from '../src/config/palettes.json'
import styles from '../src/config/styles.json'
import screen from '../src/config/screen.json'
import { assertLayout, resolveFramework, bindFramework, resolveStyle, type Framework, type FrameLayout } from '../src/display/framework.mjs'
import type { Screen } from '../src/contracts/types'

const base = frameJson as Framework
describe('framework selection', () => {
  it('keeps slots and colors independent across all style, layout and palette combinations', () => {
    for (const style of styles.presets) for (const layout of layouts.presets) for (const palette of palettes.presets) {
      const result = resolveFramework({ ...base, styleId: style.id, layoutId: layout.id, paletteId: palette.id }, layouts as any, palettes, styles)
      expect(result.style.id).toBe(style.id)
      expect(result.layout).toEqual(layout)
      expect(result.palette).toEqual(palette)
    }
  })
  it('uses an explicit style ahead of the legacy effect flag and supports older configurations', () => {
    expect(resolveStyle({ styleId: 'story-atlas', visualStyle: 'cinematic' }).id).toBe('story-atlas')
    expect(resolveStyle({ visualStyle: 'cinematic' }).id).toBe('command-hud')
    expect(resolveStyle({}).id).toBe('editorial-light')
    expect(() => resolveStyle({ styleId: 'typo' })).toThrow('unknown style')
  })
  it('accepts complete custom styles and rejects missing or malformed choices', () => {
    const customStyle = { ...styles.presets[0], id: 'custom', name: '品牌自定义' }
    expect(resolveFramework({ ...base, styleId: 'custom', customStyle }, layouts as any, palettes).style.name).toBe('品牌自定义')
    expect(() => resolveStyle({ styleId: 'custom' })).toThrow('unknown style')
    expect(() => resolveStyle({ styleId: 'custom', customStyle: { ...customStyle, effects: 'typo' } as any })).toThrow()
    expect(() => resolveStyle({}, { ...styles, presets: [...styles.presets, styles.presets[0]] })).toThrow('duplicate style')
  })
  it('validates exhibition ornaments and a persisted intensity without changing content geometry', () => {
    const result = resolveFramework({ ...base, styleId: 'hologram-reactor', effectIntensity: 'off' }, layouts as any, palettes)
    expect(result.style.ornament).toBe('hologram')
    expect(result.style.defaultIntensity).toBe('high')
    expect(result.layout.id).toBe(base.layoutId)
    expect(result.palette.id).toBe(base.paletteId)
    expect(() => resolveFramework({ ...base, effectIntensity: 'flash' } as any, layouts as any, palettes)).toThrow()
    expect(() => resolveStyle({ styleId: 'custom', customStyle: { ...styles.presets[0], id: 'custom', ornament: 'typo' } as any })).toThrow()
    expect(() => resolveStyle({ styleId: 'custom', customStyle: { ...styles.presets[0], id: 'custom', defaultIntensity: 'flash' } as any })).toThrow()
  })
  it.each(layouts.presets.map(p => p.id))('can combine %s with every palette without business input', id => {
    for (const palette of palettes.presets) {
      const result = resolveFramework({ ...base, layoutId: id, paletteId: palette.id }, layouts as any, palettes)
      expect(result.layout.id).toBe(id)
      expect(result.palette.id).toBe(palette.id)
    }
  })
  it('accepts custom geometry and a manual palette, without inventing a map', () => {
    const customLayout: FrameLayout = { id: 'custom', name: '双列', description: '左主右辅', aspect: '16:9', rows: 10, slots: [
      { id: 'left', label: '主区', role: 'main', layout: { col: 1, row: 1, width: 7, height: 10 } },
      { id: 'right', label: '辅助区', role: 'list', layout: { col: 8, row: 1, width: 5, height: 10 } },
    ] }
    const frame = { ...base, layoutId: 'custom', paletteId: 'custom', customLayout, customPalette: { ...palettes.presets[0], id: 'custom' } }
    expect(resolveFramework(frame, layouts as any, palettes).layout.slots.some(s => s.role === 'map')).toBe(false)
    expect(() => resolveFramework({ ...frame, customLayout: undefined }, layouts as any, palettes)).toThrow('unknown layout')
  })
  it.each(['overlap', 'overflow', 'fraction', 'duplicate', 'negative'])('rejects invalid geometry: %s', failure => {
    const layout = structuredClone(layouts.presets[0]) as FrameLayout
    if (failure === 'overlap') layout.slots[1].layout.col = 1
    if (failure === 'overflow') layout.slots[0].layout.height = 100
    if (failure === 'fraction') layout.slots[0].layout.width = 1.5
    if (failure === 'duplicate') layout.slots[1].id = layout.slots[0].id
    if (failure === 'negative') layout.slots[0].layout.col = -1
    expect(() => assertLayout(layout)).toThrow()
  })
  it('does not silently fall back from unknown choices or an incomplete manual palette', () => {
    expect(() => resolveFramework({ ...base, layoutId: 'unknown' }, layouts as any, palettes)).toThrow('unknown layout')
    expect(() => resolveFramework({ ...base, paletteId: 'unknown' }, layouts as any, palettes)).toThrow('unknown palette')
    expect(() => resolveFramework({ ...base, paletteId: 'custom', customPalette: { id: 'custom', name: '手动', tokens: { accent: '#123456' } } }, layouts as any, palettes)).toThrow()
  })
})
describe('framework to final page', () => {
  const bindings = { enterprises: 'overview-1', occupancy: 'overview-2', investment: 'overview-3', energy: 'left-top', map: 'map', ranking: 'left-bottom', industries: 'left-middle', activity: 'bottom', alerts: 'right-top', table: 'right-bottom' }
  const frame: Framework = { ...base, layoutId: 'map-center', bindings, title: '确认主题', canvas: { width: 2560, height: 1440 } }
  it('reuses confirmed slots, title and canvas while preserving queries and content', () => {
    const result = bindFramework(screen as Screen, frame, layouts as any, palettes)
    expect(result.title).toBe(frame.title)
    expect(result.canvas).toEqual(frame.canvas)
    expect(result.queries).toBe(screen.queries)
    for (const binding of result.components) {
      const slot = layouts.presets[0].slots.find(s => s.id === frame.bindings[binding.id])!
      expect(binding.layout).toEqual(slot.layout)
      expect(binding.title).toBe(screen.components.find(b => b.id === binding.id)!.title)
    }
    expect(screen.title).not.toBe(frame.title)
  })
  it.each(['missing', 'duplicate', 'unknown', 'map-role', 'unfilled'])('requires content reconciliation: %s', failure => {
    const edited = structuredClone(frame)
    if (failure === 'missing') delete edited.bindings.energy
    if (failure === 'duplicate') edited.bindings.energy = 'overview-1'
    if (failure === 'unknown') edited.bindings.energy = 'unknown'
    if (failure === 'map-role') { edited.bindings.map = 'left-top'; edited.bindings.energy = 'map' }
    const input = failure === 'unfilled' ? { ...screen, components: screen.components.filter(b => b.id !== 'energy') } : screen
    if (failure === 'unfilled') delete edited.bindings.energy
    expect(() => bindFramework(input as Screen, edited, layouts as any, palettes)).toThrow()
  })
})
