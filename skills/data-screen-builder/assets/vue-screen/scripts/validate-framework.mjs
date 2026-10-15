import { readFile } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import { resolve } from 'node:path'
import { resolveFramework } from '../src/display/framework.mjs'

const root = process.argv[2] ? resolve(process.argv[2]) : fileURLToPath(new URL('..', import.meta.url))
try {
  const [frame, layouts, palettes, styles] = await Promise.all(['framework', 'layouts', 'palettes', 'styles'].map(async name => JSON.parse(await readFile(resolve(root, `src/config/${name}.json`), 'utf8'))))
  const { layout, palette, style } = resolveFramework(frame, layouts, palettes, styles)
  console.log(`PASS: empty framework, ${layout.slots.length} slots, ${layout.name}, ${palette.name}, ${style.name}; no business data loaded`)
} catch (error) { console.error(error.message); process.exitCode = 1 }
