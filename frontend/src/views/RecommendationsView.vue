<template>
  <div>
    <h1 class="page-title">🎯 Smart Recommendations</h1>
    <p class="subtitle">AI-powered personalized suggestions based on your preferences and behavior</p>

    <div v-if="loading" class="loading">Loading recommendations...</div>
    <div v-else>
      <div v-if="userCluster && isLoggedIn" class="cluster-info card">
        <div class="cluster-badge">
          <span class="cluster-icon">👤</span>
          <div>
            <h3>Your User Segment</h3>
            <p class="cluster-name">{{ userCluster.cluster_name }}</p>
          </div>
        </div>
        <div class="cluster-features">
          <div class="feature-item">
            <span class="feature-label">Museum Preference</span>
            <div class="feature-bar">
              <div class="feature-fill" :style="{ width: (userCluster.features?.museum_preference * 100) + '%' }"></div>
            </div>
          </div>
          <div class="feature-item">
            <span class="feature-label">Nature Preference</span>
            <div class="feature-bar">
              <div class="feature-fill nature" :style="{ width: (userCluster.features?.nature_preference * 100) + '%' }"></div>
            </div>
          </div>
          <div class="feature-item">
            <span class="feature-label">History Preference</span>
            <div class="feature-bar">
              <div class="feature-fill history" :style="{ width: (userCluster.features?.history_preference * 100) + '%' }"></div>
            </div>
          </div>
        </div>
      </div>

      <div class="section">
        <h2>🔥 Trending Now (Weighted Algorithm)</h2>
        <p class="section-desc">Based on recent reviews, ratings, and sentiment scores with time decay</p>
        <div class="trending-grid">
          <div v-for="item in trendingAttractions" :key="item.attraction_id" class="trending-card card" @click="goToAttraction(item.attraction_id)">
            <div class="trending-score">
              <span class="score-value">{{ item.trending_score }}</span>
              <span class="score-label">score</span>
            </div>
            <div class="trending-info">
              <h3>{{ item.name }}</h3>
              <p class="trending-location">{{ item.location }}</p>
              <div class="trending-meta">
                <span class="rating">★ {{ item.avg_rating }}</span>
                <span class="reviews">{{ item.total_reviews }} reviews</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="isLoggedIn" class="section">
        <h2>✨ Personalized For You (TF-IDF + Cosine Similarity)</h2>
        <p class="section-desc">Based on your review history and preferences</p>
        <div class="rec-actions">
          <button @click="fetchPersonalRecs" class="btn-secondary">🔄 Refresh</button>
        </div>
        <div v-if="personalRecs.length > 0" class="recs-grid">
          <div v-for="item in personalRecs" :key="item.attraction_id" class="rec-card card" @click="goToAttraction(item.attraction_id)">
            <div class="rec-header">
              <h3>{{ item.name }}</h3>
              <span class="match-badge">{{ item.similarity_score }}% match</span>
            </div>
            <p class="rec-location">{{ item.location }}</p>
            <div class="rec-footer">
              <span class="rating">★ {{ item.avg_rating }}</span>
            </div>
          </div>
        </div>
        <div v-else class="no-recs">
          <p>Explore more attractions to get personalized recommendations!</p>
        </div>
      </div>
      <div v-else class="login-prompt card">
        <p>Login to see personalized recommendations based on your preferences</p>
        <router-link to="/login" class="btn-primary">Login</router-link>
      </div>

      <div class="section">
        <h2>📊 Attraction Categories</h2>
        <div class="category-tabs">
          <button
            v-for="cat in categories"
            :key="cat"
            :class="{ active: selectedCategory === cat }"
            @click="selectCategory(cat)"
            class="category-tab"
          >
            {{ cat }}
          </button>
        </div>
        <div v-if="categoryRecs.length > 0" class="recs-grid">
          <div v-for="item in categoryRecs" :key="item.attraction_id" class="rec-card card" @click="goToAttraction(item.attraction_id)">
            <h3>{{ item.name }}</h3>
            <p class="rec-location">{{ item.location }}</p>
            <div class="rec-footer">
              <span class="rating">★ {{ item.avg_rating }}</span>
              <span class="score">{{ item.score }} trending</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { algoAPI } from '@/api/client.js'

const router = useRouter()
const loading = ref(false)
const isLoggedIn = ref(!!localStorage.getItem('token'))
const userCluster = ref(null)
const trendingAttractions = ref([])
const personalRecs = ref([])
const categories = ['museum', 'nature', 'castle', 'church', 'palace', 'park']
const selectedCategory = ref('museum')
const categoryRecs = ref([])

const fetchTrending = async () => {
  try {
    const res = await algoAPI.getTrending({ limit: 6 })
    trendingAttractions.value = res.data.data || []
  } catch (e) {
    console.error('Trending fetch failed', e)
  }
}

const fetchUserCluster = async () => {
  if (!isLoggedIn.value) return
  try {
    const res = await algoAPI.getMyCluster()
    userCluster.value = res.data.data
  } catch (e) {
    console.error('User cluster fetch failed', e)
  }
}

const fetchPersonalRecs = async () => {
  if (!isLoggedIn.value) return
  loading.value = true
  try {
    const res = await algoAPI.getPersonalRecommendations({ top_k: 6 })
    personalRecs.value = res.data.data || []
  } catch (e) {
    console.error('Personal recs fetch failed', e)
  } finally {
    loading.value = false
  }
}

const fetchCategoryRecs = async (category) => {
  try {
    const res = await algoAPI.getTrendingByCategory(category, { limit: 6 })
    categoryRecs.value = res.data.data || []
  } catch (e) {
    console.error('Category recs fetch failed', e)
  }
}

const selectCategory = (cat) => {
  selectedCategory.value = cat
  fetchCategoryRecs(cat)
}

const goToAttraction = (id) => {
  router.push(`/attractions/${id}`)
}

onMounted(async () => {
  loading.value = true
  await Promise.all([
    fetchTrending(),
    fetchUserCluster(),
    fetchPersonalRecs(),
    fetchCategoryRecs(selectedCategory.value)
  ])
  loading.value = false
})
</script>

<style scoped>
.subtitle {
  color: #666;
  margin-bottom: 2rem;
}

.cluster-info {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  margin-bottom: 2rem;
}
.cluster-badge {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}
.cluster-icon {
  font-size: 2.5rem;
}
.cluster-name {
  font-size: 1.2rem;
  font-weight: bold;
  margin-top: 0.2rem;
}
.cluster-features {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}
.feature-item {
  background: rgba(255,255,255,0.2);
  padding: 0.8rem;
  border-radius: 8px;
}
.feature-label {
  font-size: 0.8rem;
  display: block;
  margin-bottom: 0.3rem;
}
.feature-bar {
  height: 6px;
  background: rgba(255,255,255,0.3);
  border-radius: 3px;
  overflow: hidden;
}
.feature-fill {
  height: 100%;
  background: #ffd32a;
  border-radius: 3px;
  transition: width 0.5s;
}
.feature-fill.nature { background: #26de81; }
.feature-fill.history { background: #fd9644; }

.section {
  margin-bottom: 2.5rem;
}
.section h2 {
  color: #1a5e63;
  margin-bottom: 0.5rem;
}
.section-desc {
  color: #888;
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.trending-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}
.trending-card {
  display: flex;
  gap: 1rem;
  cursor: pointer;
  transition: transform 0.2s;
}
.trending-card:hover {
  transform: translateX(4px);
}
.trending-score {
  background: linear-gradient(135deg, #ff6b6b, #ee5a24);
  color: white;
  padding: 1rem;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-width: 70px;
}
.score-value {
  font-size: 1.5rem;
  font-weight: bold;
}
.score-label {
  font-size: 0.7rem;
}
.trending-info {
  flex: 1;
}
.trending-info h3 {
  color: #1a5e63;
  margin-bottom: 0.3rem;
}
.trending-location {
  color: #888;
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
}
.trending-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.85rem;
}
.trending-meta .rating {
  color: #f5a623;
  font-weight: bold;
}

.rec-actions {
  margin-bottom: 1rem;
}
.recs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}
.rec-card {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}
.rec-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.1);
}
.rec-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.5rem;
}
.rec-header h3 {
  color: #1a5e63;
  margin: 0;
}
.match-badge {
  background: #e8f4f8;
  color: #1a5e63;
  padding: 0.2rem 0.5rem;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
}
.rec-location {
  color: #888;
  font-size: 0.85rem;
  margin: 0.3rem 0;
}
.rec-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 0.5rem;
}
.rec-footer .rating {
  color: #f5a623;
  font-weight: bold;
}
.rec-footer .score {
  color: #ff6b6b;
  font-weight: 600;
}

.category-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}
.category-tab {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  background: white;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s;
}
.category-tab:hover {
  border-color: #1a5e63;
  color: #1a5e63;
}
.category-tab.active {
  background: #1a5e63;
  color: white;
  border-color: #1a5e63;
}

.no-recs, .login-prompt {
  text-align: center;
  padding: 2rem;
  color: #888;
}

@media (max-width: 768px) {
  .cluster-features {
    grid-template-columns: 1fr;
  }
}
</style>
