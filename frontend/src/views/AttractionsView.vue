<template>
  <div>
    <div class="page-heading">
      <h1 class="page-title">{{ $t('attractions.title') }}</h1>
      <button v-if="isAdmin" class="btn-primary" @click="showCreate = !showCreate">
        {{ showCreate ? 'Close form' : 'Add attraction' }}
      </button>
    </div>

    <form v-if="isAdmin && showCreate" class="create-panel card" @submit.prevent="createAttraction">
      <h2>Add attraction</h2>
      <p class="draft-note">New attractions are saved as drafts. They become public only after core field sources and an external rating pass the audit.</p>
      <div class="form-grid">
        <label>Name *<input v-model.trim="createForm.name" required maxlength="200" /></label>
        <label>Location *<input v-model.trim="createForm.location" required maxlength="255" /></label>
        <label>City<input v-model.trim="createForm.city" maxlength="100" /></label>
        <label>Region<input v-model.trim="createForm.region" maxlength="100" /></label>
        <label>Category<input v-model.trim="createForm.category" maxlength="50" placeholder="museum, church, park..." /></label>
        <label>Ticket price (BYN)<input v-model.number="createForm.ticket_price" type="number" min="0" step="0.01" /></label>
        <label>Latitude<input v-model.number="createForm.latitude" type="number" min="-90" max="90" step="any" /></label>
        <label>Longitude<input v-model.number="createForm.longitude" type="number" min="-180" max="180" step="any" /></label>
        <label class="wide">Image URL<input v-model.trim="createForm.image_url" type="url" placeholder="https://..." /></label>
        <label class="wide">Description<textarea v-model.trim="createForm.description" rows="3" maxlength="1200"></textarea></label>
      </div>
      <p v-if="adminError" class="form-error">{{ adminError }}</p>
      <button class="btn-primary" type="submit" :disabled="creating">{{ creating ? 'Adding...' : 'Add attraction' }}</button>
    </form>

    <div class="controls">
      <input
        v-model="search"
        :placeholder="$t('attractions.search')"
        @input="debouncedFetch"
        class="search-input"
      />
      <select v-model="category" @change="page = 1; syncQuery()" class="filter-select">
        <option value="">{{ $t('attractions.allCategories') }}</option>
        <option v-for="c in categories" :key="c" :value="c">{{ formatCategory(c) }}</option>
      </select>
      <select v-model="sortBy" @change="page = 1; syncQuery()" class="sort-select">
        <option value="created_at">{{ $t('attractions.sortNew') }}</option>
        <option value="rating">{{ $t('attractions.sortRating') }}</option>
        <option value="name">{{ $t('attractions.sortName') }}</option>
      </select>
    </div>

    <div v-if="loading" class="loading">{{ $t('common.loading') }}</div>
    <div v-else-if="attractions.length === 0" class="loading">{{ $t('home.noAttractions') }}</div>
    <div v-else class="attractions-grid">
      <AttractionCard
        v-for="(a, index) in attractions"
        :key="a.id"
        :attraction="a"
        :eager="index < 3"
        :admin-mode="isAdmin"
        @delete="deleteAttraction"
      />
    </div>

    <div v-if="totalPages > 1" class="pagination">
      <button @click="goToPage(page - 1)" :disabled="page <= 1" class="btn-secondary">Prev</button>
      <span>Page {{ page }} / {{ totalPages }}</span>
      <button @click="goToPage(page + 1)" :disabled="page >= totalPages" class="btn-secondary">Next</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { attractionsAPI } from '@/api/client.js'
import AttractionCard from '../components/AttractionCard.vue'
import { formatCategory } from '@/utils/displayText.js'

const route = useRoute()
const router = useRouter()
const attractions = ref([])
const loading = ref(false)
const search = ref('')
const category = ref('')
const sortBy = ref('created_at')
const page = ref(1)
const totalPages = ref(1)
const categories = ref([])
const storedUser = JSON.parse(localStorage.getItem('user') || '{}')
const isAdmin = storedUser.role === 'admin'
const showCreate = ref(false)
const creating = ref(false)
const adminError = ref('')
const emptyCreateForm = () => ({ name: '', location: '', city: '', region: '', category: 'other', ticket_price: null, latitude: null, longitude: null, image_url: '', description: '' })
const createForm = ref(emptyCreateForm())

const createAttraction = async () => {
  creating.value = true
  adminError.value = ''
  try {
    await attractionsAPI.create(createForm.value)
    createForm.value = emptyCreateForm()
    showCreate.value = false
    page.value = 1
    await Promise.all([fetchAttractions(), loadCategories()])
  } catch (e) {
    adminError.value = e.response?.data?.error || 'Unable to add the attraction.'
  } finally {
    creating.value = false
  }
}

const deleteAttraction = async (attraction) => {
  if (!confirm(`Archive "${attraction.name}"? It will leave the public catalog but keep related content.`)) return
  adminError.value = ''
  try {
    await attractionsAPI.delete(attraction.id)
    await fetchAttractions()
  } catch (e) {
    adminError.value = e.response?.data?.error || 'Unable to delete the attraction.'
  }
}

let debounceTimer = null
const debouncedFetch = () => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    page.value = 1
    syncQuery()
  }, 400)
}

const syncQuery = () => {
  const q = {}
  if (page.value > 1) q.page = String(page.value)
  if (search.value) q.search = search.value
  if (category.value) q.category = category.value
  if (sortBy.value !== 'created_at') q.sort = sortBy.value
  router.replace({ query: q })
}

let activeRequest = null
const fetchAttractions = async () => {
  // 切换筛选时取消上一次请求，避免旧结果覆盖新结果。
  activeRequest?.abort()
  const controller = new AbortController()
  activeRequest = controller
  loading.value = true
  try {
    const res = await attractionsAPI.list({
      search: search.value,
      category: category.value,
      sort: sortBy.value,
      page: page.value,
      per_page: 9
    }, { signal: controller.signal })
    if (controller.signal.aborted) return
    attractions.value = res.data.attractions
    totalPages.value = res.data.pages
  } catch (e) {
    if (!controller.signal.aborted) console.error(e)
  } finally {
    if (activeRequest === controller) loading.value = false
  }
}

const loadCategories = async () => {
  try {
    const res = await attractionsAPI.categories()
    categories.value = res.data.categories || []
  } catch (e) {
    console.error(e)
  }
}

const goToPage = (p) => {
  page.value = p
  syncQuery()
}
watch(() => route.query, (q) => {
  page.value = Math.max(1, Number(q.page) || 1)
  search.value = q.search || ''
  category.value = q.category || ''
  sortBy.value = q.sort || 'created_at'
  fetchAttractions()
}, { immediate: true })

onMounted(() => {
  loadCategories()
})
onBeforeUnmount(() => {
  clearTimeout(debounceTimer)
  activeRequest?.abort()
})
</script>

<style scoped>
.page-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.25rem;
}
.page-heading .page-title { margin-bottom: 0; }
.create-panel { margin-bottom: 1.5rem; padding: 1.25rem; }
.create-panel h2 { margin: 0 0 1rem; color: var(--text); }
.form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1rem; margin-bottom: 1rem; }
.form-grid label { display: flex; flex-direction: column; gap: .35rem; color: var(--text-soft); font-size: .88rem; font-weight: 600; }
.form-grid .wide { grid-column: 1 / -1; }
.form-error { color: var(--danger, #b91c1c); margin: 0 0 .8rem; }
.controls {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.search-input {
  flex: 1;
  min-width: 240px;
  max-width: 400px;
}

.filter-select,
.sort-select {
  width: 200px;
}

.attractions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
}
@media (max-width: 680px) {
  .page-heading { align-items: flex-start; }
  .form-grid { grid-template-columns: 1fr; }
  .form-grid .wide { grid-column: auto; }
}
</style>
