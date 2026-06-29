<template>
  <div class="home">
    <section class="hero">
      <div class="hero-content">
        <h1>{{ $t('home.hero') }}</h1>
        <p>{{ $t('home.heroSub') }}</p>
        <button @click="$router.push('/attractions')" class="btn-primary">{{ $t('home.exploreBtn') }}</button>
      </div>
    </section>

    <section class="section">
      <h2 class="section-title">{{ $t('home.featured') }}</h2>
      <div v-if="loading" class="loading">{{ $t('common.loading') }}</div>
      <div v-else-if="attractions.length === 0" class="loading">{{ $t('home.noAttractions') }}</div>
      <div v-else class="attractions-grid">
        <AttractionCard v-for="a in attractions" :key="a.id" :attraction="a" />
      </div>
    </section>

    <section class="section">
      <h2 class="section-title">{{ $t('home.recentReviews') }}</h2>
      <div v-if="recentReviews.length === 0" class="loading">{{ $t('attractionDetail.noReviews') }}</div>
      <div v-else class="reviews-list">
        <div v-for="r in recentReviews" :key="r.id" class="review-item card">
          <div class="review-header">
            <strong>{{ r.username }}</strong>
          </div>
          <p class="review-content">{{ r.content }}</p>
          <div class="review-footer">
            <span class="stars">{{ '★'.repeat(r.rating) }}{{ '☆'.repeat(5 - r.rating) }}</span>
            <span :class="'sentiment-badge sentiment-' + r.sentiment_label">{{ r.sentiment_label }}</span>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { attractionsAPI, reviewsAPI } from '../api/client.js'
import AttractionCard from '../components/AttractionCard.vue'

const attractions = ref([])
const recentReviews = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await attractionsAPI.list({ per_page: 6, sort: 'rating' })
    attractions.value = res.data.attractions
    const revRes = await reviewsAPI.list({ per_page: 5 })
    recentReviews.value = revRes.data.reviews
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.hero {
  background: linear-gradient(135deg, #1a5e63, #2d8a8e);
  color: white;
  padding: 4rem 2rem;
  border-radius: 16px;
  text-align: center;
  margin-bottom: 2rem;
}

.hero h1 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.hero p {
  font-size: 1.1rem;
  opacity: 0.9;
  margin-bottom: 1.5rem;
}

.section {
  margin-bottom: 3rem;
}

.section-title {
  font-size: 1.5rem;
  color: #1a5e63;
  margin-bottom: 1.2rem;
}

.attractions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.review-item {
  padding: 1rem 1.2rem;
}

.review-header {
  margin-bottom: 0.5rem;
}

.review-content {
  color: #555;
  margin-bottom: 0.5rem;
}

.review-footer {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stars {
  color: #f5a623;
  letter-spacing: 2px;
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
</style>
