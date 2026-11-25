<template>
  <a v-if="rating" class="external-rating-source" :href="rating.source_url"
     target="_blank" rel="noopener noreferrer" @click.stop @keydown.stop>
    <template v-if="showScore">{{ formatScoreNumber(rating.score) }} / {{ rating.scale }} · </template>{{ rating.provider }}<template v-if="showCount"> · {{ Number(rating.review_count).toLocaleString('en-US') }} {{ externalCountLabel(attraction) }}</template>
  </a>
</template>

<script setup>
import { computed } from 'vue'
import { externalCountLabel, formatScoreNumber } from '../utils/ratings.js'
const props = defineProps({
  attraction: { type: Object, required: true },
  showScore: { type: Boolean, default: true },
  showCount: { type: Boolean, default: true }
})
const rating = computed(() => props.attraction.primary_external_rating)
</script>

<style scoped>
.external-rating-source { font-size: .78rem; color: var(--text-mute); line-height: 1.5; overflow-wrap: anywhere; }
.external-rating-source:hover { color: var(--brand-600); text-decoration: underline; }
</style>
