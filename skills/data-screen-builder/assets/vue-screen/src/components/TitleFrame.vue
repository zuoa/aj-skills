<script setup lang="ts">
import type { Ornament } from '../display/framework.mjs'
import TitleOrnament from './TitleOrnament.vue'
defineProps<{ title: string; subtitle: string; ornament?: Ornament }>()
</script>

<template>
  <div class="title-block">
    <TitleOrnament v-if="ornament && ornament !== 'none'" :kind="ornament" />
    <span class="title-wing left-wing fx" aria-hidden="true"></span>
    <div class="title-copy"><h1 :class="{ 'long-title': title.length > 14 }">{{ title }}</h1><p class="title-subtitle">{{ subtitle }}</p></div>
    <span class="title-wing right-wing fx" aria-hidden="true"></span>
  </div>
</template>
