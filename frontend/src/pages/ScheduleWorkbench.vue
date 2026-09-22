<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
const principal = ref(800000)
const annual_rate = ref(4.2)
const months = ref(360)
const benchmarks = ref([])
const benchmark_id = ref(null)
const out = ref(null)
onMounted(async () => { benchmarks.value = (await getJSON('/api/benchmarks')).items.filter(b => b.enabled) })
const run = async () => {
  const body = { principal: principal.value, annual_rate: annual_rate.value, months: months.value, persist: true }
  if (benchmark_id.value) body.benchmark_id = benchmark_id.value
  out.value = await postJSON('/api/schedule', body)
}
</script>
<template><div class="page"><h1>等额本息试算</h1>
<label>本金 <input v-model.number="principal" /></label>
<label>利率基准 <select v-model="benchmark_id">
  <option :value="null">手动年利率</option>
  <option v-for="b in benchmarks" :key="b.id" :value="b.id">{{ b.name }}（{{ b.lpr }}% {{ b.spread_bp >= 0 ? '+' : '' }}{{ b.spread_bp }}BP）</option>
</select></label>
<label v-if="!benchmark_id">年利率% <input v-model.number="annual_rate" /></label>
<label>月数 <input v-model.number="months" /></label>
<button @click="run">计算</button>
<p v-if="out">合成年利率 {{ out.annual_rate }}% · 月供 {{ out.monthly_payment }} · 利息合计 {{ out.total_interest }}</p>
</div></template>
