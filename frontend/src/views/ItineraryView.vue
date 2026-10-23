<template>
  <div class="itin">
    <header class="page-head no-print">
      <div>
        <h1 class="page-title">Trip Itinerary</h1>
        <p class="page-sub">Plan your day by day. Everything saves to this browser, so closing the tab will not lose it.</p>
      </div>
      <div class="row head-actions">
        <button class="btn btn-ghost btn-sm" type="button" @click="downloadText" :disabled="!days.length">Download as text</button>
        <button class="btn btn-ghost btn-sm" type="button" @click="print" :disabled="!days.length">Print / Save PDF</button>
      </div>
    </header>

    <section v-if="days.length" class="grid grid-4 stats fade-up no-print">
      <StatCard label="Days" :value="days.length" icon="📆" color="var(--brand-600)" />
      <StatCard label="Stops" :value="totalStops" icon="📍" color="var(--info)" />
      <StatCard label="Estimated total" :value="totalCost" :decimals="2" icon="🎟️" color="var(--accent-600)" suffix=" BYN" />
      <StatCard label="Average rating" :value="avgRating" :decimals="2" icon="⭐" color="var(--success)" suffix=" / 5" />
    </section>

    <div class="trip-meta no-print">
      <label>
        <span>Trip name</span>
        <input v-model="tripName" placeholder="Belarus summer 2026" />
      </label>
    </div>

    <EmptyState
      v-if="!days.length"
      icon="🧳"
      title="Start by adding a day"
      hint="Each day is a list of stops with notes. You can add as many days as you like and reorder them however you want."
    >
      <button class="btn btn-primary" type="button" @click="addDay" style="margin-top: .7rem">+ Add the first day</button>
    </EmptyState>

    <section v-else class="days fade-up" :class="{ printable: printing }">
      <article v-for="(d, di) in days" :key="d.id" class="day card">
        <header class="day-head no-print">
          <input class="dtitle" v-model="d.title" :aria-label="'Day ' + (di + 1) + ' title'" />
          <span class="dsub">
            {{ d.items.length }} stop{{ d.items.length === 1 ? '' : 's' }}
            <template v-if="dayCost(d) > 0">· {{ dayCost(d).toFixed(2) }} BYN</template>
          </span>
          <span class="spacer"></span>
          <button class="btn btn-ghost btn-sm" type="button" :disabled="di === 0" @click="moveDay(di, -1)" title="Move up">↑</button>
          <button class="btn btn-ghost btn-sm" type="button" :disabled="di === days.length - 1" @click="moveDay(di, 1)" title="Move down">↓</button>
          <button class="btn btn-soft btn-sm" type="button" @click="removeDay(di)">Remove day</button>
        </header>

        <header class="day-head printable">
          <h2>{{ d.title || ('Day ' + (di + 1)) }}</h2>
          <span>{{ d.items.length }} stop{{ d.items.length === 1 ? '' : 's' }}</span>
        </header>

        <ul
          v-if="d.items.length"
          class="stops"
          @dragover.prevent
          @drop="onDrop($event, di, -1)"
        >
          <li
            v-for="(stop, si) in d.items"
            :key="stop.attraction.id"
            class="stop"
            :draggable="true"
            @dragstart="onDragStart($event, di, si)"
            @dragover.prevent
            @drop.stop="onDrop($event, di, si)"
          >
            <span class="handle no-print" title="Drag to reorder">⋮⋮</span>
            <span class="num">{{ si + 1 }}</span>
            <div class="thumb" :style="imgStyle(stop.attraction)"><span v-if="!stop.attraction.image_url" class="ph">🏛️</span></div>
            <div class="stop-meta">
              <strong>{{ stop.attraction.name }}</strong>
              <em>{{ stop.attraction.city || stop.attraction.region || '—' }} · {{ Number(stop.attraction.avg_rating || 0).toFixed(1) }} ★</em>
            </div>
            <input class="note no-print" v-model="stop.note" placeholder="Note (optional)" />
            <span class="stop-price">{{ stop.attraction.ticket_price ? stop.attraction.ticket_price.toFixed(2) + ' BYN' : 'Free' }}</span>
            <div class="row stop-actions no-print">
              <button class="btn btn-ghost btn-sm" type="button" :disabled="si === 0" @click="moveStop(di, si, -1)">↑</button>
              <button class="btn btn-ghost btn-sm" type="button" :disabled="si === d.items.length - 1" @click="moveStop(di, si, 1)">↓</button>
              <router-link :to="'/attractions/' + stop.attraction.id" class="btn btn-ghost btn-sm">View</router-link>
              <button class="btn btn-soft btn-sm" type="button" @click="removeStop(di, si)">Remove</button>
            </div>
          </li>
        </ul>
        <p v-else class="empty-day">No stops yet for this day.</p>

        <div class="day-foot no-print">
          <button class="btn btn-soft btn-sm" type="button" @click="openPicker(di)">+ Add a stop</button>
        </div>
      </article>
    </section>

    <div v-if="days.length" class="add-day-bar no-print">
      <button class="btn btn-primary" type="button" @click="addDay">+ Add another day</button>
    </div>

    <div v-if="pickerDay != null" class="picker-overlay" @click.self="closePicker">
      <div class="picker card">
        <header class="section-head">
          <div>
            <h2>Add a stop to {{ days[pickerDay].title || ('Day ' + (pickerDay + 1)) }}</h2>
            <p class="sub">Search and pick. You cannot add the same place twice to the same day.</p>
          </div>
          <button class="btn btn-ghost btn-sm" type="button" @click="closePicker">Close</button>
        </header>
        <input v-model="pickerSearch" class="picker-search" type="search" placeholder="Search attractions…" />
        <div class="picker-list">
          <button
            v-for="a in pickerOptions"
            :key="a.id"
            class="picker-row"
            :disabled="alreadyAdded(a.id, pickerDay)"
            @click="pickStop(a)"
          >
            <div class="thumb" :style="imgStyle(a)"><span v-if="!a.image_url" class="ph">🏛️</span></div>
            <div class="meta">
              <strong>{{ a.name }}</strong>
              <em>{{ a.city || a.region || '—' }} · {{ cap(a.category) }} · {{ Number(a.avg_rating || 0).toFixed(1) }} ★</em>
            </div>
            <span v-if="alreadyAdded(a.id, pickerDay)" class="pill">Already in day</span>
            <span v-else class="pill pill-brand">Add</span>
          </button>
          <p v-if="!pickerOptions.length" class="empty-state">No attractions match that search.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { attractionsAPI } from '@/api/client.js'
import StatCard from '../components/StatCard.vue'
import EmptyState from '../components/EmptyState.vue'

const STORAGE = 'belarus-itinerary'

const tripName = ref('My Belarus trip')
const days = ref([])
const allAttractions = ref([])
const printing = ref(false)
const pickerDay = ref(null)
const pickerSearch = ref('')

const uid = () => Date.now().toString(36) + Math.random().toString(36).slice(2, 6)

const load = () => {
  try {
    const raw = localStorage.getItem(STORAGE)
    if (!raw) { days.value = []; return }
    const data = JSON.parse(raw)
    tripName.value = data.tripName || 'My Belarus trip'
    days.value = (data.days || []).map((d) => ({ id: d.id || uid(), title: d.title || 'New day', items: d.items || [] }))
  } catch (_) { days.value = [] }
}
const save = () => {
  localStorage.setItem(STORAGE, JSON.stringify({ tripName: tripName.value, days: days.value }))
}

const addDay = () => days.value.push({ id: uid(), title: 'Day ' + (days.value.length + 1), items: [] })
const removeDay = (i) => { if (confirm('Remove this day and all its stops?')) days.value.splice(i, 1) }
const moveDay = (i, dir) => {
  const j = i + dir
  if (j < 0 || j >= days.value.length) return
  const tmp = days.value[i]; days.value[i] = days.value[j]; days.value[j] = tmp
}
const removeStop = (di, si) => days.value[di].items.splice(si, 1)
const moveStop = (di, si, dir) => {
  const j = si + dir
  const items = days.value[di].items
  if (j < 0 || j >= items.length) return
  const tmp = items[si]; items[si] = items[j]; items[j] = tmp
}
const alreadyAdded = (id, di) => days.value[di].items.some((s) => s.attraction.id === id)

const stars = (r) => {
  const full = Math.round(r || 0)
  return '★'.repeat(full) + '☆'.repeat(5 - full)
}
const cap = (s) => s ? s.charAt(0).toUpperCase() + s.slice(1) : '—'
const imgStyle = (a) => a.image_url
  ? { backgroundImage: `url(${a.image_url})` }
  : { background: 'var(--grad-brand)' }
const dayCost = (d) => d.items.reduce((s, x) => s + (x.attraction.ticket_price || 0), 0)
const totalStops = computed(() => days.value.reduce((s, d) => s + d.items.length, 0))
const totalCost = computed(() => days.value.reduce((s, d) => s + dayCost(d), 0).toFixed(2))
const avgRating = computed(() => {
  const all = days.value.flatMap((d) => d.items)
  if (!all.length) return 0
  return all.reduce((s, x) => s + (x.attraction.avg_rating || 0), 0) / all.length
})
let dragInfo = null
const onDragStart = (e, di, si) => { dragInfo = { di, si }; e.dataTransfer.effectAllowed = 'move' }
const onDrop = (e, di, si) => {
  if (!dragInfo || dragInfo.di !== di) return
  const target = si < 0 ? days.value[di].items.length - 1 : si
  if (target === dragInfo.si) return
  const items = days.value[di].items
  const [moved] = items.splice(dragInfo.si, 1)
  items.splice(target, 0, moved)
  dragInfo = null
}
const openPicker = async (di) => {
  pickerDay.value = di
  pickerSearch.value = ''
  if (!allAttractions.value.length) {
    const res = await attractionsAPI.list({ per_page: 200 })
    allAttractions.value = res.data.attractions
  }
}
const closePicker = () => { pickerDay.value = null }
const pickerOptions = computed(() => {
  const q = pickerSearch.value.trim().toLowerCase()
  return allAttractions.value
    .filter((a) => !q || a.name.toLowerCase().includes(q) || (a.city || '').toLowerCase().includes(q))
    .slice(0, 60)
})
const pickStop = (a) => {
  if (pickerDay.value == null) return
  if (alreadyAdded(a.id, pickerDay.value)) return
  days.value[pickerDay.value].items.push({ attraction: a, note: '' })
  closePicker()
}
const downloadText = () => {
  const lines = [`Trip: ${tripName.value || 'My Belarus trip'}`, '']
  days.value.forEach((d, i) => {
    lines.push(`Day ${i + 1} - ${d.title || ''}`.trim())
    if (d.items.length) {
      d.items.forEach((s, j) => {
        const price = s.attraction.ticket_price ? s.attraction.ticket_price.toFixed(2) + ' BYN' : 'Free'
        lines.push(`  ${j + 1}. ${s.attraction.name} (${s.attraction.city || s.attraction.region || '—'}) — ${price}`)
        if (s.note) lines.push(`     note: ${s.note}`)
      })
    } else {
      lines.push('  (no stops)')
    }
    lines.push('')
  })
  const blob = new Blob([lines.join('\n')], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a'); a.href = url; a.download = (tripName.value || 'itinerary').replace(/\s+/g, '_') + '.txt'
  document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url)
}
const print = () => { printing.value = true; setTimeout(() => { window.print(); printing.value = false }, 50) }

watch([tripName, days], save, { deep: true })
onMounted(load)
</script>

<style scoped>
.itin { display: flex; flex-direction: column; gap: 1.25rem; }
.page-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }
.head-actions { gap: .5rem; }

.stats { gap: 1rem; }
.trip-meta label { display: block; }
.trip-meta input { font-size: 1.05rem; font-weight: 600; }

.days { display: flex; flex-direction: column; gap: 1rem; }
.day { padding: 0; overflow: hidden; }
.day-head {
  display: flex; align-items: center; gap: .5rem;
  padding: .8rem 1rem;
  background: var(--surface-2);
  border-bottom: 1px solid var(--border);
  flex-wrap: wrap;
}
.day-head.printable { background: var(--surface); border-bottom: 2px solid var(--text); }
.day-head .dtitle { flex: 1 1 200px; font-weight: 600; font-size: 1rem; padding: .4rem .55rem; }
.day-head .dsub { color: var(--text-mute); font-size: .85rem; }
.day-head.printable h2 { margin: 0; font-size: 1.1rem; }

.stops { list-style: none; margin: 0; padding: .4rem; display: flex; flex-direction: column; gap: .3rem; }
.stop {
  display: grid;
  grid-template-columns: 24px 26px 48px 1fr 200px 90px auto;
  gap: .5rem; align-items: center;
  padding: .5rem .55rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
}
.stop .handle { cursor: grab; color: var(--text-mute); user-select: none; text-align: center; }
.stop .num { color: var(--text-mute); font-weight: 700; text-align: center; }
.thumb { width: 48px; height: 48px; border-radius: var(--radius-sm); background-size: cover; background-position: center; display: flex; align-items: center; justify-content: center; }
.thumb .ph { font-size: 1.3rem; opacity: .6; }
.stop-meta { display: flex; flex-direction: column; min-width: 0; }
.stop-meta strong { font-size: .92rem; font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.stop-meta em { font-style: normal; font-size: .76rem; color: var(--text-mute); }
.stop .note { width: 100%; padding: .4rem .5rem; font-size: .82rem; }
.stop-price { text-align: right; font-weight: 700; color: var(--accent-600); font-size: .85rem; }
.stop-actions { gap: .3rem; flex-wrap: nowrap; }

.empty-day { margin: 0; padding: 1rem; text-align: center; color: var(--text-mute); font-size: .88rem; }
.day-foot { padding: .6rem 1rem 1rem; border-top: 1px solid var(--border); background: var(--surface-2); }

.add-day-bar { display: flex; justify-content: center; padding-top: .5rem; }

.picker-overlay {
  position: fixed; inset: 0; z-index: 200;
  background: rgba(15, 23, 42, .55);
  display: flex; align-items: center; justify-content: center;
  padding: 2rem;
}
.picker { width: min(680px, 100%); max-height: 80vh; display: flex; flex-direction: column; padding: 0; }
.picker .section-head { padding: 1rem 1.1rem .5rem; }
.picker-search { margin: 0 1.1rem .5rem; }
.picker-list { overflow-y: auto; padding: .5rem 1.1rem 1rem; display: flex; flex-direction: column; gap: .35rem; }
.picker-row {
  display: flex; align-items: center; gap: .6rem;
  padding: .5rem; border-radius: var(--radius-sm);
  background: var(--surface);
  border: 1px solid var(--border);
  cursor: pointer; text-align: left;
  font: inherit; color: inherit;
  transition: background-color var(--speed) var(--ease);
}
.picker-row:hover:not(:disabled) { background: var(--surface-hover); }
.picker-row:disabled { opacity: .55; cursor: not-allowed; }
.picker-row .meta { flex: 1 1 auto; min-width: 0; display: flex; flex-direction: column; }
.picker-row .meta strong { font-size: .9rem; }
.picker-row .meta em { font-style: normal; font-size: .76rem; color: var(--text-mute); }

@media (max-width: 880px) {
  .stop {
    grid-template-columns: 26px 48px 1fr 90px;
    grid-template-areas:
      'handle num thumb meta price'
      'note  note note  note note'
      'actions actions actions actions actions';
    row-gap: .35rem;
  }
  .stop .handle { grid-area: handle; }
  .stop .num    { grid-area: num; }
  .stop .thumb  { grid-area: thumb; }
  .stop-meta    { grid-area: meta; }
  .stop-price   { grid-area: price; }
  .stop .note   { grid-area: note; }
  .stop-actions { grid-area: actions; }
}

@media print {
  .no-print { display: none !important; }
  .trip-meta, .stats, .add-day-bar { display: none; }
  .day { box-shadow: none; border: 1px solid #ccc; page-break-inside: avoid; }
  .day + .day { margin-top: 1rem; }
  .stop { grid-template-columns: 24px 26px 48px 1fr 90px !important; }
  .stop .note, .stop-actions { display: none; }
  body { background: #fff; }
}
</style>