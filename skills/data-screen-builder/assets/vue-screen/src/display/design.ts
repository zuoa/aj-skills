import type { Binding, Screen, Geography } from '../contracts/types'
import type { Theme } from '../theme'

export interface DesignProfile {
  id: string; name: string; intent: string; style: 'cinematic' | 'restrained'
  renderer: Geography['renderer']; gridRows: string; tokens: Partial<Theme>
  layouts: Record<string, Binding['layout']>
}
export function withDesign(screen: Screen, design: DesignProfile, renderer = design.renderer): Screen {
  const ids = new Set(screen.components.map(b => b.id))
  for (const id of Object.keys(design.layouts)) if (!ids.has(id)) throw new Error(`设计引用未知组件 ${id}`)
  return { ...screen, components: screen.components.map(b => ({
    ...b, layout: design.layouts[b.id] || b.layout,
    geography: b.geography ? { ...b.geography, renderer } : undefined,
  })) }
}
