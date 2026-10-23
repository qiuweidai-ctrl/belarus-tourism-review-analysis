<template>
  <div id="app">
    <router-view v-if="isAuthPage" />

    <div v-else class="app-shell" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <button
        v-if="mobileNavOpen"
        class="nav-overlay"
        type="button"
        aria-label="Close navigation"
        @click="mobileNavOpen = false"
      ></button>

      <aside class="sidebar" :class="{ 'mobile-open': mobileNavOpen }">
        <router-link to="/" class="sidebar-brand" @click="mobileNavOpen = false">
          <span class="brand-mark">BT</span>
          <span class="brand-copy">
            <strong>Belarus Tourism</strong>
            <small>Review &amp; Analysis</small>
          </span>
        </router-link>

        <nav class="sidebar-nav" aria-label="Main navigation">
          <section v-for="group in navGroups" :key="group.label" class="nav-section">
            <p class="nav-section-label">{{ group.label }}</p>
            <router-link
              v-for="item in group.items"
              :key="item.to"
              :to="item.to"
              class="side-link"
              :title="sidebarCollapsed ? item.label : undefined"
              @click="mobileNavOpen = false"
            >
              <span class="side-icon" aria-hidden="true">{{ item.icon }}</span>
              <span class="side-label">{{ item.label }}</span>
            </router-link>
          </section>
        </nav>

        <div class="sidebar-foot">
          <span class="status-dot"></span>
          <span class="side-label">System online</span>
        </div>
      </aside>

      <div class="workspace">
        <header class="topbar">
          <div class="topbar-left">
            <button
              class="top-icon desktop-toggle"
              type="button"
              :aria-label="sidebarCollapsed ? 'Expand navigation' : 'Collapse navigation'"
              @click="toggleSidebar"
            >
              <span aria-hidden="true">☰</span>
            </button>
            <button
              class="top-icon mobile-toggle"
              type="button"
              aria-label="Open navigation"
              @click="mobileNavOpen = true"
            >
              <span aria-hidden="true">☰</span>
            </button>
            <div class="page-context">
              <span class="breadcrumb">Belarus Tourism / {{ currentPageTitle }}</span>
              <strong>{{ currentPageTitle }}</strong>
            </div>
          </div>

          <form class="global-search" @submit.prevent="submitSearch">
            <span aria-hidden="true">⌕</span>
            <input
              v-model="query"
              type="search"
              placeholder="Search attractions, cities..."
              aria-label="Search attractions and cities"
            />
          </form>

          <div class="topbar-actions">
            <button
              class="top-icon"
              type="button"
              :title="isDark ? 'Use light mode' : 'Use dark mode'"
              :aria-label="isDark ? 'Use light mode' : 'Use dark mode'"
              @click="toggleTheme"
            >
              <span aria-hidden="true">{{ isDark ? '☀' : '☾' }}</span>
            </button>

            <template v-if="isLoggedIn">
              <button class="user-menu" type="button" @click="goProfile">
                <span class="avatar" :style="{ backgroundColor: avatarColor }">{{ avatarLetter }}</span>
                <span class="user-copy">
                  <strong>{{ displayName }}</strong>
                  <small>{{ currentUser?.role || 'user' }}</small>
                </span>
              </button>
              <button class="logout-btn" type="button" @click="logout">Sign out</button>
            </template>
            <template v-else>
              <router-link to="/login" class="header-link">Sign in</router-link>
              <router-link to="/register" class="btn btn-primary btn-sm">Create account</router-link>
            </template>
          </div>
        </header>

        <main class="main-content">
          <router-view v-slot="{ Component }">
            <transition name="page" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </main>

        <footer class="site-footer">
          <span>Belarus Tourism Review &amp; Analysis System</span>
          <span>Flask · Vue 3 · MySQL</span>
        </footer>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { authAPI } from '@/api/client.js'

const router = useRouter()
const route = useRoute()
const query = ref('')
const mobileNavOpen = ref(false)
const sidebarCollapsed = ref(localStorage.getItem('sidebar-collapsed') === 'true')
const isDark = ref(document.documentElement.getAttribute('data-theme') === 'dark')
const authVersion = ref(0)

const isAuthPage = computed(() => ['/login', '/register'].includes(route.path))
const isLoggedIn = computed(() => {
  void authVersion.value
  return Boolean(localStorage.getItem('token'))
})
const currentUser = computed(() => {
  void authVersion.value
  try {
    return JSON.parse(localStorage.getItem('user') || 'null')
  } catch (_) {
    return null
  }
})
const isAdmin = computed(() => ['admin', 'moderator'].includes(currentUser.value?.role))

const pages = {
  '/': 'Overview',
  '/attractions': 'Attractions',
  '/map': 'Map Explorer',
  '/rankings': 'Rankings',
  '/compare': 'Compare Attractions',
  '/insights': 'Data Insights',
  '/wordcloud': 'Word Clouds',
  '/articles': 'Travel Articles',
  '/qa': 'Questions & Answers',
  '/itinerary': 'Trip Planner',
  '/wishlist': 'Wishlist',
  '/recommendations': 'Recommendations',
  '/profile': 'My Profile',
  '/admin': 'Administration'
}

const currentPageTitle = computed(() => {
  if (route.path.startsWith('/attractions/')) return 'Attraction Details'
  if (route.path.startsWith('/articles/')) return route.path.endsWith('/write') ? 'Write Article' : 'Article Details'
  return pages[route.path] || 'Belarus Tourism'
})

const navGroups = computed(() => [
  { label: 'Overview', items: [{ to: '/', label: 'Dashboard', icon: '⌂' }] },
  {
    label: 'Explore',
    items: [
      { to: '/attractions', label: 'Attractions', icon: '◇' },
      { to: '/map', label: 'Map Explorer', icon: '⌖' },
      { to: '/rankings', label: 'Rankings', icon: '★' },
      { to: '/compare', label: 'Compare', icon: '⇄' }
    ]
  },
  {
    label: 'Analytics',
    items: [
      { to: '/insights', label: 'Data Insights', icon: '▥' },
      { to: '/wordcloud', label: 'Word Clouds', icon: '☁' }
    ]
  },
  {
    label: 'Community',
    items: [
      { to: '/articles', label: 'Travel Articles', icon: '▤' },
      { to: '/qa', label: 'Questions & Answers', icon: '?' }
    ]
  },
  {
    label: 'My Trip',
    items: [
      { to: '/itinerary', label: 'Trip Planner', icon: '▣' },
      { to: '/wishlist', label: 'Wishlist', icon: '♡' },
      { to: '/recommendations', label: 'For You', icon: '✦', auth: true },
      { to: '/profile', label: 'My Profile', icon: '○', auth: true }
    ]
  },
  { label: 'Administration', items: [{ to: '/admin', label: 'Admin Panel', icon: '⚙', admin: true }] }
].map((group) => ({
  ...group,
  items: group.items.filter((item) => (!item.auth || isLoggedIn.value) && (!item.admin || isAdmin.value))
})).filter((group) => group.items.length))

const displayName = computed(() => {
  const user = currentUser.value
  return user?.username || user?.name || user?.email || 'Traveler'
})
const avatarLetter = computed(() => displayName.value.trim().charAt(0).toUpperCase() || '?')
const avatarColor = computed(() => {
  let hash = 0
  for (const char of displayName.value) hash = char.charCodeAt(0) + ((hash << 5) - hash)
  return `hsl(${Math.abs(hash) % 360}, 52%, 44%)`
})

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
  localStorage.setItem('sidebar-collapsed', String(sidebarCollapsed.value))
}
const submitSearch = () => {
  const search = query.value.trim()
  router.push({ path: '/attractions', query: search ? { search } : {} })
}
const toggleTheme = () => {
  isDark.value = !isDark.value
  const theme = isDark.value ? 'dark' : 'light'
  document.documentElement.setAttribute('data-theme', theme)
  localStorage.setItem('theme', theme)
  window.dispatchEvent(new CustomEvent('app:theme-changed', { detail: theme }))
}
const goProfile = () => router.push('/profile')
const logout = async () => {
  try {
    await authAPI.logout()
  } catch (_) {
  }
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  authVersion.value++
  router.push('/login')
}

const refreshAuth = () => { authVersion.value++ }
watch(() => route.fullPath, () => {
  authVersion.value++
  mobileNavOpen.value = false
})
onMounted(() => {
  window.addEventListener('storage', refreshAuth)
  window.addEventListener('app:auth-changed', refreshAuth)
})
onUnmounted(() => {
  window.removeEventListener('storage', refreshAuth)
  window.removeEventListener('app:auth-changed', refreshAuth)
})
</script>

<style>
#app { min-height: 100vh; }
.app-shell { min-height: 100vh; }
.sidebar {
  position: fixed;
  inset: 0 auto 0 0;
  z-index: 120;
  width: 236px;
  display: flex;
  flex-direction: column;
  background: var(--surface);
  border-right: 1px solid var(--border);
  box-shadow: 8px 0 24px rgba(15, 23, 42, .035);
  transition: width var(--speed) var(--ease), transform var(--speed) var(--ease);
}
.sidebar-brand {
  height: 70px;
  display: flex;
  align-items: center;
  gap: .7rem;
  padding: 0 1.1rem;
  color: var(--text);
  border-bottom: 1px solid var(--border);
  overflow: hidden;
}
.brand-mark {
  width: 38px;
  height: 38px;
  flex: 0 0 38px;
  display: grid;
  place-items: center;
  color: #fff;
  font-size: .9rem;
  font-weight: 800;
  letter-spacing: .04em;
  border-radius: 10px;
  background: var(--grad-brand);
  box-shadow: var(--shadow-brand);
}
.brand-copy { min-width: 145px; display: flex; flex-direction: column; line-height: 1.2; }
.brand-copy strong { color: var(--text); font-size: .94rem; }
.brand-copy small { color: var(--text-mute); font-size: .67rem; }
.sidebar-nav { flex: 1; overflow-y: auto; padding: 1rem .75rem; }
.nav-section + .nav-section { margin-top: 1.05rem; }
.nav-section-label {
  margin: 0 0 .35rem;
  padding: 0 .65rem;
  color: var(--text-mute);
  font-size: .64rem;
  font-weight: 800;
  letter-spacing: .12em;
  text-transform: uppercase;
  white-space: nowrap;
}
.side-link {
  min-height: 42px;
  display: flex;
  align-items: center;
  gap: .75rem;
  margin: .12rem 0;
  padding: .55rem .65rem;
  color: var(--text-soft);
  font-size: .86rem;
  font-weight: 600;
  border-radius: 9px;
  white-space: nowrap;
  transition: color var(--speed) var(--ease), background var(--speed) var(--ease);
}
.side-link:hover { color: var(--brand-700); background: var(--surface-hover); }
.side-link.router-link-exact-active,
.side-link.router-link-active:not([href='/']) { color: var(--brand-700); background: var(--brand-50); }
[data-theme='dark'] .side-link.router-link-exact-active,
[data-theme='dark'] .side-link.router-link-active:not([href='/']) { color: var(--brand-300); background: rgba(20,184,147,.14); }
.side-icon { width: 24px; flex: 0 0 24px; display: inline-grid; place-items: center; font-size: 1rem; }
.sidebar-foot {
  min-height: 54px;
  display: flex;
  align-items: center;
  gap: .6rem;
  padding: 0 1.35rem;
  color: var(--text-mute);
  font-size: .75rem;
  border-top: 1px solid var(--border);
  white-space: nowrap;
  overflow: hidden;
}
.status-dot { width: 8px; height: 8px; flex: 0 0 8px; border-radius: 50%; background: var(--success); box-shadow: 0 0 0 4px var(--success-soft); }
.workspace { min-height: 100vh; margin-left: 236px; display: flex; flex-direction: column; transition: margin-left var(--speed) var(--ease); }
.topbar {
  position: sticky;
  top: 0;
  z-index: 90;
  height: 70px;
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0 1.4rem;
  background: color-mix(in srgb, var(--surface) 94%, transparent);
  border-bottom: 1px solid var(--border);
  box-shadow: 0 4px 16px rgba(15, 23, 42, .035);
  backdrop-filter: blur(12px);
}
.topbar-left { display: flex; align-items: center; gap: .8rem; min-width: 230px; }
.top-icon {
  width: 38px;
  height: 38px;
  flex: 0 0 38px;
  display: grid;
  place-items: center;
  color: var(--text-soft);
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 9px;
  cursor: pointer;
  font: inherit;
  font-size: 1.05rem;
}
.top-icon:hover { color: var(--brand-700); border-color: var(--brand-300); }
.page-context { display: flex; flex-direction: column; line-height: 1.25; }
.page-context strong { color: var(--text); font-size: .97rem; }
.breadcrumb { color: var(--text-mute); font-size: .68rem; }
.mobile-toggle { display: none; }
.global-search { position: relative; width: min(360px, 30vw); margin-left: auto; }
.global-search > span { position: absolute; left: .8rem; top: 50%; transform: translateY(-50%); color: var(--text-mute); pointer-events: none; }
.global-search input { height: 40px; padding-left: 2.2rem; background: var(--surface-2); border-color: var(--border); }
.topbar-actions { display: flex; align-items: center; gap: .55rem; }
.header-link { padding: .45rem .5rem; color: var(--text-soft); font-size: .84rem; font-weight: 600; }
.logout-btn { color: var(--text-mute); background: none; border: 0; cursor: pointer; font: inherit; font-size: .78rem; }
.logout-btn:hover { color: var(--danger); }
.user-menu { display: flex; align-items: center; gap: .55rem; padding: .25rem .55rem .25rem .25rem; background: transparent; border: 0; border-radius: 10px; cursor: pointer; }
.user-menu:hover { background: var(--surface-hover); }
.avatar {
  width: 34px;
  height: 34px;
  flex: 0 0 34px;
  display: grid;
  place-items: center;
  overflow: hidden;
  color: #fff;
  background-position: center;
  background-size: cover;
  border-radius: 9px;
  font-size: .82rem;
  font-weight: 800;
}
.avatar img { width: 100%; height: 100%; object-fit: cover; }
.user-copy { min-width: 72px; display: flex; flex-direction: column; align-items: flex-start; line-height: 1.2; }
.user-copy strong { max-width: 120px; overflow: hidden; color: var(--text); font-size: .8rem; text-overflow: ellipsis; }
.user-copy small { color: var(--text-mute); font-size: .66rem; text-transform: capitalize; }
.main-content { width: 100%; max-width: 1600px; min-height: calc(100vh - 118px); margin: 0 auto; padding: 1.5rem; }
.site-footer { display: flex; justify-content: space-between; gap: 1rem; padding: .9rem 1.5rem; color: var(--text-mute); font-size: .72rem; border-top: 1px solid var(--border); }
.nav-overlay { display: none; }
.sidebar-collapsed .sidebar { width: 76px; }
.sidebar-collapsed .workspace { margin-left: 76px; }
.sidebar-collapsed .brand-copy,
.sidebar-collapsed .nav-section-label,
.sidebar-collapsed .side-label { display: none; }
.sidebar-collapsed .sidebar-brand { justify-content: center; padding: 0; }
.sidebar-collapsed .sidebar-nav { padding-inline: .65rem; }
.sidebar-collapsed .side-link { justify-content: center; padding-inline: 0; }
.sidebar-collapsed .sidebar-foot { justify-content: center; padding: 0; }
.page-enter-active, .page-leave-active { transition: opacity .18s var(--ease), transform .18s var(--ease); }
.page-enter-from { opacity: 0; transform: translateY(6px); }
.page-leave-to { opacity: 0; }

@media (max-width: 1100px) {
  .global-search { width: min(280px, 26vw); }
  .user-copy, .logout-btn { display: none; }
}
@media (max-width: 820px) {
  .sidebar, .sidebar-collapsed .sidebar { width: 236px; transform: translateX(-102%); }
  .sidebar.mobile-open { transform: translateX(0); }
  .workspace, .sidebar-collapsed .workspace { margin-left: 0; }
  .sidebar-collapsed .brand-copy, .sidebar-collapsed .nav-section-label, .sidebar-collapsed .side-label { display: initial; }
  .sidebar-collapsed .sidebar-brand { justify-content: flex-start; padding: 0 1.1rem; }
  .sidebar-collapsed .sidebar-nav { padding: 1rem .75rem; }
  .sidebar-collapsed .side-link { justify-content: flex-start; padding: .55rem .65rem; }
  .sidebar-collapsed .sidebar-foot { justify-content: flex-start; padding: 0 1.35rem; }
  .nav-overlay { position: fixed; inset: 0; z-index: 110; display: block; background: rgba(15, 23, 42, .45); border: 0; }
  .desktop-toggle { display: none; }
  .mobile-toggle { display: grid; }
  .breadcrumb { display: none; }
}
@media (max-width: 640px) {
  .topbar { height: 62px; padding: 0 .85rem; }
  .topbar-left { min-width: 0; }
  .page-context strong { max-width: 135px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .global-search { display: none; }
  .header-link { display: none; }
  .main-content { padding: 1rem .85rem 1.5rem; }
  .site-footer { display: none; }
}
</style>
