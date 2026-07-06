<template>
  <div>
    <h1 class="page-title">My Profile</h1>

    <!-- Profile Info Card -->
    <div class="profile-header card">
      <div class="avatar-section">
        <div class="avatar-clickable-wrap" @click="openQuickAvatarPicker" :title="quickUploading ? 'Uploading...' : 'Click to upload / change avatar'">
          <div class="avatar" :style="avatarStyle">
            <span v-if="!profile.avatar_url" class="avatar-initials">{{ initials }}</span>
          </div>
          <span class="avatar-edit-badge" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor">
              <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04a1 1 0 0 0 0-1.41l-2.34-2.34a1 1 0 0 0-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
            </svg>
          </span>
        </div>
        <input
          ref="quickAvatarFileInput"
          type="file"
          accept="image/png,image/jpeg,image/jpg,image/gif,image/webp"
          style="display:none"
          @change="onQuickAvatarChange"
        />
        <div class="profile-info">
          <h2>{{ profile.username }}</h2>
          <p v-if="profile.nickname" class="nickname">{{ profile.nickname }}</p>
          <p class="email">{{ profile.email }}</p>
          <span :class="'role-badge role-' + profile.role">{{ profile.role }}</span>
          <p v-if="quickUploadError" class="error-msg" style="margin-top:0.4rem">{{ quickUploadError }}</p>
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
        <label>Or upload a local image (PNG/JPG/WebP/GIF, ≤4MB)</label>
        <div class="avatar-upload-row">
          <div class="avatar-preview" :style="avatarPreviewStyle">
            <span v-if="!avatarPreviewUrl && !profile.avatar_url" class="avatar-preview-empty">None</span>
          </div>
          <div class="avatar-upload-controls">
            <input
              ref="avatarFileInput"
              type="file"
              accept="image/png,image/jpeg,image/jpg,image/gif,image/webp"
              @change="onAvatarFileChange"
            />
            <button v-if="avatarPreviewUrl" type="button" class="btn-link" @click="clearAvatarFile">Clear selection</button>
            <p class="hint">A preview will appear after you pick a file; it uploads to the server when you click Save Changes.</p>
            <p v-if="avatarFileError" class="error-msg">{{ avatarFileError }}</p>
          </div>
        </div>
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

    <!-- Login History (Security tab) -->
    <div v-if="activeTab === 'security'" class="tab-content">
      <h3 class="security-title">Login Events</h3>
      <p class="security-hint">Recent login-related activity on your account (login, logout, password change, etc.).</p>
      <div v-if="loginEvents.length === 0" class="empty">No login events recorded yet.</div>
      <div v-else class="events-list">
        <div v-for="ev in loginEvents" :key="ev.id" class="event-item card" :class="'evt-' + ev.event_type">
          <div class="evt-head">
            <span class="evt-label" :class="'evt-' + ev.event_type">{{ ev.event_label }}</span>
            <span class="evt-time">{{ formatDateTime(ev.created_at) }}</span>
            <span :class="'evt-status status-' + ev.status" class="evt-status">{{ ev.status }}</span>
          </div>
          <div class="evt-body">
            <div><strong>IP:</strong> {{ ev.ip_address || '—' }}</div>
            <div class="evt-ua" :title="ev.user_agent"><strong>Device:</strong> {{ shortUA(ev.user_agent) }}</div>
            <div v-if="ev.detail" class="evt-detail"><strong>Detail:</strong> {{ ev.detail }}</div>
          </div>
        </div>
      </div>

      <div v-if="loginEventsPages > 1" class="pagination">
        <button @click="loginEventsPage--; loadLoginEvents()" :disabled="loginEventsPage <= 1" class="btn-secondary">Prev</button>
        <span>Page {{ loginEventsPage }} / {{ loginEventsPages }}</span>
        <button @click="loginEventsPage++; loadLoginEvents()" :disabled="loginEventsPage >= loginEventsPages" class="btn-secondary">Next</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { usersAPI, reviewsAPI, wishlistAPI, articlesAPI, authAPI } from '@/api/client.js'

const profile = ref(JSON.parse(localStorage.getItem('user') || '{}'))
const showEditForm = ref(false)
const activeTab = ref('reviews')
const saving = ref(false)
const editError = ref('')
const editSuccess = ref('')

// Notify the navbar to refresh its currentUser (App.vue reads user from
// localStorage and only re-evaluates on route changes / a "_bump" trigger).
function syncNavbar() {
  window.dispatchEvent(new Event('storage'))
  // Fallback: also bump a custom event so App.vue's _bump goes up
  // (App.vue already listens to 'storage' for the same effect).
  try { window.dispatchEvent(new CustomEvent('app:auth-changed')) } catch (_) {}
}

const reviews = ref([])
const wishlist = ref([])
const myArticles = ref([])
const tabCounts = ref({ reviews: 0, wishlist: 0, articles: 0, security: 0 })

const editForm = ref({ nickname: '', avatar_url: '', bio: '', current_password: '', new_password: '' })

// Avatar upload state (local-only until Save is pressed)
const avatarFileInput = ref(null)
const avatarFile = ref(null)        // the actual File object
const avatarPreviewUrl = ref('')    // object URL for instant preview
const avatarFileError = ref('')

// Quick avatar picker state (clicking the big avatar in the header).
const quickAvatarFileInput = ref(null)
const quickUploading = ref(false)
const quickUploadError = ref('')
const ALLOWED_AVATAR_TYPES = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp']
const MAX_AVATAR_SIZE = 4 * 1024 * 1024

function validateAvatarFile(f) {
  if (!ALLOWED_AVATAR_TYPES.includes(f.type)) {
    return `Unsupported file format: ${f.type || 'unknown'}. Please use PNG / JPG / GIF / WebP.`
  }
  if (f.size > MAX_AVATAR_SIZE) {
    return `File too large: ${(f.size / 1024 / 1024).toFixed(2)} MB, max 4 MB.`
  }
  return ''
}

const avatarPreviewStyle = computed(() => {
  if (avatarPreviewUrl.value) return { backgroundImage: `url(${avatarPreviewUrl.value})` }
  if (profile.value.avatar_url) return { backgroundImage: `url(${profile.value.avatar_url})` }
  return {}
})

function onAvatarFileChange(e) {
  avatarFileError.value = ''
  const f = e.target.files && e.target.files[0]
  if (!f) {
    clearAvatarFile()
    return
  }
  const err = validateAvatarFile(f)
  if (err) {
    avatarFileError.value = err
    clearAvatarFile()
    return
  }
  // Revoke any prior object URL to avoid leaks
  if (avatarPreviewUrl.value) URL.revokeObjectURL(avatarPreviewUrl.value)
  avatarFile.value = f
  avatarPreviewUrl.value = URL.createObjectURL(f)
}

function clearAvatarFile() {
  if (avatarPreviewUrl.value) URL.revokeObjectURL(avatarPreviewUrl.value)
  avatarPreviewUrl.value = ''
  avatarFile.value = null
  if (avatarFileInput.value) avatarFileInput.value.value = ''
}

// Open the hidden file picker wired to the main page avatar.
function openQuickAvatarPicker() {
  if (quickUploading.value) return
  quickUploadError.value = ''
  quickAvatarFileInput.value && quickAvatarFileInput.value.click()
}

// Handle the file the user picked via the quick avatar (header) control.
async function onQuickAvatarChange(e) {
  const f = e.target.files && e.target.files[0]
  // Always reset the input so picking the same file again still triggers change.
  if (quickAvatarFileInput.value) quickAvatarFileInput.value.value = ''
  if (!f) return
  const err = validateAvatarFile(f)
  if (err) {
    quickUploadError.value = err
    return
  }
  quickUploadError.value = ''
  quickUploading.value = true
  try {
    const up = await usersAPI.uploadAvatar(f)
    profile.value = { ...profile.value, avatar_url: up.data.avatar_url }
    editForm.value.avatar_url = up.data.avatar_url
    localStorage.setItem('user', JSON.stringify(profile.value))
    syncNavbar()
  } catch (e) {
    quickUploadError.value = e.response?.data?.error || 'Avatar upload failed, please try again'
  } finally {
    quickUploading.value = false
  }
}

// Login events state
const loginEvents = ref([])
const loginEventsPage = ref(1)
const loginEventsPages = ref(1)

const tabs = [
  { key: 'reviews', label: 'My Reviews' },
  { key: 'wishlist', label: 'Wishlist' },
  { key: 'articles', label: 'Articles' },
  { key: 'security', label: 'Security' }
] // 'security' surfaces login events

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
    // If a local file is selected, upload it first. The server endpoint
    // already persists user.avatar_url, so the matching PUT below is skipped.
    if (avatarFile.value) {
      try {
        const up = await usersAPI.uploadAvatar(avatarFile.value)
        profile.value = { ...profile.value, avatar_url: up.data.avatar_url }
        editForm.value.avatar_url = up.data.avatar_url
        clearAvatarFile()
      } catch (e) {
        editError.value = e.response?.data?.error || 'Avatar upload failed'
        saving.value = false
        return
      }
    }

    const payload = {}
    if (editForm.value.nickname) payload.nickname = editForm.value.nickname
    // Only PUT avatar_url when we did not just upload a file (server already saved it).
    if (editForm.value.avatar_url && !avatarFile.value) payload.avatar_url = editForm.value.avatar_url
    if (editForm.value.bio) payload.bio = editForm.value.bio
    if (editForm.value.new_password) {
      payload.current_password = editForm.value.current_password
      payload.new_password = editForm.value.new_password
    }
    if (Object.keys(payload).length > 0) {
      await usersAPI.updateMe(payload)
    }
    editSuccess.value = 'Profile updated!'
    await loadProfile()
    // Persist the updated profile so the navbar avatar/nickname reflect the
    // change immediately (no manual reload required).
    localStorage.setItem('user', JSON.stringify(profile.value))
    syncNavbar()
    showEditForm.value = false
  } catch (e) {
    editError.value = e.response?.data?.error || 'Update failed'
  } finally { saving.value = false }
}

const loadTab = async () => {
  if (activeTab.value === 'reviews') await loadReviews()
  else if (activeTab.value === 'wishlist') await loadWishlist()
  else if (activeTab.value === 'articles') await loadArticles()
  else if (activeTab.value === 'security') await loadLoginEvents()
}

const loadLoginEvents = async () => {
  try {
    const res = await authAPI.events({
      page: loginEventsPage.value,
      per_page: 10
    })
    loginEvents.value = res.data.events
    loginEventsPages.value = res.data.pages
    tabCounts.value.security = res.data.total
  } catch (e) { console.error(e) }
}

const shortUA = (ua) => {
  if (!ua) return 'Unknown'
  // Trim UA to its first segments; full version is in the title attribute on hover.
  return ua.length > 80 ? ua.slice(0, 80) + '...' : ua
}

const formatDateTime = (d) => {
  if (!d) return ''
  return new Date(d).toLocaleString('en-US', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
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
  await Promise.all([
    loadReviews(),
    loadWishlist(),
    loadArticles(),
    loadLoginEvents()
  ])
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
.avatar-clickable-wrap {
  position: relative;
  cursor: pointer;
  border-radius: 50%;
  display: inline-flex;
}
.avatar-clickable-wrap:hover .avatar { box-shadow: 0 0 0 3px rgba(26, 94, 99, 0.25); }
.avatar-clickable-wrap:hover .avatar-edit-badge { opacity: 1; transform: scale(1); }
.avatar-edit-badge {
  position: absolute;
  right: -2px; bottom: -2px;
  width: 26px; height: 26px;
  border-radius: 50%;
  background: #1a5e63; color: #fff;
  display: inline-flex; align-items: center; justify-content: center;
  box-shadow: 0 2px 6px rgba(0,0,0,0.2);
  opacity: 0.85;
  transition: opacity 0.15s ease, transform 0.15s ease;
}
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
  transition: box-shadow 0.15s ease;
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

/* Login events / Security tab */
.security-title { color: #1a5e63; margin-bottom: 0.3rem; }
.security-hint  { color: #888; font-size: 0.85rem; margin-bottom: 1rem; }

.events-list { display: flex; flex-direction: column; gap: 0.7rem; }
.event-item  { padding: 0.8rem 1rem; border-left: 4px solid #ccc; }
.event-item.evt-login          { border-left-color: #1a5e63; }
.event-item.evt-logout         { border-left-color: #888; }
.event-item.evt-register       { border-left-color: #2a9d5c; }
.event-item.evt-login_failed   { border-left-color: #d44; }
.event-item.evt-token_refresh  { border-left-color: #1976d2; }
.event-item.evt-password_changed { border-left-color: #f5a623; }

.evt-head {
  display: flex; align-items: center; gap: 0.8rem;
  flex-wrap: wrap; margin-bottom: 0.4rem;
}
.evt-label {
  font-weight: 600; padding: 0.15rem 0.55rem; border-radius: 10px;
  font-size: 0.78rem; color: white;
}
.evt-label.evt-login          { background: #1a5e63; }
.evt-label.evt-logout         { background: #888; }
.evt-label.evt-register       { background: #2a9d5c; }
.evt-label.evt-login_failed   { background: #d44; }
.evt-label.evt-token_refresh  { background: #1976d2; }
.evt-label.evt-password_changed { background: #f5a623; }
.evt-time { color: #888; font-size: 0.8rem; }
.evt-status { margin-left: auto; font-size: 0.75rem; padding: 0.1rem 0.5rem; border-radius: 8px; }
.status-success { background: #e6f9ee; color: #2a9d5c; }
.status-failure { background: #fee; color: #d44; }
.status-blocked { background: #fff3e0; color: #e67e00; }

.evt-body { font-size: 0.85rem; color: #555; line-height: 1.6; }
.evt-ua   { color: #888; }
.evt-detail { color: #666; font-style: italic; }
</style>
