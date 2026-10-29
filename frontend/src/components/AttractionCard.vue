<template>
  <article
    class="attraction-card card card-hover"
    tabindex="0"
    role="link"
    @click="open"
    @keydown.enter="open"
  >
    <div class="card-image" :style="imageStyle">
      <span v-if="attraction.is_featured" class="badge-featured" title="Editor's pick">★ Featured</span>
      <button
        v-if="isLoggedIn"
        class="wishlist-btn"
        :class="{ active: wishlisted }"
        :aria-pressed="wishlisted"
        :title="wishlisted ? 'Remove from wishlist' : 'Add to wishlist'"
        @click.stop="toggleWishlist"
      >
        {{ wishlisted ? '♥' : '♡' }}
      </button>
    </div>

    <div class="card-body">
      <h3>{{ attractionName(attraction) }}</h3>
      <p class="card-location">
        <span v-if="attraction.city">{{ formatPlace(attraction.city) }}</span>
        <span v-if="attraction.city && attraction.region" class="sep">·</span>
        <span v-if="attraction.region">{{ formatPlace(attraction.region) }}</span>
      </p>

      <div class="card-stats">
        <span class="rating">
          <span class="stars" aria-hidden="true">{{ stars }}</span>
          <strong>{{ attraction.avg_rating.toFixed(1) }}</strong>
        </span>
        <span class="reviews-count">{{ attraction.total_reviews }} {{ $t('attractions.reviews') }}</span>
      </div>

      <p v-if="shortDesc" class="card-desc">{{ shortDesc }}</p>

      <div class="card-foot">
        <span class="pill">{{ categoryLabel }}</span>
        <span class="spacer"></span>
        <span class="price" :class="{ free: !attraction.ticket_price }">
          {{ attraction.ticket_price ? attraction.ticket_price.toFixed(2) + ' BYN' : 'Free' }}
        </span>
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { wishlistAPI } from '@/api/client.js'
import { attractionName, formatCategory, formatPlace } from '@/utils/displayText.js'

const props = defineProps({
  attraction: { type: Object, required: true }
})

const router = useRouter()
const isLoggedIn = ref(!!localStorage.getItem('token'))
const wishlisted = ref(false)

const open = () => router.push('/attractions/' + props.attraction.id)

const imageStyle = computed(() => {
  if (props.attraction.image_url) {
    return { backgroundImage: `url(${props.attraction.image_url})` }
  }
  return { background: 'var(--grad-brand)' }
})

const stars = computed(() => {
  const full = Math.round(props.attraction.avg_rating || 0)
  return '★'.repeat(full) + '☆'.repeat(5 - full)
})

const shortDesc = computed(() => {
  const d = props.attraction.short_desc || props.attraction.description || ''
  return d.length > 110 ? d.slice(0, 110) + '…' : d
})

const categoryLabel = computed(() => {
  return formatCategory(props.attraction.category)
})

const toggleWishlist = async () => {
  try {
    const res = await wishlistAPI.toggle({ attraction_id: props.attraction.id })
    wishlisted.value = res.data.wishlisted
  } catch (e) {
    console.error(e)
  }
}

onMounted(async () => {
  if (isLoggedIn.value) {
    try {
      const res = await wishlistAPI.check(props.attraction.id)
      wishlisted.value = res.data.wishlisted
    } catch (_) { }
  }
})
</script>

<style scoped>
.attraction-card {
  cursor: pointer;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  outline: none;
}
.attraction-card:focus-visible { box-shadow: var(--ring), var(--shadow); }

.card-image {
  height: 175px;
  background-size: cover;
  background-position: center;
  position: relative;
  flex-shrink: 0;
}

.badge-featured {
  position: absolute;
  top: 10px; left: 10px;
  font-size: .7rem; font-weight: 700;
  padding: .22rem .55rem;
  border-radius: var(--radius-pill);
  background: rgba(255,255,255,.94);
  color: var(--brand-700);
  box-shadow: var(--shadow-xs);
}

.wishlist-btn {
  position: absolute;
  bottom: 10px; right: 10px;
  width: 34px; height: 34px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.94);
  font-size: 1.05rem;
  cursor: pointer;
  display: inline-flex; align-items: center; justify-content: center;
  box-shadow: var(--shadow-sm);
  transition: background-color 0.2s, transform 0.15s, color 0.2s;
  line-height: 1;
  padding: 0;
  color: var(--text-mute);
}
.wishlist-btn:hover { background: #fff; transform: scale(1.12); }
.wishlist-btn.active { color: #e91e63; }

.card-body { padding: .9rem 1rem 1rem; display: flex; flex-direction: column; flex: 1 1 auto; }

.card-body h3 {
  color: var(--text);
  margin: 0 0 .25rem;
  font-size: 1.02rem;
  line-height: 1.3;
}
.card-location {
  color: var(--text-mute);
  font-size: .8rem;
  margin: 0 0 .55rem;
}
.card-location .sep { margin: 0 .3rem; }

.card-stats {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: .55rem;
}
.rating { display: inline-flex; align-items: center; gap: .35rem; }
.stars { color: var(--accent-500); letter-spacing: 1px; font-size: .85rem; }
.rating strong { color: var(--accent-600); font-size: .88rem; }
.reviews-count { color: var(--text-mute); font-size: .78rem; }

.card-desc {
  color: var(--text-soft);
  font-size: .85rem;
  line-height: 1.5;
  margin: 0 0 .8rem;
  flex: 1 1 auto;
}

.card-foot { display: flex; align-items: center; gap: .5rem; }
.price { font-size: .84rem; font-weight: 700; color: var(--accent-600); }
.price.free { color: var(--success); }

@media (max-width: 520px) {
  .card-image { height: 150px; }
}
</style>
