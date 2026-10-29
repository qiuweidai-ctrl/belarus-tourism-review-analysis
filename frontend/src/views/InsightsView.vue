<template>
  <div class="insights">
    <header class="page-head">
      <div>
        <h1 class="page-title">Data Insights</h1>
        <p class="page-sub">
          Every chart below is aggregated in SQL so the picture stays readable —
          no 30-slice pies, no overlapping line spaghetti.
        </p>
      </div>
      <div class="head-actions">
        <button
          v-for="d in exportDatasets"
          :key="d.key"
          class="btn btn-ghost btn-sm"
          :disabled="exporting === d.key"
          @click="doExport(d.key)"
        >
          {{ exporting === d.key ? 'Preparing...' : 'Export ' + d.label }}
        </button>
      </div>
    </header>

    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <section class="grid grid-4 fade-up" aria-label="Key figures">
      <StatCard label="Attractions" :value="ov.attractions || 0" icon="🏛️" color="var(--brand-600)" />
      <StatCard label="Published reviews" :value="ov.reviews || 0" icon="💬" color="var(--info)" />
      <StatCard label="Average rating" :value="ov.avg_rating || 0" :decimals="2" icon="⭐" color="var(--accent-600)" suffix=" / 5" />
      <StatCard
        label="Positive sentiment"
        :value="positiveRatio"
        :decimals="1" icon="😊" color="var(--success)" suffix="%"
        :hint="ov.sentiment ? ov.sentiment.positive + ' of ' + ov.sentiment.total + ' analysed' : ''"
      />
      <StatCard label="Registered users" :value="ov.users || 0" icon="👥" color="var(--brand-600)" />
      <StatCard label="Travel guides" :value="ov.articles || 0" icon="📰" color="var(--info)" />
      <StatCard label="Total views" :value="ov.total_views || 0" icon="👁️" color="var(--accent-600)" />
      <StatCard label="Average ticket" :value="ov.avg_price || 0" :decimals="2" icon="🎟️" color="var(--brand-600)" suffix=" BYN" />
    </section>

    <section class="chart-grid fade-up">
      <ChartCard
        title="Rating distribution"
        subtitle="How visitors scored their visits"
        :option="ratingOption"
        :loading="loading"
        height="310px"
      />
      <ChartCard
        title="Who visits"
        subtitle="Traveller type mix"
        :option="travelTypeOption"
        :loading="loading"
        height="310px"
      />
    </section>

    <section class="chart-grid fade-up">
      <ChartCard
        title="Attractions by category"
        subtitle="Tile size is attraction count, shade is average rating"
        :option="categoryOption"
        :loading="loading"
        height="380px"
      />
      <ChartCard
        title="Where they are"
        subtitle="Attraction count per region, ranked"
        :option="regionOption"
        :loading="loading"
        height="380px"
      />
    </section>

    <section class="chart-grid fade-up">
      <ChartCard title="Ticket price bands" subtitle="Percentage of attractions in each price range" :option="priceOption" :loading="loading" height="320px">
        <template #footer>
          <span>Average ticket price: <strong>{{ Number(priceSummary.avg || 0).toFixed(2) }} BYN</strong></span>
        </template>
      </ChartCard>
      <ChartCard
        title="Reviews over time"
        subtitle="Monthly volume with the average score for each month"
        :option="trendOption"
        :loading="loading"
        height="320px"
      />
    </section>

    <section class="chart-grid fade-up">
      <ChartCard
        title="Sentiment by category"
        subtitle="Share of positive / neutral / negative reviews"
        :option="sentimentOption"
        :loading="loading"
        height="360px"
      />

      <section class="card leaderboard">
        <header class="lb-head">
          <h3>Leaderboard</h3>
          <div class="seg" role="tablist">
            <button
              v-for="m in metrics"
              :key="m.key"
              class="seg-btn"
              :class="{ on: metric === m.key }"
              role="tab"
              :aria-selected="metric === m.key"
              @click="metric = m.key"
            >{{ m.label }}</button>
          </div>
        </header>
        <ol v-if="top.length" class="lb-list">
          <li v-for="(a, i) in top" :key="a.id" class="lb-row" @click="$router.push('/attractions/' + a.id)">
            <span class="rank" :class="'r' + Math.min(i + 1, 4)">{{ i + 1 }}</span>
            <img v-if="a.image_url" :src="a.image_url" :alt="a.name" loading="lazy" />
            <span v-else class="no-img">🏛️</span>
            <span class="lb-name">
              <strong>{{ a.name }}</strong>
              <em>{{ formatPlace(a.city || a.region) || '—' }}</em>
            </span>
            <span class="lb-value">
              <strong>{{ metricValue(a) }}</strong>
              <em>{{ metricLabel }}</em>
            </span>
          </li>
        </ol>
        <p v-else class="empty-state">No attractions to rank yet.</p>
      </section>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { analyticsAPI } from '@/api/client.js'
import StatCard from '../components/StatCard.vue'
import ChartCard from '../components/ChartCard.vue'
import { formatCategory, formatPlace } from '@/utils/displayText.js'

const loading = ref(true)
const error = ref('')
const exporting = ref('')

const ov = ref({})
const rating = ref({ stars: [], categories: [] })
const region = ref({ regions: [], cities: [] })
const price = ref({ bands: [], summary: {} })
const trend = ref({ points: [], travel_types: [] })
const sentiment = ref({ overall: [], by_category: [] })
const top = ref([])
const metric = ref('rating')

const metrics = [
  { key: 'rating', label: 'Rating', label_: 'rating', fmt: (a) => Number(a.avg_rating).toFixed(2) },
  { key: 'reviews', label: 'Reviews', label_: 'reviews', fmt: (a) => a.total_reviews },
  { key: 'views', label: 'Views', label_: 'views', fmt: (a) => a.view_count },
  { key: 'wishlist', label: 'Saves', label_: 'saves', fmt: (a) => a.wishlist_count }
]
const metricLabel = computed(() => (metrics.find((m) => m.key === metric.value) || {}).label_ || '')
const metricValue = (a) => (metrics.find((m) => m.key === metric.value) || metrics[0]).fmt(a)

let signedInUser = null
try {
  signedInUser = JSON.parse(localStorage.getItem('user') || 'null')
} catch (_) {
  signedInUser = null
}

const exportDatasets = [
  { key: 'attractions', label: 'attractions' },
  { key: 'reviews', label: 'reviews' },
  { key: 'users', label: 'users' }
].filter((item) => item.key !== 'users' || ['admin', 'moderator'].includes(signedInUser?.role))

const priceSummary = computed(() => price.value.summary || {})

const positiveRatio = computed(() => {
  const s = ov.value.sentiment
  if (!s || !s.total) return 0
  return (s.positive / s.total) * 100
})

const brandGreen = '#0d9478'
const brandTeal = '#14b893'
const amber = '#f59e0b'
const blue = '#3b82f6'
const purple = '#8b5cf6'
const pink = '#ec4899'
const cyan = '#06b6d4'

const ratingOption = computed(() => {
  const rows = rating.value.stars || []
  return {
    grid: { left: 8, right: 30, top: 24, bottom: 8, containLabel: true },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: {
      type: 'category',
      data: rows.map((r) => r.rating + ' ★'),
      axisLabel: { fontSize: 12 }
    },
    yAxis: { type: 'value', name: 'Reviews', nameTextStyle: { fontSize: 11 } },
    series: [{
      type: 'bar',
      data: rows.map((r) => ({
        value: r.count,
        itemStyle: { color: r.rating >= 4 ? brandGreen : r.rating === 3 ? amber : '#ef4444' }
      })),
      barWidth: '52%',
      itemStyle: { borderRadius: [6, 6, 0, 0] },
      label: { show: true, position: 'top', color: 'inherit', fontWeight: 600 }
    }]
  }
})

const travelTypeOption = computed(() => {
  const rows = (trend.value.travel_types || []).map((r) => ({ name: r.label, value: r.count }))
  return {
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0, icon: 'circle' },
    series: [{
      type: 'pie',
      radius: ['46%', '70%'],
      center: ['50%', '44%'],
      avoidLabelOverlap: true,
      itemStyle: { borderColor: '#fff', borderWidth: 2, borderRadius: 4 },
      label: { formatter: '{b}\n{d}%', fontSize: 11, lineHeight: 15 },
      labelLine: { length: 10, length2: 10 },
      data: rows
    }]
  }
})

const categoryOption = computed(() => {
  const rows = rating.value.categories || []
  return {
    tooltip: {
      formatter: (p) => {
        const r = rows.find((x) => formatCategory(x.category) === p.name) || {}
        return `<strong>${p.name}</strong><br/>Attractions: ${p.value}<br/>Average rating: ${r.avg_rating}`
      }
    },
    series: [{
      type: 'treemap',
      roam: false,
      nodeClick: false,
      breadcrumb: { show: false },
      width: '100%',
      height: '100%',
      top: 0, left: 0, right: 0, bottom: 0,
      itemStyle: { borderColor: '#fff', borderWidth: 3, gapWidth: 3, borderRadius: 4 },
      upperLabel: { show: false },
      label: {
        show: true,
        formatter: '{b}\n{c} attractions',
        fontSize: 12,
        fontWeight: 600,
        color: '#fff'
      },
      levels: [{
        itemStyle: { borderColor: '#fff', borderWidth: 3, gapWidth: 3 },
        upperLabel: { show: false }
      }],
      data: rows.map((r) => ({
        name: formatCategory(r.category),
        value: r.count,
        avg: r.avg_rating
      }))
    }]
  }
})

const regionOption = computed(() => {
  const rows = [...(region.value.regions || [])].sort((a, b) => b.count - a.count)
  return {
    grid: { left: 8, right: 40, top: 16, bottom: 34, containLabel: true },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (ps) => {
        const r = rows.find((x) => formatPlace(x.region) === ps[0].name) || {}
        return `${ps[0].name}<br/>Attractions: ${ps[0].value}<br/>Average rating: ${r.avg_rating}`
      }
    },
    xAxis: {
      type: 'value',
      name: 'Attractions',
      nameLocation: 'middle',
      nameGap: 27,
      nameTextStyle: { fontSize: 10 },
      axisLabel: { fontSize: 9 }
    },
    yAxis: {
      type: 'category',
      data: rows.map((r) => formatPlace(r.region)).reverse(),
      axisLabel: { fontSize: 10 }
    },
    series: [{
      type: 'bar',
      data: rows.map((r) => r.count).reverse(),
      barWidth: '58%',
      itemStyle: {
        borderRadius: [0, 6, 6, 0],
        color: (p) => [brandGreen, brandTeal, blue, purple, amber, pink, cyan][p.dataIndex % 7]
      },
      label: { show: true, position: 'right', fontWeight: 600, fontSize: 9 }
    }]
  }
})

const priceOption = computed(() => {
  const rows = price.value.bands || []
  const total = rows.reduce((sum, row) => sum + Number(row.count || 0), 0)
  const percentages = rows.map((row) => total ? Number((row.count / total * 100).toFixed(1)) : 0)
  return {
    grid: { left: 8, right: 24, top: 24, bottom: 32, containLabel: true },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (items) => {
        const item = items[0]
        const source = rows.find((row) => row.label === item.name) || {}
        return `${item.name}<br/>${item.value}% of attractions<br/>${source.count || 0} attractions`
      }
    },
    xAxis: {
      type: 'value',
      name: 'Percentage of attractions',
      nameLocation: 'middle',
      nameGap: 27,
      max: 100,
      axisLabel: { formatter: '{value}%', fontSize: 9 },
      nameTextStyle: { fontSize: 10 }
    },
    yAxis: {
      type: 'category',
      data: rows.map((r) => r.label).reverse(),
      axisLabel: { fontSize: 11 }
    },
    series: [{
      type: 'bar',
      data: percentages.reverse(),
      barWidth: '58%',
      itemStyle: {
        borderRadius: [0, 6, 6, 0],
        color: (p) => [brandGreen, brandTeal, blue, purple, amber][p.dataIndex % 5]
      },
      label: { show: true, position: 'right', formatter: '{c}%', fontWeight: 600, fontSize: 10 }
    }]
  }
})

const trendOption = computed(() => {
  const pts = trend.value.points || []
  return {
    legend: { top: 0, icon: 'roundRect' },
    grid: { left: 8, right: 24, top: 44, bottom: 8, containLabel: true },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: pts.map((p) => p.month), axisLabel: { fontSize: 11 } },
    yAxis: [
      { type: 'value', name: 'Reviews' },
      { type: 'value', name: 'Average rating', min: 0, max: 5, splitLine: { show: false } }
    ],
    series: [
      {
        name: 'Reviews',
        type: 'bar',
        data: pts.map((p) => p.count),
        barWidth: '46%',
        itemStyle: { borderRadius: [6, 6, 0, 0], color: brandTeal }
      },
      {
        name: 'Average rating',
        type: 'line',
        yAxisIndex: 1,
        data: pts.map((p) => p.avg_rating),
        smooth: true,
        symbolSize: 8,
        lineStyle: { width: 3, color: amber },
        itemStyle: { color: amber, borderColor: '#fff', borderWidth: 2 }
      }
    ]
  }
})

const sentimentOption = computed(() => {
  const rows = [...(sentiment.value.by_category || [])].sort((a, b) => b.total - a.total)
  return {
    legend: { top: 0, icon: 'roundRect' },
    grid: { left: 8, right: 24, top: 44, bottom: 8, containLabel: true },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: { type: 'category', data: rows.map((r) => formatCategory(r.category)), axisLabel: { fontSize: 11, interval: 0, rotate: rows.length > 6 ? 30 : 0 } },
    yAxis: { type: 'value', name: 'Reviews' },
    series: [
      {
        name: 'Positive', type: 'bar', stack: 's',
        data: rows.map((r) => r.positive),
        itemStyle: { color: '#10b981' },
        barMaxWidth: 34
      },
      {
        name: 'Neutral', type: 'bar', stack: 's',
        data: rows.map((r) => r.neutral),
        itemStyle: { color: '#cbd5e1' },
        barMaxWidth: 34
      },
      {
        name: 'Negative', type: 'bar', stack: 's',
        data: rows.map((r) => r.negative),
        itemStyle: { color: '#ef4444', borderRadius: [4, 4, 0, 0] },
        barMaxWidth: 34
      }
    ]
  }
})

const loadTop = async () => {
  try {
    const res = await analyticsAPI.topAttractions({ metric: metric.value, limit: 8 })
    top.value = res.data.items || []
  } catch (e) { }
}

const loadAll = async () => {
  loading.value = true
  error.value = ''
  try {
    const [o, r, reg, p, t, s] = await Promise.all([
      analyticsAPI.overview(),
      analyticsAPI.ratingDistribution(),
      analyticsAPI.regionDistribution(),
      analyticsAPI.priceAnalysis(),
      analyticsAPI.reviewTrend(),
      analyticsAPI.sentimentBreakdown()
    ])
    ov.value = o.data
    rating.value = r.data
    region.value = reg.data
    price.value = p.data
    trend.value = t.data
    sentiment.value = s.data
    await loadTop()
  } catch (e) {
    error.value = 'Could not load analytics. Is the Flask API running on port 5000?'
    console.error(e)
  } finally {
    loading.value = false
  }
}

watch(metric, loadTop)

const doExport = async (dataset) => {
  exporting.value = dataset
  try {
    const res = await analyticsAPI.exportCsv(dataset)
    const url = URL.createObjectURL(new Blob([res.data], { type: 'text/csv' }))
    const a = document.createElement('a')
    a.href = url
    a.download = `${dataset}.csv`
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  } catch (e) {
    error.value = `Export failed: ${e.message}`
  } finally {
    exporting.value = ''
  }
}

onMounted(loadAll)
</script>

<style scoped>
.insights { display: flex; flex-direction: column; gap: 1.25rem; }
.page-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }
.head-actions { display: flex; gap: .5rem; flex-wrap: wrap; }

.leaderboard { padding: 1.1rem 1.15rem 1.15rem; }
.lb-head { display: flex; align-items: center; justify-content: space-between; gap: .75rem; flex-wrap: wrap; margin-bottom: .9rem; }
.lb-head h3 { margin: 0; font-size: 1.02rem; }

.seg { display: inline-flex; background: var(--surface-2); border: 1px solid var(--border); border-radius: var(--radius-pill); padding: 2px; }
.seg-btn {
  border: none; background: none; cursor: pointer;
  font: inherit; font-size: .8rem; font-weight: 600;
  color: var(--text-soft);
  padding: .3rem .7rem; border-radius: var(--radius-pill);
  transition: background-color var(--speed) var(--ease), color var(--speed) var(--ease);
}
.seg-btn:hover { color: var(--text); }
.seg-btn.on { background: var(--grad-brand); color: #fff; box-shadow: var(--shadow-xs); }

.lb-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: .3rem; }
.lb-row {
  display: flex; align-items: center; gap: .7rem;
  padding: .45rem .55rem; border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background-color var(--speed) var(--ease);
}
.lb-row:hover { background: var(--surface-hover); }
.rank {
  width: 24px; height: 24px; flex-shrink: 0;
  border-radius: 7px;
  display: inline-flex; align-items: center; justify-content: center;
  font-size: .76rem; font-weight: 800;
  background: var(--surface-2); color: var(--text-soft);
}
.rank.r1 { background: linear-gradient(135deg, #fbbf24, #f59e0b); color: #fff; }
.rank.r2 { background: linear-gradient(135deg, #cbd5e1, #94a3b8); color: #fff; }
.rank.r3 { background: linear-gradient(135deg, #d8a47f, #b45309); color: #fff; }

.lb-row img { width: 40px; height: 40px; border-radius: var(--radius-sm); object-fit: cover; flex-shrink: 0; }
.no-img {
  width: 40px; height: 40px; border-radius: var(--radius-sm); flex-shrink: 0;
  display: inline-flex; align-items: center; justify-content: center;
  background: var(--brand-50); font-size: 1.1rem;
}
.lb-name { display: flex; flex-direction: column; min-width: 0; flex: 1 1 auto; }
.lb-name strong { font-size: .88rem; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.lb-name em { font-style: normal; font-size: .74rem; color: var(--text-mute); }
.lb-value { display: flex; flex-direction: column; align-items: flex-end; flex-shrink: 0; }
.lb-value strong { font-size: .9rem; color: var(--brand-700); }
.lb-value em { font-style: normal; font-size: .7rem; color: var(--text-mute); }
[data-theme='dark'] .lb-value strong { color: var(--brand-300); }
</style>
