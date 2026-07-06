<template>
  <div>
    <h1 class="page-title">Travel Guides &amp; Articles</h1>

    <div class="controls">
      <input v-model="search" placeholder="Search articles..." @input="debouncedFetch" class="search-input" />
      <select v-model="filterType" @change="page.value = 1; syncQuery(); fetchArticles()" class="sort-select">
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
        <div class="article-cover" :class="{ 'loaded': coverLoaded[article.id], 'failed': coverFailed[article.id] }">
          <img
            v-if="article.cover_image_url && !coverFailed[article.id]"
            :src="article.cover_image_url"
            :alt="article.title"
            class="cover-img"
            @load="onCoverLoad(article.id)"
            @error="onCoverError(article.id)"
            loading="lazy"
            referrerpolicy="no-referrer"
          />
          <div v-if="!coverLoaded[article.id]" class="cover-fallback">
            <span class="cover-icon">{{ coverIcon(article) }}</span>
            <span class="cover-title-hint">{{ article.title }}</span>
          </div>
        </div>
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
      <button @click="goToPage(page - 1)" :disabled="page <= 1" class="btn-secondary">Prev</button>
      <span>Page {{ page }} / {{ totalPages }}</span>
      <button @click="goToPage(page + 1)" :disabled="page >= totalPages" class="btn-secondary">Next</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { articlesAPI } from '@/api/client.js'

const route = useRoute()
const router = useRouter()
const articles = ref([])
const loading = ref(false)
const search = ref('')
const filterType = ref('')
const page = ref(1)
const totalPages = ref(1)
const isLoggedIn = computed(() => !!localStorage.getItem('token'))

// Cover image loading state. The earlier implementation pre-probed with
// new Image() — but cross-origin images (Wikipedia etc.) often fail to probe
// and fall back forever. Now we let <img>'s native onload/onerror drive the
// state so success/failure is captured accurately.
const coverLoaded = ref({})
const coverFailed = ref({})

const onCoverLoad = (id) => { coverLoaded.value[id] = true; coverFailed.value[id] = false }
const onCoverError = (id) => { coverLoaded.value[id] = false; coverFailed.value[id] = true }

// Pick a travel-themed emoji placeholder for the cover based on the title.
const coverIcon = (article) => {
  const t = (article.title || '').toLowerCase()
  if (/castle|замок|несвиж|мир/.test(t)) return '🏰'
  if (/bison|bison|зубр/.test(t)) return '🦬'
  if (/brest|fortress|крепость/.test(t)) return '🛡️'
  if (/minsk|минск|city/.test(t)) return '🏙️'
  if (/nature|forest|лес|park/.test(t)) return '🌲'
  if (/church|cathedral|церковь/.test(t)) return '⛪'
  if (/museum|музей/.test(t)) return '🏛️'
  return '🏰'
}

let debounceTimer = null
const debouncedFetch = () => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    page.value = 1
    syncQuery()
    fetchArticles()
  }, 400)
}

const syncQuery = () => {
  const q = {}
  if (page.value > 1) q.page = page.value
  if (search.value) q.search = search.value
  if (filterType.value) q.featured = filterType.value
  router.replace({ query: q })
}

const goToPage = (p) => {
  page.value = p
  syncQuery()
  fetchArticles()
}

watch(() => route.query, (q) => {
  if (q.page !== undefined) page.value = Number(q.page)
  if (q.search !== undefined) search.value = q.search
  if (q.featured !== undefined) filterType.value = q.featured
  fetchArticles()
}, { immediate: false })

const fetchArticles = async () => {
  loading.value = true
  // Reset cover state when fetching a new batch so old fail/loaded flags
  // don't leak onto the new articles.
  coverLoaded.value = {}
  coverFailed.value = {}
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

onMounted(() => {
  // Sync state from URL query params so Back navigation lands on the correct page.
  if (route.query.page) page.value = Number(route.query.page)
  if (route.query.search) search.value = route.query.search
  if (route.query.featured) filterType.value = route.query.featured

  fetchArticles()
})
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
  flex-shrink: 0;
  border-radius: 8px 0 0 8px;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #1a5e63, #2d8a8e);
  display: flex;
  align-items: center;
  justify-content: center;
}

.cover-img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0;
  transition: opacity 0.4s ease-in;
}
.article-cover.loaded .cover-img { opacity: 1; }
.article-cover.failed { background: linear-gradient(135deg, #1a5e63, #2d8a8e); }

.cover-fallback {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.9);
  gap: 0.4rem;
  padding: 0.5rem;
}

.cover-icon {
  font-size: 3.2rem;
  filter: drop-shadow(0 2px 6px rgba(0, 0, 0, 0.25));
}

.cover-title-hint {
  font-size: 0.78rem;
  text-align: center;
  color: rgba(255, 255, 255, 0.85);
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 720px) {
  .article-cover {
    width: 100%;
    height: 160px;
    border-radius: 8px 8px 0 0;
  }
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
