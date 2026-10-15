<script setup lang="ts">
defineProps<{ kind: string }>()
const paths: Record<string, string> = {
  metric: 'M4 19V8l8-4 8 4v11H4ZM8 19v-6h8v6M8 8v2m4-4v4m4-2v2',
  trend: 'M4 4v16h16M7 15l4-5 4 3 5-7',
  composition: 'M12 3a9 9 0 1 0 9 9h-9V3ZM15 3.5A9 9 0 0 1 20.5 9H15V3.5Z',
  ranking: 'M4 7h16M4 12h12M4 17h8',
  map: 'M3 7l6-3 6 3 6-3v13l-6 3-6-3-6 3V7ZM9 4v13m6-10v13',
  heatmap: 'M4 4h6v6H4V4Zm10 0h6v6h-6V4ZM4 14h6v6H4v-6Zm10 0h6v6h-6v-6Z',
  table: 'M4 4h16v16H4V4Zm0 5h16M9 9v11',
  alerts: 'M12 3l10 18H2L12 3Zm0 6v5m0 3v1',
  status: 'M5 12l4 4 10-10',
  settings: 'M4 7h16M4 17h16M8 4v6m8 4v6',
  fullscreen: 'M9 3H3v6m12-6h6v6M3 15v6h6m12-6v6h-6',
}
</script>

<template><svg class="screen-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path :d="paths[kind] || paths.metric" /></svg></template>
