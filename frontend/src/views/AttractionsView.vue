<template>
  <div>
    <h1 class="page-title">{{ $t('attractions.title') }}</h1>

    <div class="controls">
      <input
        v-model="search"
        :placeholder="$t('attractions.search')"
        @input="debouncedFetch"
        class="search-input"
      />
      <select v-model="category" @change="page = 1; syncQuery(); fetchAttractions()" class="filter-select">
        <option value="">{{ $t('attractions.allCategories') }}</option>
        <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
      </select>
      <select v-model="sortBy" @change="page = 1; syncQuery(); fetchAttractions()" class="sort-select">
        <option value="created_at">{{ $t('attractions.sortNew') }}</option>
        <option value="rating">{{ $t('attractions.sortRating') }}</option>
        <option value="name">{{ $t('attractions.sortName') }}</option>
      </select>
    </div>

    <div v-if="loading" class="loading">{{ $t('common.loading') }}</div>
    <div v-else-if="attractions.length === 0" class="loading">{{ $t('home.noAttractions') }}</div>
    <div v-else class="attractions-grid">
      <AttractionCard
        v-for="a in attractions"
        :key="a.id"
        :attraction="a"
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
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { attractionsAPI } from '@/api/client.js'
import AttractionCard from '../components/AttractionCard.vue'

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

let debounceTimer = null
const debouncedFetch = () => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    page.value = 1
    syncQuery()
    fetchAttractions()
  }, 400)
}

const syncQuery = () => {
  const q = {}
  if (page.value > 1) q.page = page.value
  if (search.value) q.search = search.value
  if (category.value) q.category = category.value
  if (sortBy.value !== 'created_at') q.sort = sortBy.value
  router.replace({ query: q })
}

const fetchAttractions = async () => {
  loading.value = true
  try {
    const res = await attractionsAPI.list({
      search: search.value,
      category: category.value,
      sort: sortBy.value,
      page: page.value,
      per_page: 9
    })
    attractions.value = res.data.attractions
    totalPages.value = res.data.pages
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
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
  fetchAttractions()
}
watch(() => route.query, (q) => {
  if (q.page !== undefined) page.value = Number(q.page)
  if (q.search !== undefined) search.value = q.search
  if (q.category !== undefined) category.value = q.category
  if (q.sort !== undefined) sortBy.value = q.sort
  fetchAttractions()
}, { immediate: false })

onMounted(() => {
  if (route.query.page) page.value = Number(route.query.page)
  if (route.query.search) search.value = route.query.search
  if (route.query.category) category.value = route.query.category
  if (route.query.sort) sortBy.value = route.query.sort

  loadCategories()
  fetchAttractions()
})
</script>

<style scoped>
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
</style>
