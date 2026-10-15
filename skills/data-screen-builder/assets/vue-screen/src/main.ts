import { createApp } from 'vue'
import { applyTheme } from './theme'
import './style.css'
import './visual-styles.css'
import './showcase-effects.css'
import './luminous-gallery.css'
import './refined-showcase.css'

applyTheme()
// The framework entry does not import business configuration, providers or maps.
const view = new URLSearchParams(location.search).get('view')
const entry = view === 'framework'
  ? import('./FrameworkPreview.vue') : import('./App.vue')
entry.then(({ default: App }) => createApp(App, { showcase: view === 'showcase' }).mount('#app'))
