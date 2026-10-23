<template>
  <div>
    <h1 class="page-title">Admin Dashboard</h1>

    <div v-if="loading" class="loading">{{ $t('common.loading') }}</div>
    <div v-else>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-number">{{ stats.user_count }}</div>
          <div class="stat-label">Total Users</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ stats.attraction_count }}</div>
          <div class="stat-label">Attractions</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ stats.review_count }}</div>
          <div class="stat-label">Published Reviews</div>
        </div>
        <div class="stat-card">
          <div class="stat-number warning">{{ stats.pending_reviews }}</div>
          <div class="stat-label">Pending Reviews</div>
        </div>
      </div>

      <div class="tabs">
        <button v-for="tab in tabs" :key="tab.key" :class="{ active: activeTab === tab.key }" @click="activeTab = tab.key; loadTab()">
          {{ tab.label }}
        </button>
      </div>

      <div v-if="activeTab === 'users'" class="tab-content">
        <div v-if="users.length === 0" class="empty">No users found.</div>
        <table v-else class="admin-table">
          <thead><tr>
            <th>ID</th><th>Username</th><th>Email</th><th>Role</th><th>Status</th><th>Joined</th><th>Actions</th>
          </tr></thead>
          <tbody>
            <tr v-for="u in users" :key="u.id">
              <td>{{ u.id }}</td>
              <td>{{ u.username }}</td>
              <td>{{ u.email }}</td>
              <td>
                <select v-model="u.role" @change="updateUserRole(u.id, 'role', u.role)" class="inline-select">
                  <option value="user">user</option>
                  <option value="admin">admin</option>
                  <option value="moderator">moderator</option>
                </select>
              </td>
              <td>
                <span :class="'status-badge status-' + u.status">{{ u.status }}</span>
              </td>
              <td>{{ formatDate(u.created_at) }}</td>
              <td>
                <button v-if="u.status === 'active'" @click="banUser(u.id)" class="btn-danger-sm">Ban</button>
                <button v-else @click="unbanUser(u.id)" class="btn-success-sm">Unban</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="activeTab === 'reviews'" class="tab-content">
        <div class="controls">
          <select v-model="reviewFilter" @change="loadReviews" class="sort-select">
            <option value="published">Published</option>
            <option value="pending">Pending</option>
            <option value="hidden">Hidden</option>
          </select>
        </div>
        <div v-if="reviews.length === 0" class="empty">No reviews found.</div>
        <table v-else class="admin-table">
          <thead><tr>
            <th>ID</th><th>User</th><th>Attraction</th><th>Rating</th><th>Sentiment</th><th>Status</th><th>Actions</th>
          </tr></thead>
          <tbody>
            <tr v-for="r in reviews" :key="r.id">
              <td>{{ r.id }}</td>
              <td>{{ r.username }}</td>
              <td>{{ r.attraction_name }}</td>
              <td>{{ r.rating }}/5</td>
              <td>
                <span v-if="r.sentiment_label" :class="'sentiment-badge sentiment-' + r.sentiment_label">{{ r.sentiment_label }}</span>
              </td>
              <td><span :class="'status-badge status-' + r.status">{{ r.status }}</span></td>
              <td>
                <button v-if="r.status === 'published'" @click="hideReview(r.id)" class="btn-danger-sm">Hide</button>
                <button v-if="r.status === 'hidden' || r.status === 'pending'" @click="approveReview(r.id)" class="btn-success-sm">Approve</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="activeTab === 'attractions'" class="tab-content">
        <div v-if="attractions.length === 0" class="empty">No attractions.</div>
        <table v-else class="admin-table">
          <thead><tr>
            <th>ID</th><th>Name</th><th>Category</th><th>Region</th><th>Rating</th><th>Reviews</th><th>Views</th><th>Featured</th><th>Actions</th>
          </tr></thead>
          <tbody>
            <tr v-for="a in attractions" :key="a.id">
              <td>{{ a.id }}</td>
              <td>{{ a.name }}</td>
              <td>{{ a.category }}</td>
              <td>{{ a.region }}</td>
              <td>{{ a.avg_rating }}</td>
              <td>{{ a.total_reviews }}</td>
              <td>{{ a.view_count }}</td>
              <td>
                <span v-if="a.is_featured" class="badge-featured">★ Featured</span>
              </td>
              <td>
                <button @click="toggleFeature(a.id)" class="btn-secondary-sm">{{ a.is_featured ? 'Unfeature' : 'Feature' }}</button>
                <button v-if="!a.is_verified" @click="verifyAttraction(a.id)" class="btn-success-sm">Verify</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="activeTab === 'login_events'" class="tab-content">
        <div class="evt-stats" v-if="loginEventStats && Object.keys(loginEventStats).length">
          <div class="stat-chip" v-for="(c, t) in loginEventStats" :key="t">
            <span class="chip-label">{{ t }}</span>
            <span class="chip-count">{{ c }}</span>
          </div>
        </div>
        <div class="evt-filters">
          <select v-model="evtTypeFilter" @change="loadLoginEvents">
            <option value="">All event types</option>
            <option value="login">login</option>
            <option value="logout">logout</option>
            <option value="register">register</option>
            <option value="login_failed">login_failed</option>
            <option value="token_refresh">token_refresh</option>
            <option value="password_changed">password_changed</option>
          </select>
        </div>
        <div v-if="loginEvents.length === 0" class="empty">No login events recorded yet.</div>
        <div v-else class="events-list">
          <div v-for="ev in loginEvents" :key="ev.id" class="event-row">
            <span class="evt-label" :class="'evt-' + ev.event_type">{{ ev.event_label }}</span>
            <span class="evt-time">{{ formatDateTime(ev.created_at) }}</span>
            <span class="evt-user">{{ ev.username || (ev.user_id ? '#' + ev.user_id : '—') }}</span>
            <span class="evt-ip">{{ ev.ip_address || '—' }}</span>
            <span :class="'evt-status status-' + ev.status">{{ ev.status }}</span>
            <span class="evt-detail">{{ ev.detail || '' }}</span>
          </div>
        </div>
        <div v-if="loginEventsPages > 1" class="pagination">
          <button @click="evtPage--; loadLoginEvents()" :disabled="evtPage <= 1" class="btn-secondary">Prev</button>
          <span>Page {{ evtPage }} / {{ loginEventsPages }}</span>
          <button @click="evtPage++; loadLoginEvents()" :disabled="evtPage >= loginEventsPages" class="btn-secondary">Next</button>
        </div>
      </div>

      <div v-if="activeTab === 'algorithms'" class="tab-content">
        <div class="algo-section">
          <h3>🎯 User Clustering (K-Means)</h3>
          <div class="algo-actions">
            <button @click="retrainClustering" class="btn-primary">🔄 Retrain Clustering Model</button>
          </div>
          <div v-if="clusterDistribution" class="cluster-grid">
            <div v-for="(info, name) in clusterDistribution" :key="name" class="cluster-card card">
              <h4>{{ name }}</h4>
              <div class="cluster-stat">
                <span class="stat-value">{{ info.count }}</span>
                <span class="stat-pct">{{ info.percentage }}%</span>
              </div>
              <button @click="showClusterUsers(name)" class="btn-secondary-sm">View Users</button>
            </div>
          </div>
        </div>

        <div class="algo-section">
          <h3>🔍 Duplicate Review Detection (MinHash/SimHash)</h3>
          <div class="algo-actions">
            <button @click="findDuplicates" class="btn-secondary">🔍 Find Duplicate Pairs</button>
            <button @click="rebuildDuplicateIndex" class="btn-secondary">🔄 Rebuild Index</button>
          </div>
          <div v-if="duplicatePairs.length > 0" class="duplicate-list">
            <div v-for="pair in duplicatePairs" :key="pair.review_1.id + '-' + pair.review_2.id" class="duplicate-card card">
              <div class="duplicate-header">
                <span class="similarity-tag">{{ pair.similarity }}% similar</span>
                <span class="same-author" v-if="pair.review_1.user_id === pair.review_2.user_id">Same Author!</span>
              </div>
              <div class="duplicate-pair">
                <div class="review-preview">
                  <strong>{{ pair.review_1.author }}</strong>
                  <p>{{ pair.review_1.content_preview }}...</p>
                  <small>{{ formatDate(pair.review_1.created_at) }}</small>
                </div>
                <div class="vs-divider">VS</div>
                <div class="review-preview">
                  <strong>{{ pair.review_2.author }}</strong>
                  <p>{{ pair.review_2.content_preview }}...</p>
                  <small>{{ formatDate(pair.review_2.created_at) }}</small>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="algo-section">
          <h3>📈 Trending Scores</h3>
          <div class="algo-actions">
            <button @click="recalculateTrending" class="btn-secondary">🔄 Recalculate All Scores</button>
          </div>
          <div class="trending-admin-list">
            <div v-for="item in topTrending" :key="item.attraction_id" class="trending-item card">
              <span class="trending-rank">#{{ topTrending.indexOf(item) + 1 }}</span>
              <span class="trending-name">{{ item.name }}</span>
              <span class="trending-score">Score: {{ item.score }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminAPI, algoAPI } from '@/api/client.js'

const stats = ref({})
const users = ref([])
const reviews = ref([])
const attractions = ref([])
const loading = ref(false)
const activeTab = ref('users')
const reviewFilter = ref('published')

const tabs = [
  { key: 'users', label: 'Users' },
  { key: 'reviews', label: 'Reviews' },
  { key: 'attractions', label: 'Attractions' },
  { key: 'login_events', label: 'Login Events' },
  { key: 'algorithms', label: 'AI Algorithms' }
]

const loginEvents = ref([])
const loginEventStats = ref({})
const evtPage = ref(1)
const loginEventsPages = ref(1)
const evtTypeFilter = ref('')
const clusterDistribution = ref(null)
const duplicatePairs = ref([])
const topTrending = ref([])

const fetchStats = async () => {
  try {
    const res = await adminAPI.stats()
    stats.value = res.data
  } catch (e) { console.error(e) }
}

const loadTab = async () => {
  if (activeTab.value === 'users') await loadUsers()
  else if (activeTab.value === 'reviews') await loadReviews()
  else if (activeTab.value === 'attractions') await loadAttractions()
  else if (activeTab.value === 'login_events') await loadLoginEvents()
  else if (activeTab.value === 'algorithms') {
    await loadClusterDistribution()
    await loadTopTrending()
    duplicatePairs.value = []
  }
}

const loadLoginEvents = async () => {
  loading.value = true
  try {
    const params = { page: evtPage.value, per_page: 30 }
    if (evtTypeFilter.value) params.event_type = evtTypeFilter.value
    const res = await adminAPI.loginEvents(params)
    loginEvents.value = res.data.events
    loginEventStats.value = res.data.type_stats || {}
    loginEventsPages.value = res.data.pages
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

const formatDateTime = (d) => d ? new Date(d).toLocaleString('en-US', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : ''

const loadUsers = async () => {
  loading.value = true
  try {
    const res = await adminAPI.users({ per_page: 50 })
    users.value = res.data.users
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

const loadReviews = async () => {
  loading.value = true
  try {
    const res = await adminAPI.reviews({ per_page: 50, status: reviewFilter.value })
    reviews.value = res.data.reviews
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

const loadAttractions = async () => {
  loading.value = true
  try {
    const res = await adminAPI.attractions({ per_page: 50 })
    attractions.value = res.data.attractions
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

const updateUserRole = async (id, field, value) => {
  try { await adminAPI.updateUser(id, { [field]: value }) } catch (e) { alert('Update failed') }
}
const banUser = async (id) => {
  try { await adminAPI.banUser(id); await loadUsers() } catch (e) { alert('Failed') }
}
const unbanUser = async (id) => {
  try { await adminAPI.unbanUser(id); await loadUsers() } catch (e) { alert('Failed') }
}
const hideReview = async (id) => {
  try { await adminAPI.hideReview(id); await loadReviews() } catch (e) { alert('Failed') }
}
const approveReview = async (id) => {
  try { await adminAPI.approveReview(id); await loadReviews() } catch (e) { alert('Failed') }
}
const toggleFeature = async (id) => {
  try { await adminAPI.toggleFeature(id); await loadAttractions() } catch (e) { alert('Failed') }
}
const verifyAttraction = async (id) => {
  try { await adminAPI.verifyAttraction(id); await loadAttractions() } catch (e) { alert('Failed') }
}
const formatDate = (d) => new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'short' })
const loadClusterDistribution = async () => {
  try {
    const res = await algoAPI.getClusterDistribution()
    clusterDistribution.value = res.data.data
  } catch (e) {
    console.error('Cluster distribution load failed', e)
  }
}

const retrainClustering = async () => {
  if (!confirm('Retrain clustering model? This may take a while.')) return
  loading.value = true
  try {
    const res = await algoAPI.retrainClustering()
    alert(res.data.message || 'Clustering retrained successfully')
    await loadClusterDistribution()
  } catch (e) {
    alert('Failed to retrain clustering: ' + (e.response?.data?.message || e.message))
  } finally {
    loading.value = false
  }
}

const showClusterUsers = async (clusterName) => {
  const clusterId = Object.keys(clusterDistribution.value || {}).indexOf(clusterName)
  if (clusterId >= 0) {
    try {
      const res = await algoAPI.getClusterUsers(clusterId)
      alert(`Found ${res.data.data.total} users in this cluster`)
    } catch (e) {
      console.error(e)
    }
  }
}

const findDuplicates = async () => {
  loading.value = true
  try {
    const res = await algoAPI.findDuplicatePairs({ min_similarity: 0.8, limit: 20 })
    duplicatePairs.value = res.data.data || []
    alert(`Found ${duplicatePairs.value.length} duplicate pairs`)
  } catch (e) {
    console.error('Find duplicates failed', e)
    alert('Failed to find duplicates')
  } finally {
    loading.value = false
  }
}

const rebuildDuplicateIndex = async () => {
  if (!confirm('Rebuild duplicate detection index?')) return
  loading.value = true
  try {
    const res = await algoAPI.rebuildDuplicateIndex()
    alert(res.data.message || 'Index rebuilt')
  } catch (e) {
    alert('Failed to rebuild index')
  } finally {
    loading.value = false
  }
}

const loadTopTrending = async () => {
  try {
    const res = await algoAPI.getTrending({ limit: 20 })
    topTrending.value = res.data.data || []
  } catch (e) {
    console.error('Trending load failed', e)
  }
}

const recalculateTrending = async () => {
  if (!confirm('Recalculate trending scores for all attractions?')) return
  loading.value = true
  try {
    const res = await algoAPI.recalculateTrending()
    alert(res.data.message || 'Trending scores recalculated')
    await loadTopTrending()
  } catch (e) {
    alert('Failed to recalculate trending')
  } finally {
    loading.value = false
  }
}

onMounted(async () => { await fetchStats(); await loadUsers() })
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
}
.stat-card {
  background: white;
  padding: 1.2rem;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  text-align: center;
}
.stat-number { font-size: 2rem; font-weight: bold; color: #1a5e63; }
.stat-number.warning { color: #f5a623; }
.stat-label { color: #888; font-size: 0.85rem; margin-top: 0.3rem; }

.tabs { display: flex; gap: 0; margin-bottom: 1.5rem; border-bottom: 2px solid #eee; }
.tabs button {
  padding: 0.6rem 1.5rem;
  border: none;
  background: none;
  cursor: pointer;
  color: #888;
  font-size: 0.95rem;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
}
.tabs button.active { color: #1a5e63; border-bottom-color: #1a5e63; font-weight: bold; }

.admin-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.admin-table th {
  background: #f5f7fa;
  padding: 0.8rem 1rem;
  text-align: left;
  font-size: 0.85rem;
  color: #888;
  border-bottom: 1px solid #eee;
}
.admin-table td {
  padding: 0.7rem 1rem;
  border-bottom: 1px solid #f5f7fa;
  font-size: 0.9rem;
}
.admin-table tr:hover td { background: #fafafa; }

.inline-select { font-size: 0.85rem; padding: 0.3rem 0.5rem; border: 1px solid #ddd; border-radius: 4px; }

.status-badge { padding: 0.2rem 0.6rem; border-radius: 10px; font-size: 0.75rem; font-weight: 600; }
.status-active { background: #e6f9ee; color: #2a9d5c; }
.status-banned { background: #fee; color: #d44; }
.status-published { background: #e6f9ee; color: #2a9d5c; }
.status-hidden { background: #fee; color: #d44; }
.status-pending { background: #fff3e0; color: #e67e00; }

.sentiment-badge { padding: 0.2rem 0.5rem; border-radius: 10px; font-size: 0.75rem; }
.sentiment-positive { background: #e6f9ee; color: #2a9d5c; }
.sentiment-neutral { background: #f0f0f0; color: #666; }
.sentiment-negative { background: #fee; color: #d44; }

.badge-featured { background: #f5a623; color: white; padding: 0.1rem 0.5rem; border-radius: 10px; font-size: 0.75rem; }

.btn-danger-sm { background: #fee; color: #d44; border: 1px solid #fcc; padding: 0.3rem 0.6rem; border-radius: 4px; cursor: pointer; font-size: 0.8rem; }
.btn-success-sm { background: #e6f9ee; color: #2a9d5c; border: 1px solid #cfc; padding: 0.3rem 0.6rem; border-radius: 4px; cursor: pointer; font-size: 0.8rem; }
.btn-secondary-sm { background: #f5f7fa; color: #555; border: 1px solid #ddd; padding: 0.3rem 0.6rem; border-radius: 4px; cursor: pointer; font-size: 0.8rem; }

.controls { margin-bottom: 1rem; }

.evt-stats { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem; }
.stat-chip { background: #f5f7fa; padding: 0.4rem 0.8rem; border-radius: 20px; font-size: 0.85rem; display: flex; gap: 0.4rem; align-items: center; }
.chip-label { color: #555; text-transform: capitalize; }
.chip-count  { color: #1a5e63; font-weight: 600; }

.evt-filters { margin-bottom: 1rem; }
.evt-filters select { padding: 0.4rem 0.6rem; border-radius: 4px; border: 1px solid #ddd; }

.events-list { display: flex; flex-direction: column; gap: 0.4rem; }
.event-row {
  display: grid;
  grid-template-columns: 140px 160px 120px 120px 90px 1fr;
  gap: 0.8rem; align-items: center;
  padding: 0.55rem 0.9rem; background: white;
  border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  font-size: 0.85rem;
}
.evt-label {
  font-weight: 600; padding: 0.15rem 0.55rem; border-radius: 10px;
  font-size: 0.78rem; color: white; text-align: center;
}
.evt-label.evt-login          { background: #1a5e63; }
.evt-label.evt-logout         { background: #888; }
.evt-label.evt-register       { background: #2a9d5c; }
.evt-label.evt-login_failed   { background: #d44; }
.evt-label.evt-token_refresh  { background: #1976d2; }
.evt-label.evt-password_changed { background: #f5a623; }
.evt-time  { color: #888; }
.evt-user  { color: #1a5e63; font-weight: 500; }
.evt-ip    { color: #555; font-family: monospace; }
.evt-status { font-size: 0.75rem; padding: 0.1rem 0.5rem; border-radius: 8px; text-align: center; }
.evt-detail { color: #888; font-style: italic; font-size: 0.8rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.status-success { background: #e6f9ee; color: #2a9d5c; }
.status-failure { background: #fee; color: #d44; }
.status-blocked { background: #fff3e0; color: #e67e00; }

@media (max-width: 900px) {
  .event-row { grid-template-columns: 1fr; gap: 0.3rem; }
}
.sort-select { padding: 0.4rem 0.8rem; border: 1px solid #ddd; border-radius: 6px; }

.algo-section {
  margin-bottom: 2.5rem;
}
.algo-section h3 {
  color: #1a5e63;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #eee;
}
.algo-actions {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.cluster-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}
.cluster-card {
  text-align: center;
  padding: 1.2rem;
}
.cluster-card h4 {
  color: #1a5e63;
  margin-bottom: 0.8rem;
  font-size: 0.95rem;
}
.cluster-stat {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 0.8rem;
}
.cluster-stat .stat-value {
  font-size: 1.8rem;
  font-weight: bold;
  color: #1a5e63;
}
.cluster-stat .stat-pct {
  font-size: 1rem;
  color: #888;
  align-self: flex-end;
}

.duplicate-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.duplicate-card {
  padding: 1rem;
}
.duplicate-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.8rem;
}
.similarity-tag {
  background: #fee;
  color: #d44;
  padding: 0.3rem 0.8rem;
  border-radius: 15px;
  font-weight: 600;
  font-size: 0.85rem;
}
.same-author {
  background: #fff3cd;
  color: #856404;
  padding: 0.3rem 0.8rem;
  border-radius: 15px;
  font-weight: 600;
  font-size: 0.85rem;
}
.duplicate-pair {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 1rem;
  align-items: center;
}
.vs-divider {
  color: #888;
  font-weight: bold;
  font-size: 0.9rem;
}
.review-preview {
  background: #f8f9fa;
  padding: 0.8rem;
  border-radius: 6px;
}
.review-preview strong {
  color: #1a5e63;
  font-size: 0.9rem;
}
.review-preview p {
  margin: 0.5rem 0;
  font-size: 0.85rem;
  color: #555;
}
.review-preview small {
  color: #888;
  font-size: 0.75rem;
}

.trending-admin-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.trending-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.8rem 1rem;
}
.trending-rank {
  width: 30px;
  height: 30px;
  background: #1a5e63;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 0.85rem;
}
.trending-name {
  flex: 1;
  color: #333;
}
.trending-score {
  color: #f5a623;
  font-weight: 600;
}
</style>
