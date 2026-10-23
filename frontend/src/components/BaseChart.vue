<template>
  <div class="base-chart" :style="{ height: height }">
    <div v-if="loading" class="chart-overlay">
      <div class="spinner" aria-hidden="true"></div>
      <span>{{ $t('common.loading') }}</span>
    </div>
    <div v-else-if="isEmpty" class="chart-overlay">
      <span class="emoji" aria-hidden="true">📊</span>
      <span>{{ emptyText }}</span>
    </div>
    <div v-show="!loading && !isEmpty" ref="el" class="chart-canvas"></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import * as echarts from 'echarts/core'
import {
  BarChart, LineChart, PieChart, ScatterChart, RadarChart, TreemapChart, GaugeChart
} from 'echarts/charts'
import {
  GridComponent, TooltipComponent, LegendComponent, TitleComponent,
  DatasetComponent, VisualMapComponent, MarkLineComponent, DataZoomComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([
  BarChart, LineChart, PieChart, ScatterChart, RadarChart, TreemapChart, GaugeChart,
  GridComponent, TooltipComponent, LegendComponent, TitleComponent,
  DatasetComponent, VisualMapComponent, MarkLineComponent, DataZoomComponent,
  CanvasRenderer
])

const props = defineProps({
  option: { type: Object, required: true },
  height: { type: String, default: '320px' },
  loading: { type: Boolean, default: false },
  emptyText: { type: String, default: 'No data to display' }
})

const el = ref(null)
let chart = null
let observer = null
const isEmpty = computed(() => {
  const o = props.option
  if (!o) return true
  if (Array.isArray(o.series)) {
    if (o.series.length === 0) return true
    return o.series.every((s) => !s || !Array.isArray(s.data) || s.data.length === 0)
  }
  if (Array.isArray(o.data) && Array.isArray(o.treeData)) {
    return o.data.length === 0 && o.treeData.length === 0
  }
  if (Array.isArray(o.data) && o.series == null && o.xAxis == null) {
    return o.data.length === 0
  }
  return false
})

const cssVar = (name, fallback) => {
  const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim()
  return v || fallback
}

const palette = () => [
  cssVar('--brand-500', '#14b893'),
  cssVar('--accent-500', '#f59e0b'),
  '#3b82f6',
  '#8b5cf6',
  '#ec4899',
  '#06b6d4',
  '#84cc16',
  '#f97316',
  '#6366f1',
  '#14b8a6'
]

const buildOption = () => {
  const base = props.option || {}
  const textSoft = cssVar('--text-soft', '#475569')
  const textMute = cssVar('--text-mute', '#94a3b8')
  const border = cssVar('--border', '#e2e8f0')
  const surface = cssVar('--surface', '#ffffff')
  const colors = palette()
  const defaults = {
    color: colors,
    textStyle: { color: textSoft, fontFamily: 'Inter, Segoe UI, system-ui, sans-serif' },
    grid: { left: 8, right: 18, top: 40, bottom: 8, containLabel: true },
    tooltip: {
      backgroundColor: surface,
      borderColor: border,
      borderWidth: 1,
      padding: [8, 12],
      textStyle: { color: textSoft, fontSize: 12 },
      extraCssText: 'box-shadow: 0 8px 24px rgba(15,23,42,.14); border-radius: 10px;'
    },
    legend: {
      textStyle: { color: textSoft },
      icon: 'roundRect',
      itemWidth: 10,
      itemHeight: 10,
      itemGap: 14
    }
  }

  const merged = { ...defaults, ...base }
  if (merged.xAxis && !Array.isArray(merged.xAxis)) {
    merged.xAxis = {
      axisLine: { lineStyle: { color: border } },
      axisTick: { show: false },
      axisLabel: { color: textMute, fontSize: 11 },
      splitLine: { show: false },
      ...merged.xAxis
    }
  }
  if (Array.isArray(merged.xAxis)) {
    merged.xAxis = merged.xAxis.map((ax) => ({
      axisLine: { lineStyle: { color: border } },
      axisTick: { show: false },
      axisLabel: { color: textMute, fontSize: 11 },
      splitLine: { show: false },
      ...ax
    }))
  }
  if (merged.yAxis && !Array.isArray(merged.yAxis)) {
    merged.yAxis = {
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: textMute, fontSize: 11 },
      splitLine: { lineStyle: { color: border, type: 'dashed' } },
      ...merged.yAxis
    }
  }
  if (Array.isArray(merged.yAxis)) {
    merged.yAxis = merged.yAxis.map((ax) => ({
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: textMute, fontSize: 11 },
      splitLine: { lineStyle: { color: border, type: 'dashed' } },
      ...ax
    }))
  }

  return merged
}

const render = () => {
  if (!chart) return
  chart.setOption(buildOption(), { notMerge: true })
}

const init = () => {
  if (!el.value || props.loading || isEmpty.value) return
  if (!el.value.clientWidth || !el.value.clientHeight) return
  if (chart) chart.dispose()
  chart = echarts.init(el.value)
  render()
}

const scheduleInit = () => {
  requestAnimationFrame(() => requestAnimationFrame(() => {
    if (!chart) init()
    if (chart) chart.resize()
  }))
}

onMounted(async () => {
  await nextTick()
  scheduleInit()
  if (el.value && typeof ResizeObserver !== 'undefined') {
    observer = new ResizeObserver(() => chart && chart.resize())
    observer.observe(el.value)
  }
  window.addEventListener('resize', onResize)
  window.addEventListener('app:theme-changed', onThemeChanged)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
  window.removeEventListener('app:theme-changed', onThemeChanged)
  if (observer && el.value) observer.disconnect()
  if (chart) { chart.dispose(); chart = null }
})

const onResize = () => chart && chart.resize()
const onThemeChanged = () => { if (chart) chart.setOption(buildOption(), { notMerge: true }) }

watch(() => props.option, () => {
  if (props.loading || isEmpty.value) {
    if (chart) chart.clear()
    return
  }
  if (!chart) scheduleInit()
  else render()
}, { deep: true })

watch(() => props.loading, async (v) => {
  if (!v) {
    await nextTick()
    if (!chart) scheduleInit()
    else { render(); chart.resize() }
  } else if (chart) {
    chart.clear()
  }
})

watch(isEmpty, async (v) => {
  if (!v) {
    await nextTick()
    if (!chart) scheduleInit()
    else { render(); chart.resize() }
  }
})

defineExpose({ getInstance: () => chart })
</script>

<style scoped>
.base-chart { position: relative; width: 100%; }
.chart-canvas { width: 100%; height: 100%; }
.chart-overlay {
  position: absolute; inset: 0;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: .6rem; color: var(--text-mute); font-size: .88rem;
}
.emoji { font-size: 2rem; opacity: .6; }
.spinner {
  width: 30px; height: 30px;
  border: 3px solid var(--border);
  border-top-color: var(--brand-500);
  border-radius: 50%;
  animation: spin .8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
