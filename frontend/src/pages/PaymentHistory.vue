<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
onMounted(async () => { items.value = (await getJSON('/api/history')).items })
</script>
<template><div class="page"><h1>试算记录</h1>
<p>年利率在试算时钉选；之后调高 LPR 不改写旧条目的月供。</p>
<table>
  <tr><th>#</th><th>时间</th><th>基准</th><th>钉选年利率 %</th><th>月供</th><th>利息合计</th></tr>
  <tr v-for="h in items" :key="h.id">
    <td>#{{ h.id }}</td>
    <td>{{ h.created_at }}</td>
    <td>{{ h.baseline_name || '—' }}</td>
    <td>{{ h.annual_rate ?? '—' }}</td>
    <td>{{ h.monthly_payment ?? '—' }}</td>
    <td>{{ h.total_interest ?? '—' }}</td>
  </tr>
</table>
</div></template>
