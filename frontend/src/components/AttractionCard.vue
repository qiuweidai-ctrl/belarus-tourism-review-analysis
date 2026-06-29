<template>
  <div class="attraction-card card" @click="$router.push('/attractions/' + attraction.id)">
    <div class="card-image" :style="imageStyle"></div>
    <div class="card-body">
      <h3>{{ attraction.name }}</h3>
      <p class="card-location">{{ attraction.location }}</p>
      <div class="card-stats">
        <span class="rating">
          {{ '★'.repeat(Math.round(attraction.avg_rating)) }}{{ '☆'.repeat(5 - Math.round(attraction.avg_rating)) }}
          {{ attraction.avg_rating.toFixed(1) }}
        </span>
        <span class="reviews-count">{{ attraction.review_count }} {{ $t('attractions.reviews') }}</span>
      </div>
      <p class="card-desc">{{ shortDesc }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  attraction: {
    type: Object,
    required: true
  }
})

const imageStyle = computed(() => {
  if (props.attraction.image_url) {
    return { backgroundImage: `url(${props.attraction.image_url})` }
  }
  return { background: 'linear-gradient(135deg, #1a5e63, #2d8a8e)' }
})

const shortDesc = computed(() => {
  const d = props.attraction.description || ''
  return d.length > 100 ? d.slice(0, 100) + '...' : d
})
</script>

<style scoped>
.attraction-card {
  cursor: pointer;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}

.attraction-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.12);
}

.card-image {
  height: 180px;
  background-size: cover;
  background-position: center;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.card-body h3 {
  color: #1a5e63;
  margin-bottom: 0.3rem;
  font-size: 1.1rem;
}

.card-location {
  color: #888;
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
}

.card-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.rating {
  color: #f5a623;
  font-weight: bold;
  font-size: 0.95rem;
}

.reviews-count {
  color: #aaa;
  font-size: 0.85rem;
}

.card-desc {
  color: #666;
  font-size: 0.9rem;
  line-height: 1.5;
}
</style>
