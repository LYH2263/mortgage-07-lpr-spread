<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
const principal = ref(800000)
const annual_rate = ref(4.2)
const months = ref(360)
const baselines = ref([])
const baseline_id = ref(null)
const out = ref(null)
const error = ref('')

const selected = () => baselines.value.find(b => b.id === baseline_id.value) || null
const composed = () => {
  const b = selected()
  return b ? b.lpr + b.spread_bps / 100 : null
}

onMounted(async () => { baselines.value = (await getJSON('/api/baselines?enabled=true')).items })

const run = async () => {
  error.value = ''
  out.value = null
  const body = {
    principal: principal.value,
    annual_rate: annual_rate.value,
    months: months.value,
    baseline_id: baseline_id.value,
    persist: true,
  }
  try {
    out.value = await postJSON('/api/schedule', body)
  } catch (e) { error.value = e.message }
}
</script>
<template><div class="page"><h1>等额本息试算</h1>
<label>本金 <input v-model.number="principal" /></label>
<label>月数 <input v-model.number="months" /></label>
<label>LPR 基准
  <select v-model="baseline_id">
    <option :value="null">不引用（手填年利率）</option>
    <option v-for="b in baselines" :key="b.id" :value="b.id">{{ b.name }}（{{ (b.lpr + b.spread_bps / 100).toFixed(2) }}%）</option>
  </select>
</label>
<label v-if="!baseline_id">年利率% <input v-model.number="annual_rate" /></label>
<p v-if="baseline_id">合成年利率 = {{ selected().lpr }} + {{ selected().spread_bps }}/100 = <strong>{{ composed().toFixed(2) }}%</strong></p>
<button @click="run">计算</button>
<p v-if="error" style="color:#a00">{{ error }}</p>
<p v-if="out">
  合成年利率 {{ out.annual_rate }}%<template v-if="out.baseline_name">（基准：{{ out.baseline_name }}）</template>
  · 月供 {{ out.monthly_payment }} · 利息合计 {{ out.total_interest }}
</p>
</div></template>
