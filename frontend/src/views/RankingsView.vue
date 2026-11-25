<template>
  <div class="rankings">
    <header class="page-head">
      <div>
        <h1 class="page-title">Rankings</h1>
        <p class="page-sub">Visitor scores from external platforms. Rating order adjusts for rating count; displayed scores remain the platform scores.</p>
      </div>
      <div class="row head-actions">
        <div class="seg" role="tablist" aria-label="Ranking metric">
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
        <select v-model="sortName" class="sort">
          <option value="">Default order</option>
          <option value="asc">Name A → Z</option>
          <option value="desc">Name Z → A</option>
        </select>
      </div>
    </header>

    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <section v-if="loading" class="podium">
      <div v-for="i in 3" :key="i" class="pcard skeleton sk-pod" :class="'p' + i"></div>
    </section>

    <section v-else-if="top.length >= 3" class="podium">
      <div
        v-for="(a, i) in top.slice(0, 3)"
        :key="a.id"
        class="pcard card card-hover"
        :class="'p' + (i + 1)"
        @click="$router.push('/attractions/' + a.id)"
      >
        <span class="medal" :class="'m' + (i + 1)">{{ i + 1 }}</span>
        <div class="pimg">
          <img v-if="a.image_url" class="thumbnail-image" :src="a.thumbnail_url || a.image_url" :alt="a.name" decoding="async" />
          <span v-else class="ph">🏛️</span>
        </div>
        <h3 :title="a.name">{{ a.name }}</h3>
        <p class="ploc" :title="a.city || a.region">{{ a.city || a.region || '—' }}</p>
        <p class="pval">{{ format(a) }}</p>
        <ExternalRatingSource :attraction="a" :show-score="metric !== 'rating'" :show-count="metric !== 'reviews'" />
        <p v-if="metric === 'reviews'" class="ploc">reviews stored on this site</p>
        <div class="podium-step" aria-hidden="true">{{ i + 1 }}</div>
      </div>
    </section>

    <section v-if="!loading && sortedRest.length" class="card list-card">
      <div class="section-head">
        <h2>The rest</h2>
        <p class="sub">Positions 4 to {{ top.length }}</p>
      </div>
      <ol class="list">
        <li
          v-for="(a, i) in sortedRest"
          :key="a.id"
          class="row-entry"
          @click="$router.push('/attractions/' + a.id)"
        >
          <span class="rank">{{ i + 4 }}</span>
          <div class="thumb"><img v-if="a.image_url" class="thumbnail-image" :src="a.thumbnail_url || a.image_url" :alt="a.name" loading="lazy" decoding="async" /><span v-else class="ph">🏛️</span></div>
          <div class="meta">
            <strong>{{ a.name }}</strong>
            <em>{{ a.city || a.region || '—' }}<span v-if="a.category" class="dot">·</span>{{ cap(a.category) }}</em>
            <ExternalRatingSource :attraction="a" :show-score="metric !== 'rating'" :show-count="metric !== 'reviews'" />
            <em v-if="metric === 'reviews'">reviews stored on this site</em>
          </div>
          <span class="val">{{ format(a) }}</span>
        </li>
      </ol>
    </section>

    <EmptyState v-if="!loading && top.length === 0" icon="🏆" title="No attractions to rank" hint="Try switching the metric." />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { analyticsAPI } from '@/api/client.js'
import EmptyState from '../components/EmptyState.vue'
import ExternalRatingSource from '../components/ExternalRatingSource.vue'
import { storedReviewCount, formatExternalRating } from '@/utils/ratings.js'

const metric = ref('rating')
const sortName = ref('')
const top = ref([])
const loading = ref(true)
const error = ref('')

const metrics = [
  { key: 'rating', label: 'External rating' },
  { key: 'reviews', label: 'Stored reviews' },
  { key: 'views', label: 'Views' },
  { key: 'wishlist', label: 'Saves' }
]

const formatters = {
  rating: (a) => formatExternalRating(a),
  reviews: (a) => storedReviewCount(a).toLocaleString('en-US'),
  views: (a) => (a.view_count || 0).toLocaleString('en-US'),
  wishlist: (a) => (a.wishlist_count || 0).toLocaleString('en-US')
}
const format = (a) => formatters[metric.value](a)
const cap = (s) => s ? s.charAt(0).toUpperCase() + s.slice(1) : '—'

const sortedRest = computed(() => {
  if (!sortName.value) return top.value.slice(3)
  const list = [...top.value.slice(3)]
  list.sort((x, y) => sortName.value === 'asc'
    ? x.name.localeCompare(y.name)
    : y.name.localeCompare(x.name))
  return list
})

const load = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await analyticsAPI.topAttractions({ metric: metric.value, limit: 20 })
    top.value = res.data.items || []
  } catch (e) {
    error.value = 'Could not load rankings. Is the API running?'
  } finally { loading.value = false }
}

// 切换榜单指标时重新请求排名。
watch(metric, load)
onMounted(load)
</script>

<style scoped>
.rankings { display: flex; flex-direction: column; gap: 1.25rem; }
.page-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }
.head-actions { gap: .5rem; }

.sort {
  background: var(--surface);
  color: var(--text);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-sm);
  padding: .38rem .7rem;
  font-size: .85rem;
  width: auto;
}

.seg { display: inline-flex; background: var(--surface-2); border: 1px solid var(--border); border-radius: var(--radius-pill); padding: 2px; }
.seg-btn { border: none; background: none; cursor: pointer; font: inherit; font-size: .82rem; font-weight: 600; color: var(--text-soft); padding: .3rem .75rem; border-radius: var(--radius-pill); transition: background-color var(--speed) var(--ease), color var(--speed) var(--ease); }
.seg-btn:hover { color: var(--text); }
.seg-btn.on { background: var(--grad-brand); color: #fff; box-shadow: var(--shadow-xs); }

.podium {
  display: grid;
  grid-template-columns: 1fr 1.15fr 1fr;
  grid-template-areas: "second first third";
  align-items: end;
  gap: 1rem;
  padding-top: 1.5rem;
}
.pcard.p1 { grid-area: first; --podium-height: 460px; --photo-height: 160px; }
.pcard.p2 { grid-area: second; --podium-height: 410px; --photo-height: 140px; }
.pcard.p3 { grid-area: third; --podium-height: 370px; --photo-height: 120px; }
.pcard {
  position: relative; padding: 1.5rem 1.1rem 0; cursor: pointer;
  height: var(--podium-height); min-width: 0;
  text-align: center;
  display: flex; flex-direction: column; align-items: center; gap: .35rem;
  border: 1px solid var(--border);
}
.pcard.p1 {
  background: linear-gradient(135deg, var(--brand-50), var(--surface));
  border: 2px solid var(--brand-300);
  box-shadow: var(--shadow-lg);
}
[data-theme='dark'] .pcard.p1 { background: linear-gradient(135deg, rgba(20,184,147,.2), var(--surface)); }

.pimg {
  width: 100%; max-width: 240px; height: var(--photo-height); flex-shrink: 0;
  background-size: cover; background-position: center;
  border-radius: var(--radius); margin-bottom: .4rem;
  display: flex; align-items: center; justify-content: center;
}
.pcard.p1 .pimg { max-width: 280px; }
.ph { font-size: 3rem; opacity: .6; }

.medal {
  position: absolute; top: -10px; left: 50%; transform: translateX(-50%);
  width: 32px; height: 32px; border-radius: 50%;
  display: inline-flex; align-items: center; justify-content: center;
  font-weight: 800; font-size: .9rem; color: #fff;
  box-shadow: var(--shadow-sm);
}
.pcard.p1 .medal { width: 44px; height: 44px; font-size: 1.1rem; top: -16px; }
.medal.m1 { background: linear-gradient(135deg, #fbbf24, #f59e0b); }
.medal.m2 { background: linear-gradient(135deg, #cbd5e1, #64748b); }
.medal.m3 { background: linear-gradient(135deg, #fdba74, #c2410c); }

.pcard h3 {
  font-size: 1rem; margin: .2rem 0 0; line-height: 1.3; width: 100%;
  display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 3;
  max-height: 3.9em; overflow: hidden; overflow-wrap: anywhere; flex-shrink: 0;
}
.pcard.p1 h3 { font-size: 1.18rem; }
.ploc { color: var(--text-mute); font-size: .8rem; margin: 0; width: 100%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; flex-shrink: 0; }
.pval { color: var(--brand-700); font-weight: 800; font-size: 1rem; margin: .25rem 0 0; flex-shrink: 0; }
[data-theme='dark'] .pval { color: var(--brand-300); }
.pcard.p1 .pval { font-size: 1.2rem; }

.pcard :deep(.external-rating-source) { flex-shrink: 0; max-width: 100%; }
.podium-step {
  align-self: stretch; flex-shrink: 0; margin: auto -1.1rem 0;
  padding: .5rem; border-top: 1px solid var(--border);
  border-radius: 0 0 var(--radius) var(--radius);
  font-size: 1.35rem; font-weight: 900; line-height: 1.25;
}
.p1 .podium-step { color: #854d0e; background: linear-gradient(135deg, #fef3c7, #fbbf24); }
.p2 .podium-step { color: #334155; background: linear-gradient(135deg, #f1f5f9, #cbd5e1); }
.p3 .podium-step { color: #7c2d12; background: linear-gradient(135deg, #ffedd5, #fdba74); }

.list-card { padding: 1rem 1.1rem; }
.list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: .25rem; }
.row-entry {
  display: flex; align-items: center; gap: .7rem;
  padding: .5rem .55rem; border-radius: var(--radius-sm); cursor: pointer;
  transition: background-color var(--speed) var(--ease);
}
.row-entry:hover { background: var(--surface-hover); }
.rank { width: 32px; text-align: center; font-weight: 700; color: var(--text-soft); font-size: .92rem; }
.thumb { width: 48px; height: 48px; border-radius: var(--radius-sm); background-size: cover; background-position: center; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.thumb .ph { font-size: 1.3rem; opacity: .6; }
.meta { flex: 1 1 auto; min-width: 0; display: flex; flex-direction: column; }
.meta strong { font-size: .92rem; font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.meta em { font-style: normal; font-size: .76rem; color: var(--text-mute); }
.meta .dot { margin: 0 .35rem; }
.val { font-weight: 700; color: var(--brand-700); font-size: .92rem; }
[data-theme='dark'] .val { color: var(--brand-300); }

@media (max-width: 720px) {
  .podium { grid-template-columns: 1fr; grid-template-areas: "first" "second" "third"; }
  .pcard { height: auto; min-height: 330px; }
  .pcard.p1 { padding: 1.5rem 1.1rem 0; }
  .pcard h3 { display: block; max-height: none; overflow: visible; }
  .podium-step { margin-top: .75rem; }
  .pcard.p1 .medal { top: -10px; }
}
</style>
