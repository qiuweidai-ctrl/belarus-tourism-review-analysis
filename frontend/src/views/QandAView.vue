<template>
  <div>
    <h1 class="page-title">Questions &amp; Answers</h1>
    <p class="subtitle">Ask questions about Belarus attractions and get answers from the community.</p>

    <div class="controls">
      <input v-model="search" placeholder="Search questions..." @input="debouncedFetch" class="search-input" />
      <select v-model="attractionFilter" @change="fetchQuestions" class="sort-select">
        <option :value="null">All Attractions</option>
        <option v-for="a in attractions" :key="a.id" :value="a.id">{{ a.name }}</option>
      </select>
      <button v-if="isLoggedIn" @click="showAskForm = !showAskForm" class="btn-primary">
        {{ showAskForm ? 'Cancel' : 'Ask Question' }}
      </button>
    </div>

    <div v-if="showAskForm && isLoggedIn" class="ask-form card">
      <h3>Ask a Question</h3>
      <div class="form-group">
        <label>Attraction *</label>
        <select v-model="askForm.attraction_id">
          <option v-for="a in attractions" :key="a.id" :value="a.id">{{ a.name }}</option>
        </select>
      </div>
      <div class="form-group">
        <label>Question Title *</label>
        <input v-model="askForm.title" type="text" placeholder="What's your question?" />
      </div>
      <div class="form-group">
        <label>Details</label>
        <textarea v-model="askForm.content" rows="3" placeholder="Add more context..."></textarea>
      </div>
      <button @click="submitQuestion" :disabled="!askForm.title || !askForm.attraction_id" class="btn-primary">Submit Question</button>
    </div>

    <div v-if="loading" class="loading">{{ $t('common.loading') }}</div>
    <div v-else-if="questions.length === 0" class="empty-state">No questions found.</div>
    <div v-else class="questions-list">
      <div v-for="q in questions" :key="q.id" class="question-card card">
        <div class="q-header">
          <div class="q-badges">
            <span v-if="q.has_accepted_answer" class="badge-accepted">✓ Answered</span>
            <span class="badge-answers">{{ q.answer_count }} answers</span>
          </div>
          <div class="q-upvotes">▲ {{ q.upvote_count }}</div>
        </div>
        <h3 @click="$router.push('/qa?q=' + q.id)" class="q-title">{{ q.title }}</h3>
        <p class="q-content">{{ q.content.slice(0, 120) }}{{ q.content.length > 120 ? '...' : '' }}</p>
        <div class="q-footer">
          <span class="q-author">Asked by {{ q.username }}</span>
          <span class="q-date">{{ formatDate(q.created_at) }}</span>
          <span v-if="q.attraction_name" class="q-attr">In: {{ q.attraction_name }}</span>
        </div>
      </div>
    </div>

    <div v-if="totalPages > 1" class="pagination">
      <button @click="page--; fetchQuestions()" :disabled="page <= 1" class="btn-secondary">Prev</button>
      <span>{{ page }} / {{ totalPages }}</span>
      <button @click="page++; fetchQuestions()" :disabled="page >= totalPages" class="btn-secondary">Next</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { qaAPI, attractionsAPI } from '../api/client.js'

const route = useRoute()
const questions = ref([])
const attractions = ref([])
const loading = ref(false)
const search = ref('')
const attractionFilter = ref(null)
const page = ref(1)
const totalPages = ref(1)
const showAskForm = ref(false)
const isLoggedIn = computed(() => !!localStorage.getItem('token'))

const askForm = ref({ attraction_id: null, title: '', content: '' })

let debounceTimer = null
const debouncedFetch = () => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => { page.value = 1; fetchQuestions() }, 400)
}

const fetchQuestions = async () => {
  loading.value = true
  try {
    const params = { page: page.value, per_page: 15 }
    if (search.value) params.search = search.value
    if (attractionFilter.value) params.attraction_id = attractionFilter.value
    const res = await qaAPI.listQuestions(params)
    questions.value = res.data.questions
    totalPages.value = res.data.pages
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

const submitQuestion = async () => {
  try {
    await qaAPI.createQuestion(askForm.value)
    showAskForm.value = false
    askForm.value = { attraction_id: null, title: '', content: '' }
    await fetchQuestions()
  } catch (e) { alert('Failed to submit question') }
}

const formatDate = (d) => new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })

const loadAttractions = async () => {
  try {
    const res = await attractionsAPI.list({ per_page: 100 })
    attractions.value = res.data.attractions
  } catch (e) { console.error(e) }
}

onMounted(async () => {
  await loadAttractions()
  if (route.query.q) { attractionFilter.value = parseInt(route.query.q); }
  await fetchQuestions()
})
</script>

<style scoped>
.subtitle { color: #666; margin-bottom: 1.5rem; }
.controls { display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
.search-input { flex: 1; max-width: 400px; }
.sort-select { width: 200px; }

.ask-form { margin-bottom: 1.5rem; background: #f0f8f8; }
.ask-form h3 { color: #1a5e63; margin-bottom: 1rem; }
.form-group { margin-bottom: 1rem; }
.form-group label { display: block; margin-bottom: 0.3rem; font-weight: 500; }

.questions-list { display: flex; flex-direction: column; gap: 1rem; }
.question-card { padding: 1rem 1.2rem; }

.q-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
.q-badges { display: flex; gap: 0.5rem; }
.q-upvotes { color: #888; font-size: 0.9rem; }

.q-title { color: #1a5e63; cursor: pointer; margin-bottom: 0.3rem; }
.q-title:hover { text-decoration: underline; }
.q-content { color: #666; font-size: 0.9rem; margin-bottom: 0.5rem; }

.q-footer { display: flex; gap: 1rem; font-size: 0.8rem; color: #aaa; }
.q-author { color: #1a5e63; }

.badge-accepted { background: #2a9d5c; color: white; padding: 0.1rem 0.5rem; border-radius: 10px; font-size: 0.75rem; }
.badge-answers { background: #eee; color: #666; padding: 0.1rem 0.5rem; border-radius: 10px; font-size: 0.75rem; }

.pagination { display: flex; justify-content: center; gap: 1rem; margin-top: 2rem; }
</style>
