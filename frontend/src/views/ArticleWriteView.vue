<template>
  <div>
    <h1 class="page-title">{{ isEdit ? 'Edit Article' : 'Write an Article' }}</h1>

    <div v-if="error" class="error-msg">{{ error }}</div>
    <div v-if="success" class="success-msg">{{ success }}</div>

    <div class="article-form card">
      <div class="form-group">
        <label>Title *</label>
        <input v-model="form.title" type="text" placeholder="Article title..." required />
      </div>

      <div class="form-group">
        <label>Summary</label>
        <input v-model="form.summary" type="text" placeholder="Brief summary (optional)..." />
      </div>

      <div class="form-group">
        <label>Cover Image URL</label>
        <input v-model="form.cover_image_url" type="text" placeholder="https://..." />
      </div>

      <div class="form-group">
        <label>Related Attraction</label>
        <select v-model="form.attraction_id">
          <option :value="null">-- None --</option>
          <option v-for="a in attractions" :key="a.id" :value="a.id">{{ a.name }}</option>
        </select>
      </div>

      <div class="form-group">
        <label>Tags (comma separated)</label>
        <input v-model="tagsInput" type="text" placeholder="history, nature, castle..." />
      </div>

      <div class="form-group">
        <label>Content *</label>
        <textarea v-model="form.content" rows="15" placeholder="Write your travel guide here..."></textarea>
      </div>

      <div class="form-actions">
        <button @click="submit" :disabled="submitting || !form.title || !form.content" class="btn-primary">
          {{ submitting ? 'Publishing...' : (isEdit ? 'Update' : 'Publish') }}
        </button>
        <button @click="$router.push('/articles')" class="btn-secondary">Cancel</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { articlesAPI, attractionsAPI } from '../api/client.js'

const route = useRoute()
const router = useRouter()

const isEdit = ref(!!route.params.id)
const form = ref({ title: '', summary: '', content: '', cover_image_url: '', attraction_id: null, is_published: true })
const tagsInput = ref('')
const attractions = ref([])
const submitting = ref(false)
const error = ref('')
const success = ref('')

const loadArticle = async () => {
  if (!route.params.id) return
  try {
    const res = await articlesAPI.get(route.params.id)
    form.value.title = res.data.title
    form.value.summary = res.data.summary || ''
    form.value.content = res.data.content
    form.value.cover_image_url = res.data.cover_image_url || ''
    form.value.attraction_id = res.data.attraction_id
    form.value.is_published = res.data.is_published
    tagsInput.value = (res.data.tags || []).join(', ')
  } catch (e) { console.error(e) }
}

const loadAttractions = async () => {
  try {
    const res = await attractionsAPI.list({ per_page: 100 })
    attractions.value = res.data.attractions
  } catch (e) { console.error(e) }
}

const submit = async () => {
  submitting.value = true
  error.value = ''
  try {
    const payload = { ...form.value }
    if (tagsInput.value) {
      payload.tags = tagsInput.value.split(',').map(t => t.trim()).filter(Boolean)
    }
    if (isEdit.value) {
      await articlesAPI.update(route.params.id, payload)
      success.value = 'Article updated!'
    } else {
      const res = await articlesAPI.create(payload)
      router.push('/articles/' + res.data.id)
    }
  } catch (e) {
    error.value = e.response?.data?.error || 'Submission failed'
  } finally {
    submitting.value = false
  }
}

onMounted(() => { loadArticle(); loadAttractions() })
</script>

<style scoped>
.article-form { max-width: 800px; }
.form-group { margin-bottom: 1.2rem; }
.form-group label { display: block; margin-bottom: 0.4rem; font-weight: 500; color: #555; }
.form-group textarea { resize: vertical; }
.form-actions { display: flex; gap: 1rem; margin-top: 1rem; }
</style>
