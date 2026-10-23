<template>
  <div class="home-dashboard">
    <section class="welcome-row">
      <div>
        <span class="eyebrow">TRAVEL OVERVIEW</span>
        <h1>Discover Belarus</h1>
        <p>Explore trusted reviews, regional insights and personalized travel ideas.</p>
      </div>
      <div class="welcome-actions">
        <button class="btn btn-ghost" @click="$router.push('/insights')">View insights</button>
        <button class="btn btn-primary" @click="$router.push('/attractions')">Explore attractions</button>
      </div>
    </section>

    <section class="metric-grid">
      <article v-for="item in metrics" :key="item.label" class="metric-card card">
        <span class="metric-icon" :class="item.tone">{{ item.icon }}</span>
        <div>
          <small>{{ item.label }}</small>
          <strong>{{ item.value }}</strong>
          <span>{{ item.note }}</span>
        </div>
      </article>
    </section>

    <section class="dashboard-panels">
      <article class="dashboard-card card">
        <header class="panel-head">
          <div>
            <h2>Attractions by region</h2>
            <p>Verified destinations across Belarus</p>
          </div>
          <button class="text-button" type="button" @click="$router.push('/map')">Open map →</button>
        </header>
        <div v-if="loading" class="panel-loading skeleton"></div>
        <div v-else class="region-list">
          <div v-for="region in regions.slice(0, 7)" :key="region.region" class="region-row">
            <div class="region-meta">
              <span>{{ region.region }}</span>
              <strong>{{ region.count }}</strong>
            </div>
            <div class="bar-track">
              <span :style="{ width: `${Math.max(8, region.count / maxRegionCount * 100)}%` }"></span>
            </div>
          </div>
        </div>
      </article>

      <article class="dashboard-card card">
        <header class="panel-head">
          <div>
            <h2>Popular this season</h2>
            <p>Most viewed places in the platform</p>
          </div>
          <button class="text-button" type="button" @click="$router.push('/rankings')">Full ranking →</button>
        </header>
        <div v-if="loading" class="panel-loading skeleton"></div>
        <div v-else class="popular-list">
          <button
            v-for="(item, index) in trending"
            :key="item.id"
            type="button"
            class="popular-row"
            @click="$router.push(`/attractions/${item.id}`)"
          >
            <span class="rank">{{ String(index + 1).padStart(2, '0') }}</span>
            <img :src="item.image_url" alt="" />
            <span class="popular-name">
              <strong>{{ item.name }}</strong>
              <small>{{ item.city }} · {{ item.category }}</small>
            </span>
            <span class="popular-score">{{ formatNumber(item.view_count) }}</span>
          </button>
        </div>
      </article>
    </section>

    <section class="quick-grid">
      <button v-for="item in quickLinks" :key="item.to" class="quick-card card" type="button" @click="$router.push(item.to)">
        <span class="quick-icon">{{ item.icon }}</span>
        <span>
          <strong>{{ item.title }}</strong>
          <small>{{ item.hint }}</small>
        </span>
        <b>→</b>
      </button>
    </section>

    <section>
      <div class="section-head">
        <div>
          <h2>Top-rated attractions</h2>
          <p class="sub">Places receiving the strongest visitor scores</p>
        </div>
        <button class="btn btn-ghost btn-sm" @click="$router.push('/attractions')">View all</button>
      </div>
      <div v-if="loading" class="grid grid-3">
        <div v-for="index in 3" :key="index" class="skeleton attraction-skeleton"></div>
      </div>
      <div v-else-if="!attractions.length" class="empty-state card">No attractions are available.</div>
      <div v-else class="grid grid-3">
        <AttractionCard v-for="item in attractions.slice(0, 3)" :key="item.id" :attraction="item" />
      </div>
    </section>

    <section>
      <div class="section-head">
        <div>
          <h2>Recent reviews</h2>
          <p class="sub">The latest feedback shared by travelers</p>
        </div>
      </div>
      <div v-if="recentReviews.length" class="review-grid">
        <article v-for="review in recentReviews" :key="review.id" class="review-card card">
          <header>
            <span class="stars">{{ '★'.repeat(review.rating) }}<i>{{ '★'.repeat(5 - review.rating) }}</i></span>
            <span class="pill" :class="sentimentClass(review.sentiment_label)">{{ review.sentiment_label || 'neutral' }}</span>
          </header>
          <h3>{{ review.title || 'Traveler review' }}</h3>
          <p>{{ truncate(review.content) }}</p>
          <footer>
            <strong>{{ review.username || 'Traveler' }}</strong>
            <span>{{ review.attraction_name || '' }}</span>
          </footer>
        </article>
      </div>
      <div v-else-if="!loading" class="empty-state card">No reviews have been posted yet.</div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { analyticsAPI, attractionsAPI, reviewsAPI } from '@/api/client.js'
import AttractionCard from '../components/AttractionCard.vue'

const attractions = ref([])
const trending = ref([])
const recentReviews = ref([])
const regions = ref([])
const overview = ref({})
const loading = ref(true)

const formatNumber = (value) => Number(value || 0).toLocaleString('en-US')
const metrics = computed(() => [
  { label: 'Attractions', value: formatNumber(overview.value.attractions), note: 'verified destinations', icon: '◇', tone: 'mint' },
  { label: 'Traveler reviews', value: formatNumber(overview.value.reviews), note: `${overview.value.sentiment?.positive || 0} positive`, icon: '✎', tone: 'blue' },
  { label: 'Average rating', value: `${Number(overview.value.avg_rating || 0).toFixed(1)} / 5`, note: 'across all attractions', icon: '★', tone: 'amber' },
  { label: 'Total views', value: formatNumber(overview.value.total_views), note: `${overview.value.users || 0} registered travelers`, icon: '◉', tone: 'violet' }
])
const maxRegionCount = computed(() => Math.max(...regions.value.map((item) => item.count), 1))
const quickLinks = [
  { to: '/insights', icon: '▥', title: 'Data Insights', hint: 'Explore platform trends' },
  { to: '/map', icon: '⌖', title: 'Map Explorer', hint: 'Browse by location' },
  { to: '/itinerary', icon: '▣', title: 'Trip Planner', hint: 'Build a day-by-day plan' },
  { to: '/wordcloud', icon: '☁', title: 'Word Clouds', hint: 'See common review topics' }
]

const sentimentClass = (label) => ({ positive: 'pill-success', negative: 'pill-danger', neutral: 'pill-info' }[label] || 'pill-info')
const truncate = (text, limit = 145) => !text ? '' : text.length > limit ? `${text.slice(0, limit)}…` : text

onMounted(async () => {
  try {
    const [featuredRes, trendingRes, reviewRes, overviewRes, regionRes] = await Promise.all([
      attractionsAPI.list({ per_page: 6, sort: 'rating' }),
      analyticsAPI.topAttractions({ metric: 'views', limit: 6 }),
      reviewsAPI.list({ per_page: 6 }),
      analyticsAPI.overview(),
      analyticsAPI.regionDistribution()
    ])
    attractions.value = featuredRes.data.attractions || []
    trending.value = trendingRes.data.items || []
    recentReviews.value = reviewRes.data.reviews || []
    overview.value = overviewRes.data || {}
    regions.value = regionRes.data.regions || []
  } catch (error) {
    console.error('Dashboard data could not be loaded', error)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.home-dashboard { display: flex; flex-direction: column; gap: 1.4rem; }
.welcome-row { display: flex; align-items: flex-end; justify-content: space-between; gap: 1rem; }
.eyebrow { color: var(--brand-600); font-size: .68rem; font-weight: 800; letter-spacing: .14em; }
.welcome-row h1 { margin: .2rem 0 .25rem; font-size: 1.9rem; }
.welcome-row p { margin: 0; color: var(--text-mute); font-size: .9rem; }
.welcome-actions { display: flex; gap: .6rem; flex-wrap: wrap; }
.metric-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 1rem; }
.metric-card { display: flex; align-items: center; gap: .9rem; padding: 1.15rem; }
.metric-icon { width: 46px; height: 46px; flex: 0 0 46px; display: grid; place-items: center; border-radius: 12px; font-size: 1.25rem; font-weight: 800; }
.metric-icon.mint { color: #087b65; background: #d9f8ef; }
.metric-icon.blue { color: #2563eb; background: #dbeafe; }
.metric-icon.amber { color: #c56a09; background: #ffedd5; }
.metric-icon.violet { color: #7c3aed; background: #ede9fe; }
.metric-card div { min-width: 0; display: flex; flex-direction: column; }
.metric-card small { color: var(--text-mute); font-size: .72rem; }
.metric-card strong { color: var(--text); font-size: 1.45rem; line-height: 1.25; }
.metric-card span:not(.metric-icon) { color: var(--text-mute); font-size: .68rem; }
.dashboard-panels { display: grid; grid-template-columns: minmax(0, 1.45fr) minmax(360px, .85fr); gap: 1rem; }
.dashboard-card { min-height: 365px; padding: 1.2rem; }
.panel-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; margin-bottom: 1rem; }
.panel-head h2 { margin: 0; font-size: 1rem; }
.panel-head p { margin: .2rem 0 0; color: var(--text-mute); font-size: .74rem; }
.text-button { color: var(--brand-600); background: none; border: 0; cursor: pointer; font: inherit; font-size: .75rem; font-weight: 700; }
.panel-loading { height: 270px; }
.region-list { display: flex; flex-direction: column; gap: .82rem; padding-top: .35rem; }
.region-meta { display: flex; justify-content: space-between; gap: 1rem; margin-bottom: .25rem; color: var(--text-soft); font-size: .76rem; }
.region-meta strong { color: var(--text); }
.bar-track { height: 8px; overflow: hidden; background: var(--surface-hover); border-radius: var(--radius-pill); }
.bar-track span { display: block; height: 100%; border-radius: inherit; background: linear-gradient(90deg, var(--brand-600), var(--brand-300)); }
.popular-list { display: flex; flex-direction: column; }
.popular-row { display: grid; grid-template-columns: 28px 44px minmax(0, 1fr) auto; align-items: center; gap: .65rem; width: 100%; padding: .62rem .15rem; color: inherit; text-align: left; background: transparent; border: 0; border-bottom: 1px solid var(--border); cursor: pointer; }
.popular-row:last-child { border-bottom: 0; }
.popular-row:hover { background: var(--surface-hover); }
.popular-row img { width: 44px; height: 36px; object-fit: cover; border-radius: 7px; background: var(--surface-2); }
.rank { color: var(--text-mute); font-size: .68rem; font-weight: 800; }
.popular-name { min-width: 0; display: flex; flex-direction: column; }
.popular-name strong { overflow: hidden; color: var(--text); font-size: .76rem; text-overflow: ellipsis; white-space: nowrap; }
.popular-name small { color: var(--text-mute); font-size: .64rem; text-transform: capitalize; }
.popular-score { color: var(--brand-600); font-size: .72rem; font-weight: 800; }
.quick-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 1rem; }
.quick-card { display: flex; align-items: center; gap: .75rem; padding: .9rem; color: inherit; text-align: left; cursor: pointer; }
.quick-card:hover { border-color: var(--brand-300); box-shadow: var(--shadow); }
.quick-icon { width: 36px; height: 36px; flex: 0 0 36px; display: grid; place-items: center; color: var(--brand-700); background: var(--brand-50); border-radius: 9px; }
.quick-card > span:nth-child(2) { min-width: 0; display: flex; flex: 1; flex-direction: column; }
.quick-card strong { font-size: .78rem; }
.quick-card small { color: var(--text-mute); font-size: .66rem; }
.quick-card b { color: var(--text-mute); font-size: .85rem; }
.attraction-skeleton { height: 260px; }
.review-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1rem; }
.review-card { display: flex; flex-direction: column; gap: .55rem; min-height: 180px; padding: 1rem; }
.review-card header, .review-card footer { display: flex; align-items: center; justify-content: space-between; gap: .5rem; }
.review-card h3 { margin: 0; font-size: .85rem; }
.review-card p { flex: 1; margin: 0; color: var(--text-soft); font-size: .76rem; line-height: 1.55; }
.review-card footer { color: var(--text-mute); font-size: .67rem; }
.review-card footer span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.stars { color: var(--accent-500); font-size: .75rem; letter-spacing: .06em; }
.stars i { color: var(--border-strong); font-style: normal; }
@media (max-width: 1180px) {
  .metric-grid, .quick-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .dashboard-panels { grid-template-columns: 1fr; }
  .review-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 640px) {
  .welcome-row { align-items: flex-start; flex-direction: column; }
  .welcome-row h1 { font-size: 1.55rem; }
  .welcome-actions { width: 100%; }
  .welcome-actions .btn { flex: 1; }
  .metric-grid, .quick-grid, .review-grid { grid-template-columns: 1fr; }
  .dashboard-card { min-height: auto; padding: 1rem; }
}
</style>
