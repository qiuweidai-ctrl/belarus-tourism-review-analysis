<template>
  <div class="mp">
    <header class="page-head">
      <div>
        <h1 class="page-title">Map</h1>
        <p class="page-sub">Every attraction we have coordinates for. Click a card on the right to fly there.</p>
      </div>
      <div class="row head-actions">
        <input v-model="search" type="search" placeholder="Filter by name…" class="search" />
        <select v-model="category" class="select">
          <option value="">All categories</option>
          <option v-for="c in categories" :key="c" :value="c">{{ c[0].toUpperCase() + c.slice(1) }}</option>
        </select>
        <div class="seg" role="tablist" aria-label="View mode">
          <button class="seg-btn" :class="{ on: mode === 'markers' }" @click="mode = 'markers'">Markers</button>
          <button class="seg-btn" :class="{ on: mode === 'heat' }" @click="mode = 'heat'">Heatmap</button>
        </div>
      </div>
    </header>

    <section v-if="mapped.length" class="grid grid-4 stats fade-up">
      <StatCard label="Mapped" :value="mapped.length" icon="📍" color="var(--brand-600)" />
      <StatCard label="Total" :value="all.length" icon="🏛️" color="var(--info)" />
      <StatCard label="Cities" :value="cities.length" icon="🏙️" color="var(--accent-600)" />
      <StatCard label="Average rating" :value="avgRating" :decimals="2" icon="⭐" color="var(--success)" suffix=" / 5" />
    </section>

    <div class="map-wrap card">
      <div ref="mapEl" class="map"></div>
      <aside class="sidepanel">
        <div class="section-head">
          <h2>{{ mapped.length }} of {{ all.length }} shown</h2>
          <p class="sub">Click a card to focus the map.</p>
        </div>
        <div v-if="loading" class="empty-state"><div class="spinner"></div><span>Loading…</span></div>
        <div v-else-if="mapped.length === 0" class="empty-state">No markers for that filter.</div>
        <ul v-else class="cards">
          <li
            v-for="a in mapped"
            :key="a.id"
            class="mini"
            :class="{ active: activeId === a.id }"
            @click="focus(a)"
          >
            <div class="thumb" :style="imgStyle(a)"><span v-if="!a.image_url" class="ph">🏛️</span></div>
            <div class="meta">
              <strong>{{ a.name }}</strong>
              <em>{{ a.city || a.region || '—' }} · {{ cap(a.category) }}</em>
              <span class="r"><span class="stars">{{ stars(a.avg_rating) }}</span> {{ Number(a.avg_rating || 0).toFixed(1) }}</span>
            </div>
          </li>
        </ul>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { attractionsAPI } from '@/api/client.js'
import StatCard from '../components/StatCard.vue'

const all = ref([])
const categories = ref([])
const search = ref('')
const category = ref('')
const mode = ref('markers')
const activeId = ref(null)
const loading = ref(true)

const mapEl = ref(null)
let map = null
let markerLayer = null
let heatLayer = null
let tileLayer = null

const isDark = ref(document.documentElement.getAttribute('data-theme') === 'dark')

const stars = (r) => {
  const full = Math.round(r || 0)
  return '★'.repeat(full) + '☆'.repeat(5 - full)
}
const cap = (s) => s ? s.charAt(0).toUpperCase() + s.slice(1) : '—'
const imgStyle = (a) => a.image_url
  ? { backgroundImage: `url(${a.image_url})` }
  : { background: 'var(--grad-brand)' }

const palette = ['#0c7663', '#0d9478', '#14b893', '#34d3ac', '#f59e0b', '#3b82f6', '#8b5cf6', '#ec4899']

const mapped = computed(() => {
  const q = search.value.trim().toLowerCase()
  return all.value.filter((a) => {
    if (a.latitude == null || a.longitude == null) return false
    if (category.value && a.category !== category.value) return false
    if (q && !a.name.toLowerCase().includes(q)) return false
    return true
  })
})
const cities = computed(() => [...new Set(mapped.value.map((a) => a.city).filter(Boolean))])
const avgRating = computed(() => {
  if (!mapped.value.length) return 0
  return mapped.value.reduce((s, a) => s + (a.avg_rating || 0), 0) / mapped.value.length
})

const tileUrl = () => isDark.value
  ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
  : 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
const tileAttr = () => isDark.value
  ? '&copy; OpenStreetMap contributors &copy; CARTO'
  : '&copy; OpenStreetMap contributors'

const drawMarkers = () => {
  if (!map) return
  if (markerLayer) { markerLayer.clearLayers(); map.removeLayer(markerLayer) }
  if (heatLayer)   { map.removeLayer(heatLayer); heatLayer = null }
  if (mode.value !== 'markers') return
  markerLayer = L.layerGroup().addTo(map)
  mapped.value.forEach((a, i) => {
    const color = palette[i % palette.length]
    const dot = L.circleMarker([a.latitude, a.longitude], {
      radius: 7,
      fillColor: color, color: '#fff', weight: 2, opacity: 1, fillOpacity: .9
    })
    dot.bindTooltip(a.name, { direction: 'top', offset: [0, -6] })
    dot.bindPopup(`<strong>${a.name}</strong><br/>${a.city || a.region || ''}<br/>${Number(a.avg_rating || 0).toFixed(2)} / 5`)
    dot.on('click', () => { activeId.value = a.id })
    markerLayer.addLayer(dot)
  })
}

const drawHeat = () => {
  if (!map) return
  if (markerLayer) { markerLayer.clearLayers(); map.removeLayer(markerLayer); markerLayer = null }
  if (heatLayer)   { map.removeLayer(heatLayer); heatLayer = null }
  if (mode.value !== 'heat') return
  heatLayer = L.layerGroup().addTo(map)
  mapped.value.forEach((a) => {
    const r = Number(a.avg_rating || 0)
    const radius = 8 + (r / 5) * 28
    const dot = L.circleMarker([a.latitude, a.longitude], {
      radius,
      stroke: false,
      fillColor: '#0d9478',
      fillOpacity: Math.max(0.18, Math.min(0.55, r / 9))
    })
    dot.bindTooltip(`${a.name} · ${r.toFixed(1)}`, { direction: 'top' })
    dot.on('click', () => { activeId.value = a.id })
    heatLayer.addLayer(dot)
  })
}

const applyTiles = () => {
  if (!map) return
  if (tileLayer) map.removeLayer(tileLayer)
  tileLayer = L.tileLayer(tileUrl(), {
    subdomains: 'abc',
    maxZoom: 19,
    attribution: tileAttr()
  }).addTo(map)
}

const render = () => {
  if (!map) return
  if (mode.value === 'markers') drawMarkers(); else drawHeat()
  if (mapped.value.length) {
    const bounds = L.latLngBounds(mapped.value.map((a) => [a.latitude, a.longitude]))
    map.fitBounds(bounds.pad(0.15), { animate: true })
  }
}

const focus = (a) => {
  activeId.value = a.id
  if (!map) return
  map.setView([a.latitude, a.longitude], Math.max(map.getZoom(), 11), { animate: true })
}

const initMap = async () => {
  await nextTick()
  if (!mapEl.value) return
  map = L.map(mapEl.value, { zoomControl: true }).setView([53.9, 27.6], 7)
  applyTiles()
  setTimeout(() => { if (map) map.invalidateSize() }, 200)
}

const onThemeChanged = (e) => {
  isDark.value = e.detail === 'dark' || document.documentElement.getAttribute('data-theme') === 'dark'
  applyTiles()
}

const fetch = async () => {
  loading.value = true
  try {
    const [list, cats] = await Promise.all([
      attractionsAPI.list({ per_page: 200 }),
      attractionsAPI.categories()
    ])
    all.value = list.data.attractions
    categories.value = cats.data.categories || []
  } finally {
    loading.value = false
  }
}

watch([mapped, mode], render)

onMounted(async () => {
  await fetch()
  await initMap()
  render()
  window.addEventListener('app:theme-changed', onThemeChanged)
})

onBeforeUnmount(() => {
  window.removeEventListener('app:theme-changed', onThemeChanged)
  if (map) { map.remove(); map = null }
})
</script>

<style scoped>
.mp { display: flex; flex-direction: column; gap: 1.25rem; }
.page-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }
.head-actions { gap: .5rem; flex-wrap: wrap; }
.search, .select {
  background: var(--surface); color: var(--text);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-sm);
  padding: .42rem .7rem; font: inherit; font-size: .85rem;
}
.search { width: 220px; }
.select { width: auto; }

.seg { display: inline-flex; background: var(--surface-2); border: 1px solid var(--border); border-radius: var(--radius-pill); padding: 2px; }
.seg-btn { border: none; background: none; cursor: pointer; font: inherit; font-size: .82rem; font-weight: 600; color: var(--text-soft); padding: .3rem .75rem; border-radius: var(--radius-pill); }
.seg-btn:hover { color: var(--text); }
.seg-btn.on { background: var(--grad-brand); color: #fff; box-shadow: var(--shadow-xs); }

.map-wrap {
  padding: 0; overflow: hidden;
  display: grid;
  grid-template-columns: 1fr 320px;
  min-height: 560px;
  height: 60vh;
  max-height: 720px;
}
.map { width: 100%; height: 100%; }
.sidepanel {
  border-left: 1px solid var(--border);
  background: var(--surface-2);
  display: flex; flex-direction: column; min-height: 0;
}
.sidepanel .section-head { padding: .8rem 1rem 0; }

.cards { list-style: none; margin: 0; padding: .4rem .5rem .8rem; overflow-y: auto; flex: 1 1 auto; display: flex; flex-direction: column; gap: .25rem; }
.mini {
  display: flex; align-items: center; gap: .55rem;
  padding: .35rem; border-radius: var(--radius-sm); cursor: pointer;
  transition: background-color var(--speed) var(--ease);
}
.mini:hover { background: var(--surface-hover); }
.mini.active { background: var(--brand-50); }
[data-theme='dark'] .mini.active { background: rgba(20,184,147,.18); }
.thumb { width: 38px; height: 38px; border-radius: var(--radius-sm); background-size: cover; background-position: center; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.thumb .ph { font-size: 1.1rem; opacity: .6; }
.meta { display: flex; flex-direction: column; min-width: 0; }
.meta strong { font-size: .85rem; font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.meta em { font-style: normal; font-size: .72rem; color: var(--text-mute); }
.meta .r { font-size: .76rem; color: var(--text-soft); }
.meta .r .stars { color: var(--accent-500); }

.spinner { width: 30px; height: 30px; border: 3px solid var(--border); border-top-color: var(--brand-500); border-radius: 50%; animation: spin .8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 880px) {
  .map-wrap { grid-template-columns: 1fr; }
  .sidepanel { border-left: none; border-top: 1px solid var(--border); max-height: 260px; }
  .search { width: 100%; }
}
</style>
