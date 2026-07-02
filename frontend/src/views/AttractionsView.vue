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
      <select v-model="category" @change="fetchAttractions" class="filter-select">
        <option value="">{{ $t('attractions.allCategories') }}</option>
        <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
      </select>
      <select v-model="sortBy" @change="fetchAttractions" class="sort-select">
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
      <button @click="page--; fetchAttractions()" :disabled="page <= 1" class="btn-secondary">Prev</button>
      <span>Page {{ page }} / {{ totalPages }}</span>
      <button @click="page++; fetchAttractions()" :disabled="page >= totalPages" class="btn-secondary">Next</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { attractionsAPI } from '../api/client.js'
import AttractionCard from '../components/AttractionCard.vue'

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
    fetchAttractions()
  }, 400)
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

onMounted(() => {
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