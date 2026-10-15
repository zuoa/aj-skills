import { readFile } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import { resolve } from 'node:path'
import { assertConfig } from '../src/contracts/validate.mjs'
import { bindFramework, resolveFramework } from '../src/display/framework.mjs'

const root = process.argv[2] ? resolve(process.argv[2]) : fileURLToPath(new URL('..', import.meta.url))
async function json(path) { return JSON.parse(await readFile(resolve(root, path), 'utf8')) }
try {
  const [catalog, screen, manifest] = await Promise.all(['src/config/metrics.json', 'src/config/screen.json', 'src/config/component-types.json'].map(json))
  assertConfig(catalog, screen, [...manifest.builtin, ...manifest.custom])
  const [frame, layouts, palettes, styles] = await Promise.all(['framework', 'layouts', 'palettes', 'styles'].map(name => json(`src/config/${name}.json`)))
  resolveFramework(frame, layouts, palettes, styles)
  if (Object.keys(frame.bindings).length) assertConfig(catalog, bindFramework(screen, frame, layouts, palettes, styles), [...manifest.builtin, ...manifest.custom])
  const designs = await json('src/config/designs.json')
  if (!designs.profiles.some(p => p.id === designs.default)) throw new Error('unknown default design')
  for (const design of Object.keys(frame.bindings).length ? [] : designs.profiles) {
    const ids = new Set(screen.components.map(b => b.id))
    for (const id of Object.keys(design.layouts)) if (!ids.has(id)) throw new Error(`unknown layout component ${id}`)
    assertConfig(catalog, { ...screen, components: screen.components.map(b => ({ ...b, layout: design.layouts[b.id] || b.layout, geography: b.geography ? { ...b.geography, renderer: design.renderer } : undefined })) }, [...manifest.builtin, ...manifest.custom])
  }
  console.log(`PASS: ${catalog.metrics.length} metrics, ${Object.keys(screen.queries).length} queries, ${screen.components.length} components`)
} catch (error) { console.error(error.message); process.exitCode = 1 }
