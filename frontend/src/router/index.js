import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import AttractionsView from '../views/AttractionsView.vue'
import AttractionDetailView from '../views/AttractionDetailView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import RecommendationsView from '../views/RecommendationsView.vue'
import ProfileView from '../views/ProfileView.vue'
import ArticlesView from '../views/ArticlesView.vue'
import ArticleDetailView from '../views/ArticleDetailView.vue'
import ArticleWriteView from '../views/ArticleWriteView.vue'
import QandAView from '../views/QandAView.vue'
import AdminDashboardView from '../views/AdminDashboardView.vue'

const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/attractions', name: 'attractions', component: AttractionsView },
  { path: '/attractions/:id', name: 'attraction-detail', component: AttractionDetailView },
  { path: '/login', name: 'login', component: LoginView },
  { path: '/register', name: 'register', component: RegisterView },
  { path: '/recommendations', name: 'recommendations', component: RecommendationsView },
  { path: '/profile', name: 'profile', component: ProfileView },
  { path: '/articles', name: 'articles', component: ArticlesView },
  { path: '/articles/:id', name: 'article-detail', component: ArticleDetailView },
  { path: '/articles/write', name: 'article-write', component: ArticleWriteView },
  { path: '/qa', name: 'qa', component: QandAView },
  { path: '/admin', name: 'admin', component: AdminDashboardView, meta: { requiresAdmin: true } }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return new Promise((resolve) => {
        setTimeout(() => resolve(savedPosition), 50)
      })
    }
    // Restore scroll position saved by the detail page's goBack -> push flow.
    const stored = sessionStorage.getItem('__scroll_' + to.fullPath)
    if (stored) {
      return new Promise((resolve) => {
        setTimeout(() => resolve({ top: Number(stored) }), 50)
      })
    }
    return { top: 0 }
  }
})

// Per-route session store: records the path the user was on immediately
// before navigating to a detail page. Used by the "Back" button on detail
// views to return to the exact source (e.g. /attractions vs /).
const referrerByRoute = new Map()

router.beforeEach((to, from, next) => {
  // When leaving a detail page, drop its stored referrer so it doesn't
  // leak onto the next detail page (e.g. /attractions/3 -> /attractions/5).
  if (from && from.params && from.params.id) {
    referrerByRoute.delete(from.fullPath)
  }
  // Persist where the user was before entering any /:id detail page.
  if (to.params && to.params.id && from && from.path && from.path !== to.path) {
    referrerByRoute.set(to.fullPath, from.fullPath)
  }
  // Also persist current scroll position keyed by fullPath so Back navigation
  // can restore it even when router.push() is used (which bypasses savedPosition).
  if (from && from.fullPath) {
    sessionStorage.setItem('__scroll_' + from.fullPath, String(window.scrollY))
  }
  if (to.meta.requiresAdmin) {
    const user = JSON.parse(localStorage.getItem('user') || 'null')
    if (!user || (user.role !== 'admin' && user.role !== 'moderator')) {
      return next('/login')
    }
  }
  next()
})

router.getReferrer = (currentFullPath) => referrerByRoute.get(currentFullPath) || null
router.clearReferrer = (currentFullPath) => { referrerByRoute.delete(currentFullPath) }
router.getScroll = (fullPath) => Number(sessionStorage.getItem('__scroll_' + fullPath)) || 0
router.clearScroll = (fullPath) => { sessionStorage.removeItem('__scroll_' + fullPath) }

export default router
