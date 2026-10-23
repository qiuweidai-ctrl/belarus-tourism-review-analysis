<template>
  <div class="wc">
    <header class="page-head">
      <div>
        <h1 class="page-title">Word Clouds</h1>
        <p class="page-sub">What people actually say. The bigger a word appears, the more often it shows up in the chosen scope.</p>
      </div>
      <div class="seg" role="tablist" aria-label="Scope">
        <button
          v-for="s in scopes"
          :key="s.key"
          class="seg-btn"
          :class="{ on: scope === s.key }"
          role="tab"
          :aria-selected="scope === s.key"
          @click="scope = s.key"
        >{{ s.label }}</button>
      </div>
    </header>

    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <section v-if="words.length" class="grid grid-4 stats fade-up">
      <StatCard label="Total words" :value="totalWords" icon="📚" color="var(--brand-600)" />
      <StatCard label="Distinct words" :value="words.length" icon="🔤" color="var(--info)" />
      <StatCard label="Most common" :value="topWord" icon="🏆" color="var(--accent-600)" :hint="topCount + ' mentions'" />
      <StatCard label="Active scope" :value="scopeLabel" icon="🎯" color="var(--success)" />
    </section>

    <section v-if="loading" class="card cloud-card">
      <div class="empty-state"><div class="spinner"></div><span>Loading…</span></div>
    </section>

    <section v-else-if="words.length === 0" class="card cloud-card">
      <EmptyState icon="☁️" title="No words to display" hint="Try switching the scope or check back once more reviews come in." />
    </section>

    <section v-else class="card cloud-card">
      <div ref="canvas" class="canvas"></div>
    </section>

    <section v-if="words.length" class="card topcard">
      <div class="section-head">
        <h2>Top 15</h2>
        <p class="sub">If the cloud is too abstract, here are the leading words in order.</p>
      </div>
      <ol class="toplist">
        <li
          v-for="(w, i) in topList"
          :key="w.word"
          class="toprow"
          :style="{ '--row-color': palette[i % palette.length] }"
        >
          <span class="rk">{{ i + 1 }}</span>
          <span class="wd">{{ w.word }}</span>
          <div class="bar"><span :style="{ width: barWidth(w.count) + '%' }"></span></div>
          <span class="ct">{{ w.count.toLocaleString('en-US') }}</span>
        </li>
      </ol>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import 'echarts-wordcloud'
import { analyticsAPI } from '@/api/client.js'
import StatCard from '../components/StatCard.vue'
import EmptyState from '../components/EmptyState.vue'

const scope = ref('both')
const scopes = [
  { key: 'both', label: 'All content' },
  { key: 'reviews', label: 'Reviews' },
  { key: 'attractions', label: 'Attractions' }
]

const words = ref([])
const totalWords = ref(0)
const loading = ref(true)
const error = ref('')

const canvas = ref(null)
let chart = null
let observer = null

const scopeLabel = computed(() => (scopes.find((s) => s.key === scope.value) || {}).label || '')
const topWord = computed(() => words.value[0] ? words.value[0].word : '—')
const topCount = computed(() => words.value[0] ? words.value[0].count : 0)
const topList = computed(() => words.value.slice(0, 15))
const maxCount = computed(() => words.value[0] ? words.value[0].count : 1)
const barWidth = (n) => (n / maxCount.value) * 100

const palette = [
  '#0f766e', '#2563eb', '#7c3aed', '#db2777',
  '#ea580c', '#ca8a04', '#16a34a', '#0891b2'
]

const buildOption = () => ({
  tooltip: { show: true, formatter: (p) => `${p.name}<br/>${p.value.toLocaleString('en-US')} mentions` },
  series: [{
    type: 'wordCloud',
    shape: 'circle',
    keepAspectShape: true,
    left: 'center', top: 'center',
    width: '100%', height: '100%',
    sizeRange: [14, 56],
    rotationRange: [-20, 20],
    rotationStep: 10,
    gridSize: 8,
    drawOutOfBound: false,
    textStyle: {
      fontFamily: 'Inter, Segoe UI, system-ui, sans-serif',
      fontWeight: 600,
      color: (params) => palette[params.dataIndex % palette.length]
    },
    emphasis: { textStyle: { color: '#111827', textShadowBlur: 8, textShadowColor: 'rgba(15, 23, 42, .2)' } },
    data: words.value.map((w) => ({ name: w.word, value: w.count }))
  }]
})

const render = async () => {
  if (!canvas.value || words.value.length === 0) return
  await nextTick()
  if (!chart) {
    chart = echarts.init(canvas.value)
    requestAnimationFrame(() => chart && chart.resize())
  }
  chart.setOption(buildOption(), { notMerge: true })
  if (typeof ResizeObserver !== 'undefined' && !observer) {
    observer = new ResizeObserver(() => chart && chart.resize())
    observer.observe(canvas.value)
  }
}

const load = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await analyticsAPI.keywords({ scope: scope.value, limit: 200 })
    words.value = res.data.words || []
    totalWords.value = res.data.total_words || 0
  } catch (e) {
    error.value = 'Could not load the word cloud.'
  } finally { loading.value = false }
}
watch(words, async (v) => {
  if (v && v.length) await render()
}, { flush: 'post' })

const onThemeChanged = () => { if (chart) chart.setOption(buildOption(), { notMerge: true }) }

watch(scope, load)

onMounted(() => {
  load()
  window.addEventListener('app:theme-changed', onThemeChanged)
})
onBeforeUnmount(() => {
  window.removeEventListener('app:theme-changed', onThemeChanged)
  if (observer && canvas.value) observer.disconnect()
  if (chart) { chart.dispose(); chart = null }
})
</script>

<style scoped>
.wc { display: flex; flex-direction: column; gap: 1.25rem; }
.page-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }

.seg { display: inline-flex; background: var(--surface-2); border: 1px solid var(--border); border-radius: var(--radius-pill); padding: 2px; }
.seg-btn { border: none; background: none; cursor: pointer; font: inherit; font-size: .82rem; font-weight: 600; color: var(--text-soft); padding: .3rem .75rem; border-radius: var(--radius-pill); transition: background-color var(--speed) var(--ease), color var(--speed) var(--ease); }
.seg-btn:hover { color: var(--text); }
.seg-btn.on { background: var(--grad-brand); color: #fff; box-shadow: var(--shadow-xs); }

.cloud-card { padding: 0; height: 480px; overflow: hidden; }
.canvas { width: 100%; height: 100%; }

.topcard { padding: 1rem 1.1rem; }
.toplist { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: .35rem; }
.toprow { display: grid; grid-template-columns: 32px 140px 1fr 80px; align-items: center; gap: .8rem; }
.rk { font-weight: 700; color: var(--row-color); text-align: right; }
.wd { font-weight: 600; color: var(--text); }
.bar { height: 8px; background: var(--surface-2); border-radius: var(--radius-pill); overflow: hidden; }
.bar > span { display: block; height: 100%; background: var(--row-color); border-radius: var(--radius-pill); }
.ct { text-align: right; color: var(--row-color); font-variant-numeric: tabular-nums; font-size: .88rem; font-weight: 600; }

.spinner { width: 30px; height: 30px; border: 3px solid var(--border); border-top-color: var(--brand-500); border-radius: 50%; animation: spin .8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 640px) {
  .cloud-card { height: 360px; }
  .toprow { grid-template-columns: 24px 1fr 64px; }
  .toprow .bar { display: none; }
}
</style>
