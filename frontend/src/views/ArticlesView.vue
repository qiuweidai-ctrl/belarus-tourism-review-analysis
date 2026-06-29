<template>
  <div>
    <h1 class="page-title">Travel Guides &amp; Articles</h1>

    <div class="controls">
      <input v-model="search" placeholder="Search articles..." @input="debouncedFetch" class="search-input" />
      <select v-model="filterType" @change="fetchArticles" class="sort-select">
        <option value="">All Articles</option>
        <option value="true">Featured Only</option>
      </select>
      <button v-if="isLoggedIn" @click="$router.push('/articles/write')" class="btn-primary">Write Article</button>
    </div>

    <div v-if="loading" class="loading">{{ $t('common.loading') }}</div>
    <div v-else-if="articles.length === 0" class="empty-state">
      <p>No articles yet. Be the first to share your Belarus travel experience!</p>
      <button v-if="isLoggedIn" @click="$router.push('/articles/write')" class="btn-primary">Write the First Article</button>
    </div>
    <div v-else class="articles-list">
      <div v-for="article in articles" :key="article.id" class="article-card card" @click="$router.push('/articles/' + article.id)">
        <div v-if="article.cover_image_url" class="article-cover" :style="{ backgroundImage: 'url(' + article.cover_image_url + ')' }"></div>
        <div class="article-body">
          <div class="article-meta">
            <span class="article-author">By {{ article.username }}</span>
            <span class="article-date">{{ formatDate(article.created_at) }}</span>
            <span v-if="article.is_featured" class="badge-featured">Featured</span>
          </div>
          <h3>{{ article.title }}</h3>
          <p class="article-summary">{{ article.summary || article.content.slice(0, 150) + '...' }}</p>
          <div class="article-stats">
            <span>Views: {{ article.view_count }}</span>
            <span>Likes: {{ article.like_count }}</span>
            <span>Comments: {{ article.comment_count }}</span>
            <span v-if="article.attraction_name">In: {{ article.attraction_name }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="totalPages > 1" class="pagination">
      <button @click="page--; fetchArticles()" :disabled="page <= 1" class="btn-secondary">Prev</button>
      <span>Page {{ page }} / {{ totalPages }}</span>
      <button @click="page++; fetchArticles()" :disabled="page >= totalPages" class="btn-secondary">Next</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { articlesAPI } from '../api/client.js'

const articles = ref([])
const loading = ref(false)
const search = ref('')
const filterType = ref('')
const page = ref(1)
const totalPages = ref(1)
const isLoggedIn = computed(() => !!localStorage.getItem('token'))

let debounceTimer = null
const debouncedFetch = () => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => { page.value = 1; fetchArticles() }, 400)
}

const fetchArticles = async () => {
  loading.value = true
  try {
    const params = { page: page.value, per_page: 12 }
    if (search.value) params.search = search.value
    if (filterType.value === 'true') params.featured = true
    const res = await articlesAPI.list(params)
    articles.value = res.data.articles
    totalPages.value = res.data.pages
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

const formatDate = (d) => new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })

onMounted(fetchArticles)
</script>

<style scoped>
.controls {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}
.search-input { flex: 1; max-width: 400px; }
.sort-select { width: 160px; }

.articles-list { display: flex; flex-direction: column; gap: 1.2rem; }

.article-card {
  display: flex;
  cursor: pointer;
  overflow: hidden;
  transition: transform 0.2s;
}
.article-card:hover { transform: translateX(4px); }

.article-cover {
  width: 240px;
  min-height: 160px;
  background-size: cover;
  background-position: center;
  flex-shrink: 0;
  border-radius: 8px 0 0 8px;
}

.article-body { padding: 1rem 1.2rem; flex: 1; }

.article-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.85rem;
  color: #888;
  margin-bottom: 0.5rem;
}

.article-body h3 {
  color: #1a5e63;
  margin-bottom: 0.5rem;
}

.article-summary {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
  line-height: 1.5;
}

.article-stats {
  display: flex;
  gap: 1rem;
  font-size: 0.8rem;
  color: #aaa;
}

.badge-featured {
  background: #f5a623;
  color: white;
  padding: 0.1rem 0.5rem;
  border-radius: 10px;
  font-size: 0.75rem;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: #888;
}

.pagination {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-top: 2rem;
}
</style>
