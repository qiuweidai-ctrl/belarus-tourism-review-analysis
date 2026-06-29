<template>
  <div v-if="attraction">
    <button @click="$router.back()" class="btn-secondary back-btn">{{ $t('common.back') }}</button>

    <div class="detail-header">
      <div class="detail-image" :style="imageStyle"></div>
      <div class="detail-info">
        <h1>{{ attraction.name }}</h1>
        <p class="location">{{ attraction.location }}</p>
        <div class="stats">
          <span class="rating">{{ $t('attractions.rating') }}: {{ attraction.avg_rating }} / 5</span>
          <span class="review-count">{{ attraction.review_count }} {{ $t('attractions.reviews') }}</span>
        </div>
        <p class="description">{{ attraction.description }}</p>

        <div class="sentiment-summary" v-if="attraction.sentiment_score !== 0">
          <h3>{{ $t('attractionDetail.sentiment') }}</h3>
          <div class="sentiment-bar">
            <div class="sentiment-fill" :style="{ width: sentimentPercent + '%', background: sentimentColor }"></div>
          </div>
          <div class="sentiment-labels">
            <span>Negative</span>
            <span>Neutral</span>
            <span>Positive</span>
          </div>
          <p class="sentiment-desc">
            Overall sentiment score: {{ attraction.sentiment_score > 0 ? '+' : '' }}{{ attraction.sentiment_score.toFixed(2) }}
            ({{ sentimentLabel }})
          </p>
        </div>

        <div v-if="isLoggedIn && predictedRating !== null" class="predicted-rating">
          <h3>{{ $t('attractionDetail.predictedRating') }}</h3>
          <p class="pred-score">{{ predictedRating }} / 5</p>
          <p v-if="predictReason" class="pred-reason">{{ predictReason }}</p>
        </div>
      </div>
    </div>

    <div class="detail-section">
      <h2>{{ $t('attractionDetail.reviews') }}</h2>

      <div v-if="isLoggedIn" class="review-form card">
        <h3>{{ $t('attractionDetail.writeReview') }}</h3>
        <div class="rating-input">
          <label>{{ $t('attractionDetail.rating') }}:</label>
          <div class="stars-input">
            <span
              v-for="n in 5"
              :key="n"
              :class="{ 'star': true, 'filled': n <= newReview.rating }"
              @click="newReview.rating = n"
            >★</span>
          </div>
        </div>
        <textarea
          v-model="newReview.content"
          :placeholder="$t('attractionDetail.contentPlaceholder')"
          rows="4"
        ></textarea>
        <button @click="submitReview" :disabled="!newReview.content || submitting" class="btn-primary">
          {{ submitting ? $t('common.loading') : $t('attractionDetail.submit') }}
        </button>
      </div>
      <div v-else class="login-prompt">
        <p>{{ $t('attractionDetail.loginRequired') }}</p>
        <router-link to="/login" class="btn-primary">{{ $t('nav.login') }}</router-link>
      </div>

      <div v-if="reviews.length === 0" class="loading">{{ $t('attractionDetail.noReviews') }}</div>
      <div v-else class="reviews-list">
        <div v-for="r in reviews" :key="r.id" class="review-card card">
          <div class="review-top">
            <strong>{{ r.username }}</strong>
            <span class="stars">{{ '★'.repeat(r.rating) }}{{ '☆'.repeat(5 - r.rating) }}</span>
          </div>
          <p>{{ r.content }}</p>
          <div class="review-meta">
            <span :class="'sentiment-badge sentiment-' + r.sentiment_label">
              {{ r.sentiment_label }}
            </span>
            <span class="review-date">{{ formatDate(r.created_at) }}</span>
            <button
              v-if="isLoggedIn && currentUserId == r.user_id"
              @click="deleteReview(r.id)"
              class="btn-link delete-btn"
            >{{ $t('common.delete') }}</button>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div v-else class="loading">{{ $t('common.loading') }}</div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { attractionsAPI, reviewsAPI, recommendationsAPI } from '../api/client.js'

const route = useRoute()
const router = useRouter()
const attraction = ref(null)
const reviews = ref([])
const loading = ref(true)
const submitting = ref(false)
const isLoggedIn = ref(!!localStorage.getItem('token'))
const currentUserId = ref(parseInt(localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')).id : '0'))

const newReview = ref({ content: '', rating: 5 })
const predictedRating = ref(null)
const predictReason = ref('')

const imageStyle = computed(() => {
  if (attraction.value?.image_url) {
    return { backgroundImage: `url(${attraction.value.image_url})` }
  }
  return { background: 'linear-gradient(135deg, #1a5e63, #2d8a8e)' }
})

const sentimentPercent = computed(() => {
  if (!attraction.value) return 50
  return Math.round(((attraction.value.sentiment_score + 1) / 2) * 100)
})

const sentimentColor = computed(() => {
  if (!attraction.value) return '#888'
  const s = attraction.value.sentiment_score
  if (s > 0.2) return '#2a9d5c'
  if (s < -0.2) return '#d44'
  return '#f5a623'
})

const sentimentLabel = computed(() => {
  if (!attraction.value) return 'neutral'
  const s = attraction.value.sentiment_score
  if (s > 0.2) return 'positive'
  if (s < -0.2) return 'negative'
  return 'neutral'
})

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

const fetchData = async () => {
  loading.value = true
  try {
    const id = route.params.id
    const [aRes, rRes] = await Promise.all([
      attractionsAPI.get(id),
      reviewsAPI.list({ attraction_id: id, per_page: 50 })
    ])
    attraction.value = aRes.data
    reviews.value = rRes.data.reviews

    if (isLoggedIn.value) {
      try {
        const predRes = await recommendationsAPI.predictRating({ attraction_id: parseInt(id) })
        predictedRating.value = predRes.data.predicted_rating
        predictReason.value = predRes.data.reason || ''
      } catch (e) {
        console.error('Prediction failed', e)
      }
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const submitReview = async () => {
  submitting.value = true
  try {
    await reviewsAPI.create({
      attraction_id: parseInt(route.params.id),
      content: newReview.value.content,
      rating: newReview.value.rating
    })
    newReview.value.content = ''
    newReview.value.rating = 5
    await fetchData()
  } catch (e) {
    alert('Failed to submit review')
  } finally {
    submitting.value = false
  }
}

const deleteReview = async (id) => {
  if (!confirm('Delete this review?')) return
  try {
    await reviewsAPI.delete(id)
    await fetchData()
  } catch (e) {
    alert('Failed to delete review')
  }
}

onMounted(fetchData)
</script>

<style scoped>
.back-btn {
  margin-bottom: 1.5rem;
}

.detail-header {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

.detail-image {
  height: 350px;
  background-size: cover;
  background-position: center;
  border-radius: 12px;
}

.detail-info h1 {
  color: #1a5e63;
  margin-bottom: 0.5rem;
}

.location {
  color: #666;
  margin-bottom: 1rem;
}

.stats {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1rem;
}

.rating { color: #f5a623; font-weight: bold; }
.review-count { color: #888; }

.description {
  color: #555;
  line-height: 1.8;
  margin-bottom: 1.5rem;
}

.sentiment-summary h3, .predicted-rating h3 {
  font-size: 1rem;
  color: #1a5e63;
  margin-bottom: 0.5rem;
}

.sentiment-bar {
  height: 8px;
  background: #eee;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.3rem;
}

.sentiment-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s;
}

.sentiment-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: #888;
  margin-bottom: 0.5rem;
}

.sentiment-desc {
  font-size: 0.9rem;
  color: #555;
}

.pred-score {
  font-size: 1.8rem;
  color: #1a5e63;
  font-weight: bold;
}

.pred-reason {
  font-size: 0.9rem;
  color: #666;
  margin-top: 0.3rem;
}

.detail-section h2 {
  color: #1a5e63;
  margin-bottom: 1.2rem;
}

.review-form {
  margin-bottom: 2rem;
}

.rating-input {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.stars-input {
  display: flex;
  gap: 0.3rem;
}

.star {
  font-size: 1.5rem;
  cursor: pointer;
  color: #ddd;
  transition: color 0.2s;
}

.star.filled {
  color: #f5a623;
}

.review-form textarea {
  margin-bottom: 1rem;
  resize: vertical;
}

.login-prompt {
  text-align: center;
  padding: 2rem;
  background: white;
  border-radius: 10px;
  margin-bottom: 2rem;
}

.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.review-card {
  padding: 1rem 1.2rem;
}

.review-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.stars {
  color: #f5a623;
  letter-spacing: 2px;
}

.review-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 0.5rem;
}

.sentiment-badge {
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.sentiment-positive { background: #e6f9ee; color: #2a9d5c; }
.sentiment-neutral { background: #f0f0f0; color: #666; }
.sentiment-negative { background: #fee; color: #d44; }

.review-date {
  color: #aaa;
  font-size: 0.85rem;
}

.delete-btn {
  color: #d44;
  margin-left: auto;
}

@media (max-width: 768px) {
  .detail-header {
    grid-template-columns: 1fr;
  }
}
</style>
