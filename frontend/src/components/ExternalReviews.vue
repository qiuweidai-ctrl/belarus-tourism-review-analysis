<template>
  <section class="external-reviews detail-section" aria-labelledby="external-review-heading">
    <h2 id="external-review-heading">Visitor reviews from external platforms</h2>
    <p class="review-notice">Short excerpts in their original language. Authors and dates come from the source platform; these are not site-user reviews.</p>
    <p v-if="loading" role="status">Loading external reviews…</p>
    <p v-else-if="error" role="status">Could not load excerpts. You can still read the source platform below.</p>
    <div v-else-if="items.length" class="external-review-list">
      <article v-for="review in items" :key="review.id" class="card external-review">
        <header>
          <strong>{{ review.author_name }}</strong>
          <span class="pill">{{ review.provider }} · excerpt</span>
          <span v-if="review.score != null" class="individual-score">{{ review.score }} / {{ review.scale }}</span>
        </header>
        <blockquote :lang="review.original_language === 'und' ? undefined : review.original_language">{{ review.excerpt }}<span v-if="review.is_truncated">…</span></blockquote>
        <footer>
          <span>{{ review.source_date_kind === 'updated' ? 'Updated on source' : 'Published on source' }}: {{ sourceDate(review.source_date || review.published_at) }}</span>
          <span v-if="review.original_language !== 'und'">Language: {{ review.original_language }}</span>
          <a :href="review.source_url" target="_blank" rel="noopener noreferrer">Read on {{ review.provider }} ↗</a>
        </footer>
      </article>
    </div>
    <p v-else>No verified excerpt is available yet. This does not mean the platform has no reviews.</p>
    <div class="platform-links">
      <a v-for="source in attraction.external_ratings || []" :key="source.provider + source.provider_poi_id"
         :href="source.source_url" target="_blank" rel="noopener noreferrer">Open {{ source.provider }} page ↗</a>
    </div>
  </section>
</template>

<script setup>
import { ref, watch } from 'vue'
import { attractionsAPI } from '@/api/client.js'

const props = defineProps({ attraction: { type: Object, required: true } })
const items = ref([])
const loading = ref(false)
const error = ref(false)
let requestVersion = 0
const sourceDate = (value) => value ? value.slice(0, 10) : ''

watch(() => props.attraction.id, async (id) => {
  // 切换景点后忽略上一个景点的返回结果。
  const version = ++requestVersion
  items.value = []
  loading.value = true
  error.value = false
  try {
    const response = await attractionsAPI.externalReviews(id)
    if (version === requestVersion) items.value = response.data.items || []
  } catch (_) {
    if (version === requestVersion) error.value = true
  } finally {
    if (version === requestVersion) loading.value = false
  }
}, { immediate: true })
</script>

<style scoped>
.external-reviews { margin-top: 1.5rem; }
.review-notice { color: var(--text-soft); font-size: .86rem; line-height: 1.6; }
.external-review-list { display: grid; gap: 1rem; }
.external-review { padding: 1.1rem; }
.external-review header, .external-review footer { display: flex; flex-wrap: wrap; align-items: center; gap: .6rem; }
.individual-score { margin-left: auto; font-weight: 700; color: var(--brand-700); }
blockquote { margin: 1rem 0; padding-left: .9rem; border-left: 3px solid var(--brand-300); line-height: 1.7; overflow-wrap: anywhere; }
.external-review footer { font-size: .78rem; color: var(--text-mute); }
.external-review a, .platform-links a { color: var(--brand-700); text-decoration: underline; }
.platform-links { display: flex; flex-wrap: wrap; gap: 1rem; margin-top: 1rem; font-size: .86rem; }
</style>
