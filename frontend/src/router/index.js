import { createRouter, createWebHistory } from 'vue-router'
const HomeView = () => import('../views/HomeView.vue')
const AttractionsView = () => import('../views/AttractionsView.vue')
const AttractionDetailView = () => import('../views/AttractionDetailView.vue')
const LoginView = () => import('../views/LoginView.vue')
const RegisterView = () => import('../views/RegisterView.vue')
const RecommendationsView = () => import('../views/RecommendationsView.vue')
const ProfileView = () => import('../views/ProfileView.vue')
const ArticlesView = () => import('../views/ArticlesView.vue')
const ArticleDetailView = () => import('../views/ArticleDetailView.vue')
const ArticleWriteView = () => import('../views/ArticleWriteView.vue')
const QandAView = () => import('../views/QandAView.vue')
const AdminDashboardView = () => import('../views/AdminDashboardView.vue')
const InsightsView = () => import('../views/InsightsView.vue')
const WordCloudView = () => import('../views/WordCloudView.vue')
const RankingsView = () => import('../views/RankingsView.vue')
const MapView = () => import('../views/MapView.vue')
const CompareView = () => import('../views/CompareView.vue')
const ItineraryView = () => import('../views/ItineraryView.vue')
const WishlistView = () => import('../views/WishlistView.vue')

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

// 前端控制页面入口，实际权限仍由后端检查。
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
