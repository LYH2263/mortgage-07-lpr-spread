<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON, putJSON } from '../api'
const items = ref([])
const blank = { name: '', lpr: 3.6, spread_bp: 0 }
const form = ref({ ...blank })
const editing = ref(null)
const err = ref('')
const load = async () => { items.value = (await getJSON('/api/benchmarks')).items }
const synth = b => (Math.round((b.lpr + b.spread_bp / 100) * 1e6) / 1e6).toFixed(2)
const submit = async () => {
  err.value = ''
  try {
    if (editing.value) await putJSON(`/api/benchmarks/${editing.value}`, form.value)
    else await postJSON('/api/benchmarks', form.value)
    form.value = { ...blank }; editing.value = null
    await load()
  } catch (e) { err.value = String(e.message || e) }
}
const edit = b => { editing.value = b.id; form.value = { name: b.name, lpr: b.lpr, spread_bp: b.spread_bp } }
const cancel = () => { editing.value = null; form.value = { ...blank } }
const toggle = async b => { await postJSON(`/api/benchmarks/${b.id}/${b.enabled ? 'disable' : 'enable'}`, {}); await load() }
onMounted(load)
</script>
<template><div class="page"><h1>利率基准（LPR 加点）</h1>
<p>合成年利率 = LPR + 加点基点 / 100，且不得为负。试算可引用启用中的基准。</p>
<p>
  <input v-model="form.name" placeholder="名称" />
  <label>LPR% <input v-model.number="form.lpr" type="number" step="0.01" style="width:6rem" /></label>
  <label>加点BP <input v-model.number="form.spread_bp" type="number" style="width:6rem" /></label>
  <button @click="submit">{{ editing ? '保存' : '新建' }}</button>
  <button v-if="editing" @click="cancel">取消</button>
  <span v-if="err" style="color:red">{{ err }}</span>
</p>
<table>
<tr><th>#</th><th>名称</th><th>LPR%</th><th>加点BP</th><th>合成年利率%</th><th>状态</th><th>操作</th></tr>
<tr v-for="b in items" :key="b.id">
  <td>{{ b.id }}</td><td>{{ b.name }}</td><td>{{ b.lpr }}</td><td>{{ b.spread_bp }}</td>
  <td>{{ synth(b) }}</td>
  <td>{{ b.enabled ? '启用' : '停用' }}</td>
  <td><a href="#" @click.prevent="edit(b)">编辑</a> · <a href="#" @click.prevent="toggle(b)">{{ b.enabled ? '停用' : '启用' }}</a></td>
</tr>
</table>
</div></template>
