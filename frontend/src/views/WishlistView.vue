<template>
  <div class="wish">
    <header class="page-head">
      <div>
        <h1 class="page-title">My Wishlist</h1>
        <p class="page-sub">Every attraction you saved, with quick actions for trip planning.</p>
      </div>
      <div class="row head-actions">
        <select v-model="sort" class="sort">
          <option value="recent">Recently added</option>
          <option value="rating">Highest rated</option>
          <option value="priceLow">Price · low to high</option>
          <option value="priceHigh">Price · high to low</option>
        </select>
      </div>
    </header>

    <EmptyState
      v-if="!isLoggedIn"
      icon="🔒"
      title="Sign in to view your wishlist"
      hint="Your saved attractions live behind your account so you can access them from any device."
    >
      <router-link to="/login" class="btn btn-primary" style="margin-top: .7rem">Go to login</router-link>
    </EmptyState>

    <template v-else>
      <section v-if="items.length" class="grid grid-4 stats fade-up">
        <StatCard label="Saved" :value="items.length" icon="♥" color="var(--danger)" />
        <StatCard v-if="allPricesKnown" label="Estimated total" :value="totalPrice" :decimals="2" icon="🎟️" color="var(--brand-600)" suffix=" BYN" />
        <StatCard label="Average rating" :value="avgRating" :decimals="2" icon="⭐" color="var(--accent-600)" suffix=" / 5" />
        <StatCard label="Visited" :value="visitedCount" icon="✅" color="var(--success)" />
      </section>

      <div v-if="error" class="alert alert-error">{{ error }}</div>

      <div v-if="loading" class="grid grid-3">
        <div v-for="i in 6" :key="i" class="skeleton sk-card"></div>
      </div>

      <EmptyState
        v-else-if="items.length === 0"
        icon="💔"
        title="No saved attractions yet"
        hint="Browse the catalog and tap the heart on anything you want to come back to."
      >
        <router-link to="/attractions" class="btn btn-primary" style="margin-top: .7rem">Browse attractions</router-link>
      </EmptyState>

      <section v-else class="grid grid-3 fade-up">
        <article v-for="w in pageItems" :key="w.attraction_id || w.id" class="card card-hover wcard">
          <div class="wimg">
            <img v-if="w.image_url" class="thumbnail-image" :src="w.thumbnail_url || w.image_url" :alt="w.name" loading="lazy" decoding="async" />
            <span v-if="w.is_featured" class="badge">★ Featured</span>
            <span v-if="w.visited" class="badge visited">✓ Visited</span>
          </div>
          <div class="wbody">
            <h3>{{ w.name }}</h3>
            <p class="loc">{{ w.city || w.region || '—' }}</p>
            <p class="rate">
              <strong>{{ formatExternalRating(w) }}</strong>
              <ExternalRatingSource :attraction="w" :show-score="false" />
            </p>
            <p v-if="w.note" class="note">"{{ w.note }}"</p>
            <div class="row foot">
              <span class="pill">{{ cap(w.category) }}</span>
              <span class="spacer"></span>
              <span v-if="w.ticket_price != null" class="price" :class="{ free: w.ticket_price === 0 }">
                {{ priceLabel(w.ticket_price) }}
              </span>
            </div>
            <div class="row actions">
              <label class="prio">
                <span>Priority</span>
                <select :value="w.priority" @change="setPriority(w, $event.target.value)">
                  <option v-for="n in 5" :key="n" :value="n">{{ '★'.repeat(n) }}</option>
                </select>
              </label>
              <span class="spacer"></span>
              <router-link :to="'/attractions/' + (w.attraction_id || w.id)" class="btn btn-ghost btn-sm">View</router-link>
              <button class="btn btn-soft btn-sm" type="button" @click="toggleVisited(w)">{{ w.visited ? 'Unmark' : 'Mark visited' }}</button>
              <button class="btn btn-soft btn-sm" type="button" @click="remove(w)" title="Remove from wishlist">✕</button>
            </div>
          </div>
        </article>
      </section>

      <nav v-if="totalPages > 1" class="pager" aria-label="Pagination">
        <button class="btn btn-ghost btn-sm" :disabled="page === 1" @click="page--">← Previous</button>
        <span class="page-info">Page {{ page }} of {{ totalPages }}</span>
        <button class="btn btn-ghost btn-sm" :disabled="page === totalPages" @click="page++">Next →</button>
      </nav>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { wishlistAPI } from '@/api/client.js'
import StatCard from '../components/StatCard.vue'
import EmptyState from '../components/EmptyState.vue'
import ExternalRatingSource from '../components/ExternalRatingSource.vue'
import { externalProvider, externalReviewCount, externalScore, formatExternalRating } from '@/utils/ratings.js'

const items = ref([])
const loading = ref(false)
const error = ref('')
const sort = ref('recent')
const page = ref(1)
const perPage = 24

const isLoggedIn = ref(!!localStorage.getItem('token'))

// 先按选中的方式排序，再截取当前页。
const sorted = computed(() => {
  const list = [...items.value]
  switch (sort.value) {
    case 'rating': return list.sort((a, b) => (externalScore(b) || 0) - (externalScore(a) || 0))
    case 'priceLow': return list.sort((a, b) => (a.ticket_price || Infinity) - (b.ticket_price || Infinity))
    case 'priceHigh': return list.sort((a, b) => (b.ticket_price || -1) - (a.ticket_price || -1))
    default: return list
  }
})
const totalPages = computed(() => Math.max(1, Math.ceil(sorted.value.length / perPage)))
const pageItems = computed(() => {
  const start = (page.value - 1) * perPage
  return sorted.value.slice(start, start + perPage)
})
const totalPrice = computed(() => items.value.reduce((s, w) => s + (w.ticket_price || 0), 0).toFixed(2))
const allPricesKnown = computed(() => items.value.every((w) => w.ticket_price != null))
const avgRating = computed(() => {
  if (!items.value.length) return 0
  return (items.value.reduce((s, w) => s + (externalScore(w) || 0), 0) / items.value.length)
})
const visitedCount = computed(() => items.value.filter((w) => w.visited).length)

const cap = (s) => s ? s.charAt(0).toUpperCase() + s.slice(1) : '—'
const priceLabel = (price) => price === 0 ? 'Free' : `${price.toFixed(2)} BYN`
const load = async () => {
  if (!isLoggedIn.value) return
  loading.value = true; error.value = ''
  try {
    const saved = await wishlistAPI.all()
    items.value = saved.map((w) => ({ ...w, attraction_id: w.attraction_id || w.id }))
  } catch (e) {
    if (e.response && e.response.status === 401) { isLoggedIn.value = false; return }
    error.value = 'Could not load your wishlist.'
  } finally { loading.value = false }
}

const remove = async (w) => {
  try {
    await wishlistAPI.remove(w.attraction_id || w.id)
    items.value = items.value.filter((x) => (x.attraction_id || x.id) !== (w.attraction_id || w.id))
  } catch (e) { error.value = 'Could not remove that item.' }
}

const setPriority = async (w, p) => {
  w.priority = Number(p)
}

const toggleVisited = async (w) => {
  w.visited = !w.visited
}

watch(sort, () => { page.value = 1 })

onMounted(load)
</script>

<style scoped>
.wish { display: flex; flex-direction: column; gap: 1.25rem; }
.page-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }
.sort { background: var(--surface); color: var(--text); border: 1px solid var(--border-strong); border-radius: var(--radius-sm); padding: .38rem .7rem; font-size: .85rem; width: auto; }

.stats { gap: 1rem; }
.sk-card { height: 280px; border-radius: var(--radius); }

.wcard { padding: 0; overflow: hidden; display: flex; flex-direction: column; }
.wimg { height: 150px; background-size: cover; background-position: center; position: relative; }
.badge { position: absolute; top: 8px; left: 8px; padding: .18rem .5rem; border-radius: var(--radius-pill); background: rgba(255,255,255,.95); color: var(--brand-700); font-size: .7rem; font-weight: 700; }
.badge.visited { background: rgba(16,185,129,.95); color: #fff; left: auto; right: 8px; }

.wbody { padding: .85rem 1rem 1rem; display: flex; flex-direction: column; gap: .35rem; flex: 1 1 auto; }
.wbody h3 { margin: 0; font-size: 1rem; }
.wbody .loc { margin: 0; font-size: .78rem; color: var(--text-mute); }
.wbody .rate { margin: .2rem 0 .4rem; display: flex; align-items: center; gap: .35rem; flex-wrap: wrap; font-size: .85rem; }
.wbody .stars { color: var(--accent-500); }
.wbody .rate strong { color: var(--accent-600); }
.wbody .rate em { font-style: normal; color: var(--text-mute); font-size: .76rem; }
.wbody .note { margin: 0 0 .4rem; color: var(--text-soft); font-size: .82rem; font-style: italic; }
.foot .price { font-weight: 700; color: var(--accent-600); font-size: .85rem; }
.foot .price.free { color: var(--success); }

.actions { gap: .4rem; margin-top: .55rem; }
.prio { display: inline-flex; align-items: center; gap: .35rem; font-size: .78rem; color: var(--text-soft); }
.prio select { width: auto; padding: .25rem .5rem; font-size: .82rem; }

.pager { display: flex; align-items: center; justify-content: center; gap: .8rem; margin-top: .5rem; }
.page-info { color: var(--text-mute); font-size: .88rem; }
</style>
