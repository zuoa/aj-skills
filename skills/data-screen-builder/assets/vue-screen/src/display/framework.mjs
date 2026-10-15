import Ajv2020 from 'ajv/dist/2020.js'
import schema from './framework.schema.json' with { type: 'json' }
import bundledStyles from '../config/styles.json' with { type: 'json' }

const ajv = new Ajv2020({ allErrors: true, strict: true, allowUnionTypes: true })
ajv.addSchema(schema)
function shape(kind, value) {
  const check = ajv.getSchema(`${schema.$id}#/$defs/${kind}`)
  if (!check(value)) throw new Error(`framework ${kind}: ${ajv.errorsText(check.errors)}`)
}
function ensure(value, message) { if (!value) throw new Error(`framework: ${message}`) }
export function assertLayout(layout) {
  shape('layout', layout)
  ensure(new Set(layout.slots.map(s => s.id)).size === layout.slots.length, 'duplicate slot ID')
  for (const slot of layout.slots) {
    const r = slot.layout
    ensure(r.col + r.width <= 13 && r.row + r.height <= layout.rows + 1, `slot ${slot.id} exceeds grid`)
  }
  for (let i = 0; i < layout.slots.length; i++) for (let j = i + 1; j < layout.slots.length; j++) {
    const a = layout.slots[i].layout, b = layout.slots[j].layout
    ensure(!(a.col < b.col + b.width && b.col < a.col + a.width && a.row < b.row + b.height && b.row < a.row + a.height), `overlapping slots ${layout.slots[i].id}, ${layout.slots[j].id}`)
  }
  return layout
}
export function resolveStyle(frame, styles = bundledStyles) {
  ensure(styles.version === '1' && Array.isArray(styles.presets), 'invalid style library')
  ensure(new Set(styles.presets.map(p => p.id)).size === styles.presets.length, 'duplicate style ID')
  for (const preset of styles.presets) shape('style', preset)
  if (frame.customStyle) { shape('style', frame.customStyle); ensure(frame.customStyle.id === 'custom', 'customStyle.id must be custom') }
  ensure(styles.presets.every(p => p.id !== 'custom'), 'reserved style ID custom')
  const id = frame.styleId || (frame.visualStyle === 'cinematic' ? 'command-hud' : 'editorial-light')
  const style = id === 'custom' ? frame.customStyle : styles.presets.find(p => p.id === id)
  ensure(style, `unknown style ${id}`)
  return style
}
export function resolveFramework(frame, layouts, palettes, styles = bundledStyles) {
  shape('frame', frame)
  for (const [kind, library] of [['layout', layouts], ['palette', palettes]]) {
    ensure(library.version === '1' && Array.isArray(library.presets), `invalid ${kind} library`)
    ensure(new Set(library.presets.map(p => p.id)).size === library.presets.length, `duplicate ${kind} ID`)
    ensure(library.presets.every(p => p.id !== 'custom'), `reserved ${kind} ID custom`)
    for (const preset of library.presets) kind === 'layout' ? assertLayout(preset) : shape('palette', preset)
  }
  const layout = frame.layoutId === 'custom' ? frame.customLayout : layouts.presets.find(p => p.id === frame.layoutId)
  const palette = frame.paletteId === 'custom' ? frame.customPalette : palettes.presets.find(p => p.id === frame.paletteId)
  ensure(layout, `unknown layout ${frame.layoutId}`)
  ensure(palette, `unknown palette ${frame.paletteId}`)
  if (frame.customLayout) { assertLayout(frame.customLayout); ensure(frame.customLayout.id === 'custom', 'customLayout.id must be custom') }
  if (frame.customPalette) { shape('palette', frame.customPalette); ensure(frame.customPalette.id === 'custom', 'customPalette.id must be custom') }
  return { layout, palette, style: resolveStyle(frame, styles) }
}

// The final page consumes the same slots as the empty preview. Never guess a binding.
export function bindFramework(screen, frame, layouts, palettes, styles = bundledStyles) {
  const { layout } = resolveFramework(frame, layouts, palettes, styles)
  const ids = new Set(screen.components.map(b => b.id)), used = new Set()
  ensure(ids.size === screen.components.length, 'duplicate component ID')
  ensure(Object.keys(frame.bindings).length === ids.size && Object.keys(frame.bindings).every(id => ids.has(id)), 'bindings must cover every component exactly once')
  const components = screen.components.map(binding => {
    const slotId = frame.bindings[binding.id], slot = layout.slots.find(s => s.id === slotId)
    ensure(slot, `unknown slot for ${binding.id}`)
    ensure(!used.has(slotId), `duplicate binding to ${slotId}`)
    used.add(slotId)
    ensure((binding.type === 'map') === (slot.role === 'map'), `map role mismatch for ${binding.id}`)
    if (slot.role === 'metric') ensure(binding.type === 'metric' || binding.type === 'status', `metric role mismatch for ${binding.id}`)
    return { ...binding, layout: { ...slot.layout } }
  })
  ensure(used.size === layout.slots.length, 'unfilled slots; reconcile content and confirm the revised framework')
  return { ...screen, title: frame.title, canvas: { ...frame.canvas }, components }
}
