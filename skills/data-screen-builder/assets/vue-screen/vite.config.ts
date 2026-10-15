import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const provider = env.VITE_DATA_PROVIDER || 'mock'
  if (!['mock', 'http'].includes(provider)) throw new Error('VITE_DATA_PROVIDER must be mock or http')
  if (command === 'build' && mode !== 'demo' && provider !== 'http') {
    throw new Error('Production build requires VITE_DATA_PROVIDER=http. Use npm run build:demo for an explicitly labelled demo.')
  }
  return {
    plugins: [vue()],
    // Prebundle the lazy renderers too: discovering a new dependency on the first
    // map switch otherwise makes Vite reload the page and reset the selected design.
    optimizeDeps: { include: [
      'three', 'three/addons/controls/OrbitControls.js', 'three/addons/renderers/CSS2DRenderer.js',
      'three/addons/postprocessing/EffectComposer.js', 'three/addons/postprocessing/RenderPass.js',
      'three/addons/postprocessing/UnrealBloomPass.js', 'three/addons/postprocessing/OutputPass.js',
      'ol/Map.js', 'ol/View.js', 'ol/format/GeoJSON.js', 'ol/layer/Vector.js', 'ol/layer/Tile.js',
      'ol/source/Vector.js', 'ol/source/XYZ.js', 'ol/style.js', 'ol/control/defaults.js',
      'ol/proj/Projection.js', 'ol/proj.js',
    ] },
    define: { __DATA_PROVIDER__: JSON.stringify(provider) },
    server: { proxy: { '/api': { target: env.METRICS_PROXY_TARGET || 'http://127.0.0.1:4175', changeOrigin: true } } },
  }
})
