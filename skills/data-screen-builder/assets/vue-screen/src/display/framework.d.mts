import type { Screen, Binding } from '../contracts/types'
import type { Theme } from '../theme'

export interface FrameSlot { id: string; label: string; role: 'metric' | 'chart' | 'map' | 'list' | 'main'; layout: Binding['layout'] }
export interface FrameLayout { id: string; name: string; description: string; aspect: string; rows: number; slots: FrameSlot[] }
export interface FramePalette { id: string; name: string; tokens: Partial<Theme> }
export type Ornament = 'none' | 'mecha' | 'hologram' | 'astral' | 'gilded' | 'luminous'
export type EffectIntensity = 'off' | 'low' | 'medium' | 'high'
export interface FrameStyle { id: string; name: string; description: string; effects: 'cinematic' | 'restrained'; ornament?: Ornament; defaultIntensity?: EffectIntensity; recommendedPalettes: string[]; tokens: Partial<Theme> }
export interface Framework {
  version: string; title: string; canvas: { width: number; height: number }
  layoutId: string; paletteId: string; styleId?: string; customStyle?: FrameStyle; effectIntensity?: EffectIntensity; bindings: Record<string, string>
  visualStyle?: 'cinematic' | 'restrained'; customLayout?: FrameLayout; customPalette?: FramePalette
}
export interface Library<T> { version: string; presets: T[] }
export function assertLayout(layout: FrameLayout): FrameLayout
export function resolveStyle(frame: Pick<Framework, 'styleId' | 'visualStyle' | 'customStyle'>, styles?: Library<FrameStyle>): FrameStyle
export function resolveFramework(frame: Framework, layouts: Library<FrameLayout>, palettes: Library<FramePalette>, styles?: Library<FrameStyle>): { layout: FrameLayout; palette: FramePalette; style: FrameStyle }
export function bindFramework(screen: Screen, frame: Framework, layouts: Library<FrameLayout>, palettes: Library<FramePalette>, styles?: Library<FrameStyle>): Screen
