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
import InsightsView from '../views/InsightsView.vue'
import WordCloudView from '../views/WordCloudView.vue'
import RankingsView from '../views/RankingsView.vue'
import MapView from '../views/MapView.vue'
import CompareView from '../views/CompareView.vue'
import ItineraryView from '../views/ItineraryView.vue'
import WishlistView from '../views/WishlistView.vue'

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
  { path: '/admin', name: 'admin', component: AdminDashboardView, meta: { requiresAdmin: true } },
  { path: '/insights', name: 'insights', component: InsightsView },
  { path: '/wordcloud', name: 'wordcloud', component: WordCloudView },
  { path: '/rankings', name: 'rankings', component: RankingsView },
  { path: '/map', name: 'map', component: MapView },
  { path: '/compare', name: 'compare', component: CompareView },
  { path: '/itinerary', name: 'itinerary', component: ItineraryView },
  { path: '/wishlist', name: 'wishlist', component: WishlistView }
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
    const stored = sessionStorage.getItem('__scroll_' + to.fullPath)
    if (stored) {
      return new Promise((resolve) => {
        setTimeout(() => resolve({ top: Number(stored) }), 50)
      })
    }
    return { top: 0 }
  }
})
const referrerByRoute = new Map()

router.beforeEach((to, from, next) => {
  if (from && from.params && from.params.id) {
    referrerByRoute.delete(from.fullPath)
  }
  if (to.params && to.params.id && from && from.path && from.path !== to.path) {
    referrerByRoute.set(to.fullPath, from.fullPath)
  }
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
