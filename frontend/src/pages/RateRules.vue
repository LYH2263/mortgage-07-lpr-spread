<script setup>
import { computed, onMounted, ref } from 'vue'
import { getJSON, patchJSON, postJSON } from '../api'

const items = ref([])
const form = ref({ name: '', lpr: 3.6, spread_bps: 55 })
const error = ref('')

const compose = (lpr, bps) => Number(lpr) + Number(bps) / 100
const formRate = computed(() => compose(form.value.lpr, form.value.spread_bps))

async function load() {
  items.value = (await getJSON('/api/baselines')).items
}
async function createBaseline() {
  error.value = ''
  if (formRate.value < 0) { error.value = '合成年利率不得为负'; return }
  await postJSON('/api/baselines', { ...form.value, enabled: true })
  form.value = { name: '', lpr: 3.6, spread_bps: 55 }
  await load()
}
async function edit(it) {
  error.value = ''
  const lpr = prompt(`LPR（${it.name}）`, it.lpr)
  if (lpr === null) return
  const spread_bps = prompt('加点基点（负为减点）', it.spread_bps)
  if (spread_bps === null) return
  if (compose(Number(lpr), Number(spread_bps)) < 0) { error.value = '合成年利率不得为负'; return }
  try {
    await patchJSON(`/api/baselines/${it.id}`, { lpr: Number(lpr), spread_bps: Number(spread_bps) })
  } catch (e) { error.value = e.message; return }
  await load()
}
async function disable(it) {
  if (!confirm(`停用基准「${it.name}」？停用后试算不可再引用，历史记录不受影响。`)) return
  try {
    await patchJSON(`/api/baselines/${it.id}`, { enabled: false })
  } catch (e) { error.value = e.message; return }
  await load()
}
onMounted(load)
</script>
<template><div class="page">
  <h1>LPR 加点基准</h1>
  <p>合成年利率 = LPR + 加点基点 ÷ 100（1 基点 = 0.01%），且不得为负。停用后不可再被试算引用，已落库记录的月供不变。</p>
  <table>
    <tr><th>#</th><th>名称</th><th>LPR %</th><th>加点 BP</th><th>合成年利率 %</th><th>状态</th><th></th></tr>
    <tr v-for="it in items" :key="it.id">
      <td>{{ it.id }}</td>
      <td>{{ it.name }}</td>
      <td>{{ it.lpr }}</td>
      <td>{{ it.spread_bps }}</td>
      <td>{{ compose(it.lpr, it.spread_bps).toFixed(2) }}</td>
      <td>{{ it.enabled ? '启用' : '停用' }}</td>
      <td>
        <button @click="edit(it)">编辑</button>
        <button v-if="it.enabled" @click="disable(it)">停用</button>
      </td>
    </tr>
  </table>
  <h2>新建基准</h2>
  <label>名称 <input v-model="form.name" placeholder="如 5年期首套" /></label>
  <label>LPR % <input v-model.number="form.lpr" type="number" step="0.01" /></label>
  <label>加点 BP <input v-model.number="form.spread_bps" type="number" step="1" /></label>
  <span>合成 {{ formRate.toFixed(2) }}%</span>
  <button @click="createBaseline">创建</button>
  <p v-if="error" style="color:#a00">{{ error }}</p>
</div></template>
