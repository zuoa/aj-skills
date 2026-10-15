import { markRaw, type Component } from 'vue'
import type { ComponentType } from '../contracts/types'
import manifest from '../config/component-types.json'

export const builtinTypes = manifest.builtin as ComponentType[]
const custom = new Map<string, Component>()
export function registerComponent(name: string, component: Component): void {
  if (builtinTypes.includes(name as ComponentType) || custom.has(name)) throw new Error(`Component already registered: ${name}`)
  custom.set(name, markRaw(component))
}
export function componentTypes(): string[] { return [...builtinTypes, ...custom.keys()] }
export function customComponent(name: string): Component | undefined { return custom.get(name) }
