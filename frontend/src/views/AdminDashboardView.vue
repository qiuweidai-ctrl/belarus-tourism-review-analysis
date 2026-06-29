<template>
  <div>
    <h1 class="page-title">Admin Dashboard</h1>

    <div v-if="loading" class="loading">{{ $t('common.loading') }}</div>
    <div v-else>
      <!-- Stats Cards -->
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

      <!-- Tabs -->
      <div class="tabs">
        <button v-for="tab in tabs" :key="tab.key" :class="{ active: activeTab === tab.key }" @click="activeTab = tab.key; loadTab()">
          {{ tab.label }}
        </button>
      </div>

      <!-- Users Tab -->
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

      <!-- Reviews Tab -->
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

      <!-- Attractions Tab -->
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
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminAPI } from '../api/client.js'

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
  { key: 'attractions', label: 'Attractions' }
]

const fetchStats = async () => {
  try {
    const res = await adminAPI.stats()
    stats.value = res.data
  } catch (e) { console.error(e) }
}

const loadTab = async () => {
  if (activeTab.value === 'users') await loadUsers()
  else if (activeTab.value === 'reviews') await loadReviews()
  else await loadAttractions()
}

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
.sort-select { padding: 0.4rem 0.8rem; border: 1px solid #ddd; border-radius: 6px; }
</style>
