<template>
  <div class="compare">
    <header class="page-head">
      <div>
        <h1 class="page-title">Compare Attractions</h1>
        <p class="page-sub">Pick two places to see them side by side, with the better value highlighted in every row.</p>
      </div>
    </header>

    <section class="card pickers">
      <div class="picker">
        <label>Attraction A</label>
        <select v-model="idA">
          <option value="">— pick an attraction —</option>
          <option v-for="a in optionsForB" :key="'A' + a.id" :value="a.id">{{ attractionName(a) }} · {{ formatPlace(a.city || a.region) || '—' }}</option>
        </select>
      </div>
      <button class="btn btn-ghost btn-sm swap" type="button" :disabled="!idA || !idB" @click="swap" title="Swap A and B">⇄</button>
      <div class="picker">
        <label>Attraction B</label>
        <select v-model="idB">
          <option value="">— pick an attraction —</option>
          <option v-for="a in optionsForA" :key="'B' + a.id" :value="a.id">{{ attractionName(a) }} · {{ formatPlace(a.city || a.region) || '—' }}</option>
        </select>
      </div>
    </section>

    <EmptyState
      v-if="!idA || !idB"
      icon="⚖️"
      title="Choose two attractions to compare"
      hint="The same attraction cannot be selected on both sides."
    />

    <div v-else-if="loading" class="empty-state">
      <div class="spinner" aria-hidden="true"></div>
      <span>Loading…</span>
    </div>

    <div v-else-if="!a || !b" class="alert alert-error">Could not load both attractions.</div>

    <section v-else class="stack fade-up">
      <section class="card summary">
        <div v-for="bar in summaryBars" :key="bar.key" class="sumrow">
          <header><span>{{ bar.label }}</span><span class="win" v-if="bar.winner">{{ attractionName(bar.winner === 'A' ? a : b) }} wins</span></header>
          <div class="bars">
            <div class="bar a" :style="{ width: bar.a + '%' }"><span>{{ bar.aText }}</span></div>
            <div class="bar b" :style="{ width: bar.b + '%' }"><span>{{ bar.bText }}</span></div>
          </div>
        </div>
      </section>

      <section class="card ctable">
        <div class="row ctable-head">
          <div class="cth attr">&nbsp;</div>
          <div class="cth col a"><strong>{{ attractionName(a) }}</strong><em>{{ formatPlace(a.city || a.region) }}</em></div>
          <div class="cth col b"><strong>{{ attractionName(b) }}</strong><em>{{ formatPlace(b.city || b.region) }}</em></div>
        </div>
        <div v-for="(row, i) in rows" :key="i" class="row ctable-row" :class="{ winA: row.winner === 'A', winB: row.winner === 'B' }">
          <div class="cth attr"><span class="ico">{{ row.icon }}</span><span>{{ row.label }}</span></div>
          <div class="cth col a" :class="{ winner: row.winner === 'A' }">
            <span v-if="row.type === 'stars'">
              <span class="stars">{{ starsFor(a.avg_rating) }}</span>
              <em>{{ Number(a.avg_rating).toFixed(2) }}</em>
            </span>
            <span v-else-if="row.type === 'image'">
              <img v-if="a.image_url" :src="a.image_url" :alt="a.name" />
              <span v-else class="no-img">🏛️</span>
            </span>
            <span v-else-if="row.type === 'pills'">
              <span v-if="a.is_featured" class="pill pill-brand">Featured</span>
              <span v-if="!a.is_featured" class="muted">—</span>
            </span>
            <span v-else-if="row.type === 'price'">
              <strong v-if="a.ticket_price">{{ a.ticket_price.toFixed(2) }} BYN</strong>
              <span v-else class="muted">Free</span>
            </span>
            <span v-else-if="row.type === 'number'" :class="{ 'big-num': true }">{{ row.render(a) }}</span>
            <span v-else>{{ row.render(a) || '—' }}</span>
            <span v-if="row.winner === 'A'" class="winner-mark" title="Better">★</span>
          </div>
          <div class="cth col b" :class="{ winner: row.winner === 'B' }">
            <span v-if="row.type === 'stars'">
              <span class="stars">{{ starsFor(b.avg_rating) }}</span>
              <em>{{ Number(b.avg_rating).toFixed(2) }}</em>
            </span>
            <span v-else-if="row.type === 'image'">
              <img v-if="b.image_url" :src="b.image_url" :alt="b.name" />
              <span v-else class="no-img">🏛️</span>
            </span>
            <span v-else-if="row.type === 'pills'">
              <span v-if="b.is_featured" class="pill pill-brand">Featured</span>
              <span v-if="!b.is_featured" class="muted">—</span>
            </span>
            <span v-else-if="row.type === 'price'">
              <strong v-if="b.ticket_price">{{ b.ticket_price.toFixed(2) }} BYN</strong>
              <span v-else class="muted">Free</span>
            </span>
            <span v-else-if="row.type === 'number'" class="big-num">{{ row.render(b) }}</span>
            <span v-else>{{ row.render(b) || '—' }}</span>
            <span v-if="row.winner === 'B'" class="winner-mark" title="Better">★</span>
          </div>
        </div>
      </section>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { attractionsAPI } from '@/api/client.js'
import { attractionName, formatCategory, formatPlace } from '@/utils/displayText.js'
import EmptyState from '../components/EmptyState.vue'

const all = ref([])
const idA = ref('')
const idB = ref('')
const a = ref(null)
const b = ref(null)
const loading = ref(false)

const optionsForB = computed(() => all.value.filter((x) => x.id !== Number(idB.value)))
const optionsForA = computed(() => all.value.filter((x) => x.id !== Number(idA.value)))

const starsFor = (r) => {
  const full = Math.round(r || 0)
  return '★'.repeat(full) + '☆'.repeat(5 - full)
}

const fetchAll = async () => {
  const res = await attractionsAPI.list({ per_page: 200 })
  all.value = res.data.attractions
}

const fetchOne = async (id) => {
  const res = await attractionsAPI.get(id)
  return res.data
}

const loadPair = async () => {
  if (!idA.value || !idB.value) { a.value = b.value = null; return }
  loading.value = true
  try {
    const [ra, rb] = await Promise.all([fetchOne(idA.value), fetchOne(idB.value)])
    a.value = ra; b.value = rb
  } finally { loading.value = false }
}

watch([idA, idB], loadPair)

const swap = () => { const t = idA.value; idA.value = idB.value; idB.value = t }
const rows = computed(() => {
  if (!a.value || !b.value) return []
  const A = a.value, B = b.value
  const higherWins = (av, bv) => (av ?? 0) > (bv ?? 0) ? 'A' : ((av ?? 0) < (bv ?? 0) ? 'B' : null)
  const lowerWins  = (av, bv) => (av ?? Infinity) < (bv ?? Infinity) ? 'A' : ((av ?? Infinity) > (bv ?? Infinity) ? 'B' : null)
  return [
    { label: 'Image', icon: '🖼️', type: 'image' },
    { label: 'City', icon: '🏙️', render: (x) => formatPlace(x.city) },
    { label: 'Region', icon: '🗺️', render: (x) => formatPlace(x.region) },
    { label: 'Category', icon: '🏷️', render: (x) => formatCategory(x.category) },
    { label: 'Rating', icon: '⭐', type: 'stars', winner: higherWins(A.avg_rating, B.avg_rating) },
    { label: 'Reviews', icon: '💬', type: 'number', render: (x) => (x.total_reviews || 0).toLocaleString('en-US'), winner: higherWins(A.total_reviews, B.total_reviews) },
    { label: 'Ticket price', icon: '🎟️', type: 'price', winner: lowerWins(A.ticket_price, B.ticket_price) },
    { label: 'Wishlists', icon: '♥', type: 'number', render: (x) => (x.wishlist_count || 0).toLocaleString('en-US'), winner: higherWins(A.wishlist_count, B.wishlist_count) },
    { label: 'Views', icon: '👁️', type: 'number', render: (x) => (x.view_count || 0).toLocaleString('en-US'), winner: higherWins(A.view_count, B.view_count) },
    { label: 'Sentiment', icon: '😊', render: (x) => (x.sentiment_score != null ? Number(x.sentiment_score).toFixed(2) : '—'), winner: higherWins(A.sentiment_score, B.sentiment_score) },
    { label: 'Best season', icon: '🌤️', render: (x) => x.suitable_season || '—' },
    { label: 'Opening hours', icon: '🕒', render: (x) => x.opening_hours || '—' },
    { label: 'Location', icon: '📍', render: (x) => formatPlace(x.location) },
    { label: 'Featured', icon: '🏅', type: 'pills' }
  ]
})
const summaryBars = computed(() => {
  if (!a.value || !b.value) return []
  const safe = (n) => (Number.isFinite(n) && n > 0 ? n : 0)
  const A = a.value, B = b.value
  const make = (label, av, bv, fmt) => {
    const total = safe(av) + safe(bv)
    if (total === 0) return { label, a: 50, b: 50, aText: '—', bText: '—', winner: null }
    const aPct = (av / total) * 100
    return {
      label, a: aPct, b: 100 - aPct,
      aText: fmt(av), bText: fmt(bv),
      winner: av === bv ? null : (av > bv ? 'A' : 'B')
    }
  }
  return [
    make('Rating', A.avg_rating, B.avg_rating, (n) => n.toFixed(2)),
    make('Reviews', safe(A.total_reviews), safe(B.total_reviews), (n) => Math.round(n).toLocaleString('en-US')),
    make('Popularity (views)', safe(A.view_count), safe(B.view_count), (n) => Math.round(n).toLocaleString('en-US'))
  ]
})

onMounted(fetchAll)
</script>

<style scoped>
.compare { display: flex; flex-direction: column; gap: 1.25rem; }

.pickers {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: .75rem;
  align-items: end;
  padding: 1rem 1.1rem;
}
.pickers label { display: block; margin-bottom: .35rem; }
.swap { height: 40px; align-self: end; }

.ctable { padding: 1rem 1.1rem; }
.ctable-head, .ctable-row {
  display: grid;
  grid-template-columns: 220px 1fr 1fr;
  gap: 1rem;
  padding: .65rem 0;
  align-items: center;
}
.ctable-head { border-bottom: 1px solid var(--border); padding-bottom: .8rem; }
.ctable-row + .ctable-row { border-top: 1px solid var(--border); }
.ctable-head .col { display: flex; flex-direction: column; }
.ctable-head .col em { font-style: normal; font-size: .78rem; color: var(--text-mute); }
.attr { display: flex; align-items: center; gap: .5rem; color: var(--text-soft); font-size: .88rem; font-weight: 600; }
.ico { font-size: 1rem; }

.col { font-size: .92rem; color: var(--text); }
.col .stars { color: var(--accent-500); letter-spacing: 1.2px; }
.col em { font-style: normal; color: var(--text-mute); margin-left: .35rem; font-size: .78rem; }
.col img { width: 100%; max-width: 240px; height: 120px; object-fit: cover; border-radius: var(--radius-sm); }
.col .no-img {
  width: 120px; height: 80px; border-radius: var(--radius-sm);
  display: inline-flex; align-items: center; justify-content: center;
  background: var(--brand-50); font-size: 1.6rem;
}
.col .big-num { font-weight: 700; font-size: 1.05rem; color: var(--brand-700); }
[data-theme='dark'] .col .big-num { color: var(--brand-300); }
.col .winner { background: var(--brand-50); border-radius: var(--radius-sm); padding: .35rem .55rem; }
[data-theme='dark'] .col .winner { background: rgba(20,184,147,.18); }
.winner-mark { color: var(--accent-500); margin-left: .4rem; }
.muted { color: var(--text-mute); }

.summary { padding: 1rem 1.1rem; display: flex; flex-direction: column; gap: .8rem; }
.sumrow header {
  display: flex; justify-content: space-between; align-items: baseline;
  font-size: .82rem; color: var(--text-soft); margin-bottom: .3rem;
}
.sumrow .win { color: var(--brand-700); font-weight: 600; font-size: .8rem; }
[data-theme='dark'] .sumrow .win { color: var(--brand-300); }
.bars { display: flex; height: 22px; border-radius: var(--radius-pill); overflow: hidden; background: var(--surface-2); }
.bars .bar {
  display: flex; align-items: center; justify-content: center;
  color: #fff; font-size: .74rem; font-weight: 700;
  min-width: 2px; padding: 0 .5rem;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.bars .bar.a { background: var(--grad-brand); }
.bars .bar.b { background: linear-gradient(135deg, #94a3b8, #475569); }
.bars .bar span { display: inline-block; }

.spinner { width: 30px; height: 30px; border: 3px solid var(--border); border-top-color: var(--brand-500); border-radius: 50%; animation: spin .8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 720px) {
  .pickers { grid-template-columns: 1fr; }
  .swap { width: 100%; }
  .ctable-head, .ctable-row { grid-template-columns: 1fr; }
  .ctable-row { padding: .85rem 0; }
  .attr { padding-bottom: .35rem; }
  .col img { max-width: 100%; }
}
</style>
