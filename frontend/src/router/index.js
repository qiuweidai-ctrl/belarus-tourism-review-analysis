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
  routes
})

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAdmin) {
    const user = JSON.parse(localStorage.getItem('user') || 'null')
    if (!user || (user.role !== 'admin' && user.role !== 'moderator')) {
      return next('/login')
    }
  }
  next()
})

export default router
