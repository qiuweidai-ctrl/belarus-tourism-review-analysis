<template>
  <div v-if="article">
    <button @click="$router.back()" class="btn-secondary back-btn">{{ $t('common.back') }}</button>

    <div v-if="article.cover_image_url" class="article-hero" :style="{ backgroundImage: 'url(' + article.cover_image_url + ')' }"></div>

    <div class="article-header">
      <h1>{{ article.title }}</h1>
      <div class="article-meta">
        <span>By {{ article.username }}</span>
        <span>{{ formatDate(article.created_at) }}</span>
        <span v-if="article.attraction_name">In {{ article.attraction_name }}</span>
        <span v-if="article.is_featured" class="badge-featured">Featured</span>
      </div>
    </div>

    <div class="article-content card">
      <p v-for="(para, i) in paragraphs" :key="i">{{ para }}</p>
    </div>

    <div class="article-actions">
      <button @click="toggleLike" :class="article.liked ? 'btn-primary' : 'btn-secondary'">
        {{ article.liked ? '♥ Liked' : '♡ Like' }} ({{ article.like_count }})
      </button>
      <span class="stat">Views: {{ article.view_count }}</span>
      <span class="stat">Comments: {{ article.comment_count }}</span>
    </div>

    <div class="article-comments card">
      <h3>Comments ({{ comments.length }})</h3>
      <div v-if="isLoggedIn" class="comment-form">
        <textarea v-model="newComment" placeholder="Write a comment..." rows="3"></textarea>
        <button @click="submitComment" class="btn-primary" :disabled="!newComment">Submit</button>
      </div>
      <div v-else class="login-prompt">
        <router-link to="/login">Login</router-link> to comment
      </div>
      <div v-for="c in comments" :key="c.id" class="comment-item">
        <strong>{{ c.username }}</strong>
        <span class="comment-date">{{ formatDate(c.created_at) }}</span>
        <p>{{ c.content }}</p>
      </div>
    </div>
  </div>
  <div v-else class="loading">{{ $t('common.loading') }}</div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { articlesAPI } from '../api/client.js'

const route = useRoute()
const article = ref(null)
const comments = ref([])
const newComment = ref('')
const isLoggedIn = computed(() => !!localStorage.getItem('token'))

const paragraphs = computed(() => {
  if (!article.value) return []
  return article.value.content.split('\n').filter(p => p.trim())
})

const fetchArticle = async () => {
  try {
    const res = await articlesAPI.get(route.params.id)
    article.value = res.data
    await loadComments()
  } catch (e) { console.error(e) }
}

const loadComments = async () => {
  try {
    const res = await articlesAPI.comments(route.params.id)
    comments.value = res.data.comments
  } catch (e) { console.error(e) }
}

const toggleLike = async () => {
  if (!isLoggedIn.value) return
  try {
    const res = await articlesAPI.like(route.params.id)
    article.value.liked = res.data.liked
    article.value.like_count = res.data.like_count
  } catch (e) { console.error(e) }
}

const submitComment = async () => {
  if (!newComment.value.trim()) return
  try {
    await articlesAPI.addComment(route.params.id, { content: newComment.value })
    newComment.value = ''
    await loadComments()
  } catch (e) { alert('Failed to post comment') }
}

const formatDate = (d) => new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })

onMounted(fetchArticle)
</script>

<style scoped>
.back-btn { margin-bottom: 1rem; }

.article-hero {
  height: 350px;
  background-size: cover;
  background-position: center;
  border-radius: 12px;
  margin-bottom: 1.5rem;
}

.article-header { margin-bottom: 1.5rem; }
.article-header h1 { color: #1a5e63; margin-bottom: 0.5rem; }

.article-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.9rem;
  color: #888;
}

.article-content {
  line-height: 1.9;
  color: #444;
  margin-bottom: 1.5rem;
}
.article-content p { margin-bottom: 1rem; }

.article-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-bottom: 2rem;
}
.stat { color: #888; font-size: 0.9rem; }

.article-comments h3 { margin-bottom: 1rem; color: #1a5e63; }

.comment-form textarea { margin-bottom: 0.5rem; }
.comment-form button { margin-top: 0.5rem; }

.comment-item {
  padding: 1rem 0;
  border-bottom: 1px solid #eee;
}
.comment-item strong { color: #1a5e63; }
.comment-date { color: #aaa; font-size: 0.8rem; margin-left: 0.5rem; }
.comment-item p { margin-top: 0.3rem; color: #555; }

.badge-featured { background: #f5a623; color: white; padding: 0.1rem 0.5rem; border-radius: 10px; font-size: 0.75rem; }
</style>
