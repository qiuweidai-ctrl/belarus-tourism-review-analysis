<template>
  <div>
    <h1 class="page-title">My Profile</h1>

    <!-- Profile Info Card -->
    <div class="profile-header card">
      <div class="avatar-section">
        <div class="avatar" :style="avatarStyle">{{ initials }}</div>
        <div class="profile-info">
          <h2>{{ profile.username }}</h2>
          <p v-if="profile.nickname" class="nickname">{{ profile.nickname }}</p>
          <p class="email">{{ profile.email }}</p>
          <span :class="'role-badge role-' + profile.role">{{ profile.role }}</span>
        </div>
      </div>
      <div class="profile-meta">
        <p>Member since: {{ formatDate(profile.created_at) }}</p>
        <p v-if="profile.bio">{{ profile.bio }}</p>
      </div>
      <button @click="showEditForm = !showEditForm" class="btn-secondary">{{ showEditForm ? 'Cancel' : 'Edit Profile' }}</button>
    </div>

    <!-- Edit Form -->
    <div v-if="showEditForm" class="edit-form card">
      <h3>Edit Profile</h3>
      <div v-if="editError" class="error-msg">{{ editError }}</div>
      <div v-if="editSuccess" class="success-msg">{{ editSuccess }}</div>
      <div class="form-group">
        <label>Nickname</label>
        <input v-model="editForm.nickname" type="text" />
      </div>
      <div class="form-group">
        <label>Avatar URL</label>
        <input v-model="editForm.avatar_url" type="text" placeholder="https://..." />
      </div>
      <div class="form-group">
        <label>Bio</label>
        <textarea v-model="editForm.bio" rows="3" placeholder="Tell us about yourself..."></textarea>
      </div>
      <div class="form-group">
        <label>Current Password (required for password change)</label>
        <input v-model="editForm.current_password" type="password" />
      </div>
      <div class="form-group">
        <label>New Password</label>
        <input v-model="editForm.new_password" type="password" />
      </div>
      <button @click="saveProfile" :disabled="saving" class="btn-primary">
        {{ saving ? 'Saving...' : 'Save Changes' }}
      </button>
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button v-for="tab in tabs" :key="tab.key" :class="{ active: activeTab === tab.key }" @click="activeTab = tab.key; loadTab()">
        {{ tab.label }} <span class="tab-count">{{ tabCounts[tab.key] }}</span>
      </button>
    </div>

    <!-- My Reviews -->
    <div v-if="activeTab === 'reviews'" class="tab-content">
      <div v-if="reviews.length === 0" class="empty">You have not written any reviews yet.</div>
      <div v-else class="reviews-list">
        <div v-for="r in reviews" :key="r.id" class="review-item card">
          <div class="review-top">
            <router-link :to="'/attractions/' + r.attraction_id" class="review-attr-link">{{ r.attraction_id }}</router-link>
            <span>{{ '★'.repeat(r.rating) }}{{ '☆'.repeat(5 - r.rating) }}</span>
          </div>
          <p v-if="r.title" class="review-title">{{ r.title }}</p>
          <p class="review-content">{{ r.content.slice(0, 200) }}{{ r.content.length > 200 ? '...' : '' }}</p>
          <div class="review-footer">
            <span :class="'sentiment-badge sentiment-' + r.sentiment_label">{{ r.sentiment_label }}</span>
            <span class="review-date">{{ formatDate(r.created_at) }}</span>
            <button @click="deleteReview(r.id)" class="btn-link delete-btn">Delete</button>
          </div>
        </div>
      </div>
    </div>

    <!-- My Wishlist -->
    <div v-if="activeTab === 'wishlist'" class="tab-content">
      <div v-if="wishlist.length === 0" class="empty">Your wishlist is empty.</div>
      <div v-else class="wishlist-grid">
        <div v-for="item in wishlist" :key="item.id" class="wishlist-item card">
          <router-link :to="'/attractions/' + item.attraction_id">
            <div class="wishlist-img" :style="item.image_url ? 'background-image: url(' + item.image_url + ')' : 'background: linear-gradient(135deg, #1a5e63, #2d8a8e)'"></div>
          </router-link>
          <div class="wishlist-info">
            <h4>{{ item.name }}</h4>
            <p class="wishlist-loc">{{ item.location }}</p>
            <span v-if="item.visited" class="visited-badge">✓ Visited</span>
          </div>
          <button @click="removeWish(item.attraction_id)" class="btn-link delete-btn">Remove</button>
        </div>
      </div>
    </div>

    <!-- My Articles -->
    <div v-if="activeTab === 'articles'" class="tab-content">
      <button @click="$router.push('/articles/write')" class="btn-primary" style="margin-bottom:1rem">Write New Article</button>
      <div v-if="myArticles.length === 0" class="empty">You have not written any articles yet.</div>
      <div v-else class="articles-list">
        <div v-for="a in myArticles" :key="a.id" class="article-item card">
          <h4 @click="$router.push('/articles/' + a.id)" class="article-title">{{ a.title }}</h4>
          <div class="article-meta">
            <span>{{ formatDate(a.created_at) }}</span>
            <span>Likes: {{ a.like_count }}</span>
            <span>Views: {{ a.view_count }}</span>
            <span v-if="a.is_featured" class="badge-featured">Featured</span>
          </div>
          <div class="article-actions">
            <button @click="$router.push('/articles/write?id=' + a.id)" class="btn-secondary-sm">Edit</button>
            <button @click="deleteArticle(a.id)" class="btn-link delete-btn">Delete</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { usersAPI, reviewsAPI, wishlistAPI, articlesAPI } from '../api/client.js'

const profile = ref(JSON.parse(localStorage.getItem('user') || '{}'))
const showEditForm = ref(false)
const activeTab = ref('reviews')
const saving = ref(false)
const editError = ref('')
const editSuccess = ref('')

const reviews = ref([])
const wishlist = ref([])
const myArticles = ref([])
const tabCounts = ref({ reviews: 0, wishlist: 0, articles: 0 })

const editForm = ref({ nickname: '', avatar_url: '', bio: '', current_password: '', new_password: '' })

const tabs = [
  { key: 'reviews', label: 'My Reviews' },
  { key: 'wishlist', label: 'Wishlist' },
  { key: 'articles', label: 'Articles' }
]

const initials = computed(() => {
  const name = profile.value.nickname || profile.value.username || '?'
  return name.slice(0, 2).toUpperCase()
})

const avatarStyle = computed(() => {
  const colors = ['#1a5e63', '#2d8a8e', '#1a7e63', '#1a5e83']
  const idx = (profile.value.id || 0) % colors.length
  const name = profile.value.nickname || profile.value.username || ''
  if (profile.value.avatar_url) return { backgroundImage: `url(${profile.value.avatar_url})` }
  return { background: colors[idx] }
})

const loadProfile = async () => {
  try {
    const res = await usersAPI.me()
    profile.value = res.data
    editForm.value = { nickname: res.data.nickname || '', avatar_url: res.data.avatar_url || '', bio: res.data.bio || '', current_password: '', new_password: '' }
  } catch (e) { console.error(e) }
}

const saveProfile = async () => {
  saving.value = true
  editError.value = ''
  editSuccess.value = ''
  try {
    const payload = {}
    if (editForm.value.nickname) payload.nickname = editForm.value.nickname
    if (editForm.value.avatar_url) payload.avatar_url = editForm.value.avatar_url
    if (editForm.value.bio) payload.bio = editForm.value.bio
    if (editForm.value.new_password) {
      payload.current_password = editForm.value.current_password
      payload.new_password = editForm.value.new_password
    }
    await usersAPI.updateMe(payload)
    editSuccess.value = 'Profile updated!'
    await loadProfile()
    showEditForm.value = false
  } catch (e) {
    editError.value = e.response?.data?.error || 'Update failed'
  } finally { saving.value = false }
}

const loadTab = async () => {
  if (activeTab.value === 'reviews') await loadReviews()
  else if (activeTab.value === 'wishlist') await loadWishlist()
  else if (activeTab.value === 'articles') await loadArticles()
}

const loadReviews = async () => {
  try {
    const res = await reviewsAPI.list({ user_id: profile.value.id, per_page: 100 })
    reviews.value = res.data.reviews
    tabCounts.value.reviews = res.data.total
  } catch (e) { console.error(e) }
}

const loadWishlist = async () => {
  try {
    const res = await wishlistAPI.list({ per_page: 100 })
    wishlist.value = res.data.items
    tabCounts.value.wishlist = res.data.total
  } catch (e) { console.error(e) }
}

const loadArticles = async () => {
  try {
    const res = await articlesAPI.list({ user_id: profile.value.id, per_page: 100 })
    myArticles.value = res.data.articles
    tabCounts.value.articles = res.data.total
  } catch (e) { console.error(e) }
}

const deleteReview = async (id) => {
  if (!confirm('Delete this review?')) return
  try { await reviewsAPI.delete(id); await loadReviews() } catch (e) { alert('Failed') }
}

const removeWish = async (attractionId) => {
  try { await wishlistAPI.remove(attractionId); await loadWishlist() } catch (e) { alert('Failed') }
}

const deleteArticle = async (id) => {
  if (!confirm('Delete this article?')) return
  try { await articlesAPI.delete(id); await loadArticles() } catch (e) { alert('Failed') }
}

const formatDate = (d) => new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })

onMounted(async () => {
  await loadProfile()
  await loadReviews()
})
</script>

<style scoped>
.profile-header {
  display: flex;
  align-items: center;
  gap: 2rem;
  margin-bottom: 1.5rem;
}
.avatar-section { display: flex; align-items: center; gap: 1rem; flex: 1; }
.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-size: cover;
  background-position: center;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  font-weight: bold;
  flex-shrink: 0;
}
.profile-info h2 { color: #1a5e63; margin-bottom: 0.2rem; }
.nickname { color: #666; font-size: 0.9rem; }
.email { color: #888; font-size: 0.85rem; }
.role-badge { padding: 0.2rem 0.6rem; border-radius: 10px; font-size: 0.75rem; font-weight: 600; }
.role-admin { background: #fff3e0; color: #e67e00; }
.role-moderator { background: #e8f4fd; color: #1976d2; }
.role-user { background: #eee; color: #666; }

.profile-meta { color: #888; font-size: 0.85rem; flex: 1; }

.edit-form { margin-bottom: 1.5rem; }
.edit-form h3 { color: #1a5e63; margin-bottom: 1rem; }
.form-group { margin-bottom: 1rem; }
.form-group label { display: block; margin-bottom: 0.3rem; font-weight: 500; color: #555; }

.tabs { display: flex; border-bottom: 2px solid #eee; margin-bottom: 1.5rem; }
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
.tab-count { background: #eee; padding: 0.1rem 0.4rem; border-radius: 8px; font-size: 0.75rem; margin-left: 0.3rem; }

.reviews-list { display: flex; flex-direction: column; gap: 1rem; }
.review-item { padding: 1rem 1.2rem; }
.review-top { display: flex; justify-content: space-between; margin-bottom: 0.3rem; }
.review-title { font-weight: 600; color: #333; margin-bottom: 0.3rem; }
.review-content { color: #666; font-size: 0.9rem; margin-bottom: 0.5rem; }
.review-footer { display: flex; align-items: center; gap: 1rem; font-size: 0.8rem; }
.review-date { color: #aaa; }

.wishlist-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem; }
.wishlist-item { display: flex; align-items: center; gap: 0.8rem; }
.wishlist-img { width: 60px; height: 60px; border-radius: 8px; background-size: cover; background-position: center; flex-shrink: 0; }
.wishlist-info { flex: 1; }
.wishlist-info h4 { color: #1a5e63; font-size: 0.95rem; }
.wishlist-loc { color: #888; font-size: 0.8rem; }
.visited-badge { background: #e6f9ee; color: #2a9d5c; padding: 0.1rem 0.4rem; border-radius: 8px; font-size: 0.75rem; }

.articles-list { display: flex; flex-direction: column; gap: 0.8rem; }
.article-item { padding: 1rem 1.2rem; }
.article-title { color: #1a5e63; cursor: pointer; margin-bottom: 0.3rem; }
.article-title:hover { text-decoration: underline; }
.article-meta { display: flex; gap: 1rem; font-size: 0.8rem; color: #888; margin-bottom: 0.5rem; }
.article-actions { display: flex; gap: 0.5rem; }
.btn-secondary-sm { padding: 0.3rem 0.8rem; border: 1px solid #ddd; border-radius: 4px; background: #f5f7fa; cursor: pointer; font-size: 0.85rem; }

.delete-btn { color: #d44; }

.sentiment-badge { padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.8rem; font-weight: 600; }
.sentiment-positive { background: #e6f9ee; color: #2a9d5c; }
.sentiment-neutral { background: #f0f0f0; color: #666; }
.sentiment-negative { background: #fee; color: #d44; }

.badge-featured { background: #f5a623; color: white; padding: 0.1rem 0.5rem; border-radius: 10px; font-size: 0.75rem; }
</style>
