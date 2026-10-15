<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import type { Catalog, Field, MetricQuery, Screen } from '../contracts/types'
import { resultFields } from '../contracts/validate.mjs'
import type { QueryClient } from '../data/client'
import { createReport, type LocalReports } from '../data/local-reports'

const props = defineProps<{ catalog: Catalog; screen: Screen; queries: Record<string, MetricQuery>; client: QueryClient; reports: LocalReports }>()
const emit = defineEmits<{ close: [] }>()
// Freeze the context at entry, so clock ticks cannot replace an in-progress form.
const queries = JSON.parse(JSON.stringify(props.queries)) as Record<string, MetricQuery>
const queryIds = [...new Set(props.screen.components.map(component => component.queryId))]
const selected = ref(queryIds[0] || '')
const query = computed(() => queries[selected.value])
const metric = computed(() => props.catalog.metrics.find(item => item.id === query.value?.metricId))
const fields = computed(() => metric.value ? resultFields(metric.value, query.value) as Field[] : [])
const draft = ref<Record<string, string>[]>([])
const dataAsOf = ref(''), baseline = ref(''), error = ref(''), message = ref(''), loading = ref(false), hasLocal = ref(false)
const cacheError = ref(props.reports.error)
const dialog = ref<HTMLDialogElement>()
const restorePending = ref(false)
let stop: (() => void) | undefined
let populated = false
const snapshot = () => JSON.stringify([draft.value, dataAsOf.value])
const dirty = computed(() => snapshot() !== baseline.value)
const context = computed(() => {
  if (!query.value) return ''
  const q = query.value
  const filters = Object.entries(q.filters).map(([name, value]) => `${name}=${JSON.stringify(value)}`).join('，')
  return `${filters || '全部区域'} · 最近 ${(Date.parse(q.timeRange.to) - Date.parse(q.timeRange.from)) / 3600000} 小时 · ${q.timeRange.timezone}`
})
function localTime(value: string): string {
  const date = new Date(value)
  return new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 19)
}
function name(field: Field): string {
  if (field.name === 'value') return `数值（${metric.value?.unit || '无单位'}）`
  if (field.name === 'time') return '时间'
  return props.screen.components.find(c => c.queryId === selected.value && c.fields.label === field.name)?.type === 'map' ? `${field.name}（地图区域 ID）` : field.name
}
function addRow(): void { draft.value.push(Object.fromEntries(fields.value.map(field => [field.name, '']))) }
function load(): void {
  stop?.(); error.value = ''; message.value = ''; populated = false; restorePending.value = false
  draft.value = []; dataAsOf.value = localTime(new Date().toISOString()); baseline.value = snapshot()
  if (!query.value) return
  hasLocal.value = Boolean(props.reports.get(query.value))
  cacheError.value = props.reports.error
  stop = props.client.subscribe(query.value, state => {
    loading.value = state.loading
    if (populated || dirty.value) return
    if (state.result) {
      draft.value = state.result.rows.map(row => Object.fromEntries(fields.value.map(field => {
        const value = row[field.name]
        return [field.name, value === null ? '' : field.type === 'timestamp' ? localTime(String(value)) : String(value)]
      })))
      dataAsOf.value = localTime(state.result.dataAsOf)
      populated = true; error.value = ''
    } else if (state.error) {
      error.value = `${state.error}，可手动添加记录并填报。`
    }
    baseline.value = snapshot()
  })
}
function changeQuery(event: Event): void {
  const control = event.target as HTMLSelectElement
  if (dirty.value && !window.confirm('当前指标有未保存的修改，确定放弃？')) { control.value = selected.value; return }
  selected.value = control.value; load()
}
function save(): void {
  try {
    props.reports.save(query.value, createReport(props.catalog, query.value, draft.value, dataAsOf.value))
    hasLocal.value = true; baseline.value = snapshot(); error.value = ''; cacheError.value = ''; restorePending.value = false
    message.value = '已保存，大屏已更新。刷新页面后仍会保留。'
  } catch (cause) { error.value = cause instanceof Error ? cause.message : '保存失败，请重试。'; message.value = '' }
}
function restore(): void {
  try {
    props.reports.remove(query.value)
    load()
    message.value = '已移除当前范围的填报，恢复原始数据源。'
  } catch (cause) { error.value = cause instanceof Error ? cause.message : '恢复失败，请重试。' }
}
function close(): void {
  if (dirty.value && !window.confirm('有未保存的修改，确定关闭并放弃？')) return
  dialog.value?.close(); emit('close')
}
onMounted(async () => { load(); await nextTick(); dialog.value?.showModal() })
onBeforeUnmount(() => { stop?.(); dialog.value?.close() })
</script>

<template>
  <Teleport to="body">
    <dialog ref="dialog" class="metric-report" aria-labelledby="report-title" aria-describedby="report-description" @cancel.prevent="close">
      <form @submit.prevent="save">
        <header class="report-heading"><div><p class="report-eyebrow">{{ screen.title }}</p><h2 id="report-title">指标填报</h2></div><button type="button" aria-label="关闭指标填报" @click="close">关闭</button></header>
        <p id="report-description" class="report-description">填写后保存即可更新大屏。数据仅保存在当前浏览器，不会提交到服务器。</p>
        <div class="report-controls">
          <label>填报指标<select :value="selected" aria-label="填报指标" autofocus @change="changeQuery"><option v-for="id in queryIds" :key="id" :value="id">{{ screen.components.filter(c => c.queryId === id).map(c => c.title).join(' / ') }}</option></select></label>
          <label>数据截至时间（本机时区）<input v-model="dataAsOf" aria-label="数据截至时间（本机时区）" type="datetime-local" step="1" required /></label>
        </div>
        <template v-if="metric">
          <div class="report-scope"><span>{{ context }}</span><strong>{{ hasLocal ? '已使用本地填报' : '当前为原始数据' }}</strong></div>
          <p class="report-definition">{{ metric.definition }}</p>
          <p class="report-hint">空白表示未知值；0 表示已知为零。时间按本机时区填写；地图区域 ID 和分类名称需与展示数据一致。</p>
          <p v-if="loading && !populated" role="status">正在读取当前数据，也可以直接添加记录填写。</p>
          <div class="report-table-wrap" tabindex="0" aria-label="填报数据表，可横向滚动">
            <table class="report-table"><thead><tr><th scope="col">记录</th><th v-for="field in fields" :key="field.name" scope="col">{{ name(field) }}</th><th scope="col">操作</th></tr></thead>
              <tbody><tr v-for="(row, index) in draft" :key="index"><th scope="row">{{ index + 1 }}</th><td v-for="field in fields" :key="field.name">
                <select v-if="field.type === 'boolean'" v-model="row[field.name]" :aria-label="`第 ${index + 1} 行 ${name(field)}`"><option value="">未知</option><option value="true">是</option><option value="false">否</option></select>
                <input v-else :value="row[field.name]" @input="row[field.name] = ($event.target as HTMLInputElement).value" :aria-label="`第 ${index + 1} 行 ${name(field)}`" :type="field.type === 'number' ? 'number' : field.type === 'timestamp' ? 'datetime-local' : 'text'" :step="field.type === 'number' ? 'any' : field.type === 'timestamp' ? '1' : undefined" placeholder="未知" />
              </td><td><button type="button" :aria-label="`删除第 ${index + 1} 行`" @click="draft.splice(index, 1)">删除</button></td></tr></tbody>
            </table>
            <p v-if="!draft.length" class="report-empty">暂无记录。添加记录开始填写，或保存为空数据。</p>
          </div>
          <button v-if="fields.length > 1 || !draft.length" type="button" class="report-add" @click="addRow">＋ 添加记录</button>
        </template>
        <p v-if="cacheError" class="report-error" role="status">{{ cacheError }}</p>
        <p v-if="error" class="report-error" role="alert">{{ error }}</p>
        <p v-if="message" class="report-success" role="status">{{ message }}</p>
        <div v-if="restorePending" class="report-restore" role="group" aria-label="确认恢复原始数据"><span>移除当前指标、当前范围的填报{{ dirty ? '并放弃未保存的修改' : '' }}？</span><button type="button" @click="restore">确认恢复</button><button type="button" @click="restorePending = false">取消</button></div>
        <footer class="report-footer"><button type="button" :disabled="!hasLocal" @click="restorePending = true">恢复原始数据</button><span>{{ dirty ? '有未保存的修改' : '保存后应用到当前范围' }}</span><button type="submit" class="report-save" :disabled="!metric">保存并更新大屏</button></footer>
      </form>
    </dialog>
  </Teleport>
</template>

<style scoped>
.metric-report { width: min(960px, calc(100vw - 32px)); max-height: calc(100dvh - 32px); margin: auto; padding: 28px; overflow-y: auto; border: 1px solid var(--muted); border-radius: 8px; background: var(--surface); color: var(--text); box-shadow: 0 24px 90px #0006; font: 14px/1.6 var(--bodyFont); }
.metric-report::backdrop { background: #030912b8; backdrop-filter: blur(5px); }
.report-heading, .report-footer, .report-scope, .report-restore { display: flex; align-items: center; justify-content: space-between; gap: 16px; }
.report-eyebrow { margin: 0 0 4px; color: var(--muted); font-size: 12px; }
.report-heading h2 { font-size: 24px; letter-spacing: 1px; }
.report-description { color: var(--muted); margin: 18px 0 24px; }
.report-controls { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.report-controls label { display: grid; gap: 8px; color: var(--muted); font-size: 12px; }
.metric-report input, .metric-report select { width: 100%; min-width: 150px; height: 40px; padding: 0 10px; border: 1px solid var(--muted); border-radius: 4px; background: var(--background); color: var(--text); font: inherit; }
.metric-report button { height: 38px; font-size: 13px; border-radius: 4px; white-space: nowrap; }
.report-scope { margin-top: 22px; flex-wrap: wrap; font-size: 12px; color: var(--muted); }
.report-scope strong { color: var(--accent); font-weight: 500; }
.report-definition { margin: 10px 0; }
.report-hint { font-size: 12px; color: var(--muted); margin: 0 0 16px; }
.report-table-wrap { max-height: 42dvh; overflow: auto; border: 1px solid var(--border); border-radius: 4px; }
.report-table { width: 100%; border-collapse: collapse; white-space: nowrap; text-align: left; }
.report-table th, .report-table td { padding: 10px 12px; border-bottom: 1px solid var(--border); }
.report-table thead { position: sticky; top: 0; background: var(--surface); z-index: 1; }
.report-table th { font-size: 12px; color: var(--muted); font-weight: 500; }
.report-table tbody th { width: 48px; }
.report-table input[type=number] { min-width: 160px; font-variant-numeric: tabular-nums; }
.report-table input[type=datetime-local] { min-width: 235px; }
.report-empty { text-align: center; color: var(--muted); padding: 12px; }
.report-add { margin-top: 12px; }
.report-error { color: var(--warning); overflow-wrap: anywhere; }
.report-success { color: var(--good); }
.report-restore { justify-content: flex-start; flex-wrap: wrap; padding: 12px 0; color: var(--warning); }
.report-footer { margin-top: 24px; padding-top: 20px; border-top: 1px solid var(--border); }
.report-footer span { margin-left: auto; font-size: 12px; color: var(--muted); }
.report-save { background: var(--accent); color: var(--background); border-color: var(--accent); font-weight: 600; }
@media (max-width: 600px) { .metric-report { padding: 20px 16px; } .report-controls { grid-template-columns: 1fr; gap: 14px; } .report-footer { flex-wrap: wrap; gap: 12px; } .report-footer span { display: none; } .report-save { margin-left: auto; } }
</style>
