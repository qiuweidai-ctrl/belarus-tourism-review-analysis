<template>
  <div v-if="attraction">
    <button @click="goBack" class="btn-secondary back-btn">{{ $t('common.back') }}</button>

    <div class="detail-header">
      <div class="detail-image-wrap">
        <div
          class="detail-image"
          :class="{ 'is-editable': canEditImage }"
          :style="imageStyle"
          :title="canEditImage ? 'Click to change the main image' : ''"
          @click="onImageClick"
        ></div>
        <input
          v-if="canEditImage"
          ref="imageFileInput"
          type="file"
          accept="image/png,image/jpeg,image/jpg,image/gif,image/webp"
          style="display:none"
          @change="onImageFileChange"
        />
        <button
          v-if="canEditImage"
          type="button"
          class="detail-image-edit-btn"
          @click.stop="onImageClick"
          :disabled="imageUploading"
        >
          <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor" aria-hidden="true">
            <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04a1 1 0 0 0 0-1.41l-2.34-2.34a1 1 0 0 0-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
          </svg>
          <span>{{ imageUploading ? 'Uploading...' : 'Change Image' }}</span>
        </button>
        <p v-if="imageUploadError" class="error-msg image-upload-error">{{ imageUploadError }}</p>
      </div>
      <div class="detail-info">
        <div class="detail-title-row">
          <h1>{{ attractionName(attraction) }}</h1>
          <button
            v-if="isLoggedIn"
            class="wishlist-detail-btn"
            :class="{ active: wishlisted }"
            @click="toggleWishlist"
            :title="wishlisted ? 'Remove from wishlist' : 'Add to wishlist'"
          >
            {{ wishlisted ? '♥ Saved' : '♡ Save' }}
          </button>
        </div>
        <p class="location">{{ formatPlace(attraction.location) }}</p>
        <div class="stats">
          <span class="rating">{{ $t('attractions.rating') }}: {{ attraction.avg_rating }} / 5</span>
          <span class="review-count">{{ attraction.review_count }} {{ $t('attractions.reviews') }}</span>
        </div>
        <p class="description">{{ attraction.description }}</p>

        <div v-if="aiSummary" class="ai-summary card">
          <h3>🤖 AI Generated Summary</h3>
          <p>{{ aiSummary }}</p>
        </div>

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

    <div v-if="similarAttractions.length > 0" class="similar-attractions">
      <h2>✨ Similar Attractions (TF-IDF)</h2>
      <div class="similar-grid">
        <div
          v-for="item in similarAttractions"
          :key="item.attraction_id"
          class="similar-card card"
          @click="goToAttraction(item.attraction_id)"
        >
          <div v-if="item.image_url" class="similar-img" :style="{ backgroundImage: `url(${item.image_url})` }"></div>
          <div v-else class="similar-img placeholder"></div>
          <div class="similar-info">
            <h4>{{ item.name }}</h4>
            <p class="similar-location">{{ formatPlace(item.location) }}</p>
            <div class="similar-meta">
              <span class="rating">★ {{ item.avg_rating }}</span>
              <span class="similarity-badge">{{ item.similarity }}% match</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="topQualityReviews.length > 0" class="top-reviews-section">
      <h2>🏆 Top Quality Reviews</h2>
      <div class="reviews-list">
        <div v-for="item in topQualityReviews" :key="item.review_id" class="review-card card highlight">
          <div class="review-quality-badge">
            <span class="quality-score" :class="'grade-' + item.quality.grade">{{ item.quality.grade }}</span>
            <span class="quality-label">{{ item.quality.label }}</span>
            <span class="quality-number">{{ item.quality.quality_score }} points</span>
          </div>
          <div class="review-top">
            <strong>{{ item.review.author }}</strong>
            <span class="stars">{{ '★'.repeat(item.review.rating) }}{{ '☆'.repeat(5 - item.review.rating) }}</span>
          </div>
          <p>{{ item.review.content }}</p>
          <div class="review-meta">
            <span class="helpful-count">👍 {{ item.review.helpful_count }} helpful</span>
            <span class="review-date">{{ formatDate(item.review.created_at) }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="detail-section">
      <h2>{{ $t('attractionDetail.reviews') }}</h2>

      <div v-if="isLoggedIn" class="review-form card">
        <h3>{{ $t('attractionDetail.writeReview') }}</h3>
        <div v-if="duplicateWarning" class="duplicate-warning">
          <span class="warning-icon">⚠️</span>
          <span>{{ duplicateWarning }}</span>
        </div>
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
          @blur="checkDuplicate"
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
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { attractionsAPI, reviewsAPI, recommendationsAPI, wishlistAPI, algoAPI } from '@/api/client.js'
import { attractionName, formatPlace } from '@/utils/displayText.js'

const route = useRoute()
const router = useRouter()
const attraction = ref(null)
const reviews = ref([])
const loading = ref(true)
const submitting = ref(false)
const isLoggedIn = ref(!!localStorage.getItem('token'))
const similarAttractions = ref([])
const topQualityReviews = ref([])
const aiSummary = ref('')
const duplicateWarning = ref('')
let duplicateCheckTimer = null

function goBack() {
  const ref = router.getReferrer(route.fullPath)
  router.clearReferrer(route.fullPath)
  router.clearScroll(route.fullPath)
  if (ref) {
    router.push(ref)
  } else if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/')
  }
}
const currentUserId = ref(parseInt(localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')).id : '0'))

const newReview = ref({ content: '', rating: 5 })
const predictedRating = ref(null)
const predictReason = ref('')
const wishlisted = ref(false)
const imageFileInput = ref(null)
const imageUploading = ref(false)
const imageUploadError = ref('')
const currentUser = ref(null)
const currentUserRole = ref('')
const imageCacheBust = ref(0)

const ALLOWED_IMG_TYPES = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp']
const MAX_IMG_SIZE = 8 * 1024 * 1024
const canEditImage = computed(() => {
  if (!isLoggedIn.value || !attraction.value || !currentUser.value) return false
  if (currentUserRole.value === 'admin') return true
  return attraction.value.created_by === currentUser.value.id
})

const imageStyle = computed(() => {
  const url = attraction.value?.image_url
  if (url) {
    const sep = url.includes('?') ? '&' : '?'
    return { backgroundImage: `url(${url}${sep}t=${imageCacheBust.value})` }
  }
  return { background: 'linear-gradient(135deg, #1a5e63, #2d8a8e)' }
})

function onImageClick() {
  if (!canEditImage.value || imageUploading.value) return
  imageUploadError.value = ''
  imageFileInput.value && imageFileInput.value.click()
}

function validateImageFile(f) {
  if (!ALLOWED_IMG_TYPES.includes(f.type)) {
    return `Unsupported file format: ${f.type || 'unknown'}. Please use PNG / JPG / GIF / WebP.`
  }
  if (f.size > MAX_IMG_SIZE) {
    return `File too large: ${(f.size / 1024 / 1024).toFixed(2)} MB, max 8 MB.`
  }
  return ''
}

async function onImageFileChange(e) {
  const f = e.target.files && e.target.files[0]
  if (imageFileInput.value) imageFileInput.value.value = ''
  if (!f) return
  const err = validateImageFile(f)
  if (err) {
    imageUploadError.value = err
    return
  }
  imageUploadError.value = ''
  imageUploading.value = true
  try {
    const id = parseInt(route.params.id)
    const res = await attractionsAPI.uploadImage(id, f)
    if (res.data && res.data.attraction) {
      attraction.value = res.data.attraction
    } else if (res.data && res.data.image_url) {
      attraction.value = { ...attraction.value, image_url: res.data.image_url }
    }
    imageCacheBust.value = Date.now()
  } catch (e2) {
    imageUploadError.value = e2.response?.data?.error || 'Image upload failed, please try again'
  } finally {
    imageUploading.value = false
  }
}

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
    try {
      const u = JSON.parse(localStorage.getItem('user') || 'null')
      currentUser.value = u
      currentUserRole.value = (u && u.role) || ''
    } catch (_) { currentUser.value = null; currentUserRole.value = '' }

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
      try {
        const wlRes = await wishlistAPI.check(id)
        wishlisted.value = wlRes.data.wishlisted
      } catch (_) {}
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}
const fetchAlgoData = async () => {
  const id = route.params.id
  try {
    const simRes = await algoAPI.getSimilarAttractions(id, { top_k: 4 })
    similarAttractions.value = simRes.data.data || []
  } catch (e) {
    console.error('Similar attractions fetch failed', e)
  }
  try {
    const qualRes = await algoAPI.getTopQualityReviews(id, { limit: 3 })
    topQualityReviews.value = qualRes.data.data || []
  } catch (e) {
    console.error('Top quality reviews fetch failed', e)
  }
  try {
    const sumRes = await algoAPI.getAttractionSummary(id)
    aiSummary.value = sumRes.data.data?.summary || ''
  } catch (e) {
    console.error('AI summary fetch failed', e)
  }
}
const checkDuplicate = async () => {
  if (!newReview.value.content || newReview.value.content.length < 50) {
    duplicateWarning.value = ''
    return
  }
  if (duplicateCheckTimer) clearTimeout(duplicateCheckTimer)

  duplicateCheckTimer = setTimeout(async () => {
    try {
      const res = await algoAPI.checkDuplicate({ content: newReview.value.content })
      if (res.data.data?.is_duplicate) {
        const maxSim = res.data.data.max_similarity
        if (res.data.data.warning_level === 'high') {
          duplicateWarning.value = `⚠️ Your review is ${maxSim}% similar to existing content. Please write original content.`
        } else if (res.data.data.warning_level === 'medium') {
          duplicateWarning.value = `⚡ Your review has ${maxSim}% similarity to existing content.`
        }
      } else {
        duplicateWarning.value = ''
      }
    } catch (e) {
      console.error('Duplicate check failed', e)
    }
  }, 1000)
}

const goToAttraction = (id) => {
  router.push(`/attractions/${id}`)
}

const loadAttractionPage = async () => {
  attraction.value = null
  reviews.value = []
  similarAttractions.value = []
  topQualityReviews.value = []
  aiSummary.value = ''
  predictedRating.value = null
  predictReason.value = ''
  wishlisted.value = false
  await Promise.all([fetchData(), fetchAlgoData()])
  window.scrollTo({ top: 0, behavior: 'smooth' })
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
    duplicateWarning.value = ''
    await fetchData()
    await fetchAlgoData()
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

const toggleWishlist = async () => {
  if (!isLoggedIn.value) return
  try {
    const res = await wishlistAPI.toggle({ attraction_id: parseInt(route.params.id) })
    wishlisted.value = res.data.wishlisted
  } catch (e) {
    console.error(e)
  }
}

watch(() => route.params.id, (id, previousId) => {
  if (id && id !== previousId) loadAttractionPage()
})

onMounted(loadAttractionPage)
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

.detail-image-wrap {
  position: relative;
}
.detail-image {
  height: 350px;
  background-size: cover;
  background-position: center;
  border-radius: 12px;
}
.detail-image.is-editable { cursor: pointer; transition: filter 0.15s ease, box-shadow 0.15s ease; }
.detail-image.is-editable:hover {
  box-shadow: 0 0 0 3px rgba(26, 94, 99, 0.4);
  filter: brightness(0.92);
}
.detail-image-edit-btn {
  position: absolute;
  right: 10px; bottom: 10px;
  display: inline-flex; align-items: center; gap: 0.35rem;
  padding: 0.4rem 0.75rem;
  border: none; border-radius: 20px;
  background: rgba(26, 94, 99, 0.92);
  color: #fff; font-size: 0.8rem; font-weight: 600;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(0,0,0,0.25);
  transition: background 0.15s ease;
}
.detail-image-edit-btn:hover { background: #1a5e63; }
.detail-image-edit-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.image-upload-error {
  position: absolute;
  left: 10px; bottom: 10px;
  margin: 0; padding: 0.4rem 0.7rem;
  font-size: 0.8rem;
  background: #fee; border: 1px solid #fcc; color: #c33;
  border-radius: 6px;
  max-width: calc(100% - 20px);
}

.detail-info h1 {
  color: #1a5e63;
  margin-bottom: 0.5rem;
}

.detail-title-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.wishlist-detail-btn {
  padding: 0.4rem 1rem;
  border-radius: 20px;
  border: 1.5px solid #ddd;
  background: #fff;
  color: #888;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  transition: border-color 0.2s, color 0.2s, background 0.2s;
  white-space: nowrap;
}
.wishlist-detail-btn:hover {
  border-color: #e91e63;
  color: #e91e63;
}
.wishlist-detail-btn.active {
  border-color: #e91e63;
  color: #e91e63;
  background: #fce4ec;
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

.ai-summary {
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-left: 4px solid #6c5ce7;
  margin-bottom: 1rem;
}
.ai-summary h3 {
  font-size: 0.95rem;
  color: #6c5ce7;
  margin-bottom: 0.5rem;
}
.ai-summary p {
  color: #495057;
  line-height: 1.7;
}

.similar-attractions, .top-reviews-section {
  margin-bottom: 2rem;
}
.similar-attractions h2, .top-reviews-section h2 {
  color: #1a5e63;
  margin-bottom: 1rem;
}
.similar-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
}
.similar-card {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  overflow: hidden;
  padding: 0;
}
.similar-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}
.similar-img {
  height: 120px;
  background-size: cover;
  background-position: center;
}
.similar-img.placeholder {
  background: linear-gradient(135deg, #1a5e63, #2d8a8e);
}
.similar-info {
  padding: 0.8rem;
}
.similar-info h4 {
  margin: 0 0 0.3rem 0;
  color: #1a5e63;
  font-size: 0.95rem;
}
.similar-location {
  color: #888;
  font-size: 0.8rem;
  margin-bottom: 0.5rem;
}
.similar-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.similarity-badge {
  background: #e8f4f8;
  color: #1a5e63;
  padding: 0.2rem 0.5rem;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: 600;
}

.review-card.highlight {
  border-left: 4px solid #f5a623;
}
.review-quality-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}
.quality-score {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: white;
}
.quality-score.grade-A { background: #2a9d5c; }
.quality-score.grade-B { background: #4dabf7; }
.quality-score.grade-C { background: #f5a623; }
.quality-score.grade-D { background: #e8590c; }
.quality-label {
  font-size: 0.85rem;
  color: #666;
}
.quality-number {
  margin-left: auto;
  font-weight: bold;
  color: #1a5e63;
}

.duplicate-warning {
  background: #fff3cd;
  border: 1px solid #ffc107;
  color: #856404;
  padding: 0.6rem 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
}
.warning-icon {
  font-size: 1.1rem;
}
</style>
