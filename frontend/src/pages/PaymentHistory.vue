<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
onMounted(async () => {
  const rows = (await getJSON('/api/history')).items
  items.value = rows.map(h => ({ ...h, input: JSON.parse(h.input_json), result: JSON.parse(h.result_json) }))
})
</script>
<template><div class="page"><h1>试算记录</h1>
<p>记录钉选测算时的合成年利率；之后调高 LPR 不影响历史月供。</p>
<table>
<tr><th>#</th><th>时间</th><th>年利率%</th><th>月供</th><th>利息合计</th></tr>
<tr v-for="h in items" :key="h.id">
  <td>#{{ h.id }}</td><td>{{ h.created_at }}</td>
  <td>{{ h.input.annual_rate }}</td>
  <td>{{ h.result.monthly_payment }}</td>
  <td>{{ h.result.total_interest }}</td>
</tr>
</table>
</div></template>
