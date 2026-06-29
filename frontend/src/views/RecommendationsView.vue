<template>
  <div>
    <h1 class="page-title">{{ $t('recommendations.title') }}</h1>
    <p class="subtitle">{{ $t('recommendations.subtitle') }}</p>

    <div v-if="loading" class="loading">{{ $t('common.loading') }}</div>
    <div v-else-if="!hasHistory" class="no-history card">
      <p>{{ $t('recommendations.noHistory') }}</p>
    </div>
    <div v-else>
      <div class="rec-actions">
        <button @click="fetchRecommendations" class="btn-secondary">{{ $t('recommendations.refresh') }}</button>
      </div>
      <div class="recommendations-grid">
        <div v-for="rec in recommendations" :key="rec.id" class="rec-card card">
          <h3>{{ rec.name }}</h3>
          <p class="rec-location">{{ rec.location }}</p>
          <p class="rec-desc">{{ rec.description }}</p>
          <div class="rec-footer">
            <span class="rec-rating">{{ $t('attractions.rating') }}: {{ rec.avg_rating }} / 5</span>
            <router-link :to="'/attractions/' + rec.id" class="btn-primary">{{ $t('attractions.viewDetails') }}</router-link>
          </div>
          <div class="rec-reason">
            <strong>{{ $t('recommendations.reason') }}:</strong> {{ rec.reason }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { recommendationsAPI } from '../api/client.js'

const recommendations = ref([])
const loading = ref(false)
const hasHistory = ref(true)

const fetchRecommendations = async () => {
  loading.value = true
  try {
    const res = await recommendationsAPI.get({ limit: 6 })
    recommendations.value = res.data.recommendations
    hasHistory.value = true
  } catch (e) {
    console.error(e)
    hasHistory.value = false
  } finally {
    loading.value = false
  }
}

onMounted(fetchRecommendations)
</script>

<style scoped>
.subtitle {
  color: #666;
  margin-bottom: 2rem;
}

.no-history {
  text-align: center;
  padding: 3rem;
  color: #888;
}

.rec-actions {
  margin-bottom: 1.5rem;
}

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
}

.rec-card {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.rec-card h3 {
  color: #1a5e63;
}

.rec-location {
  color: #888;
  font-size: 0.9rem;
}

.rec-desc {
  color: #555;
  font-size: 0.95rem;
  flex: 1;
}

.rec-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.5rem;
}

.rec-rating {
  color: #f5a623;
  font-weight: bold;
}

.rec-reason {
  margin-top: 0.8rem;
  padding-top: 0.8rem;
  border-top: 1px solid #eee;
  font-size: 0.9rem;
  color: #666;
  font-style: italic;
}
</style>
