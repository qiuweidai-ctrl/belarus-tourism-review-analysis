<template>
  <div class="auth-page">
    <router-link to="/" class="auth-brand">
      <span>BT</span>
      <strong>Belarus Tourism</strong>
    </router-link>
    <div class="auth-card">
      <div class="auth-heading">
        <span class="auth-kicker">WELCOME BACK</span>
      <h2>{{ $t('auth.loginTitle') }}</h2>
        <p>Sign in to continue planning your Belarus journey.</p>
      </div>
      <div v-if="error" class="error-msg">{{ error }}</div>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label>{{ $t('auth.username') }}</label>
          <input v-model="form.username" type="text" autocomplete="username" placeholder="Enter your username" required />
        </div>
        <div class="form-group">
          <label>{{ $t('auth.password') }}</label>
          <input v-model="form.password" type="password" autocomplete="current-password" placeholder="Enter your password" required />
        </div>
        <label class="remember-row">
          <input type="checkbox" />
          <span>Remember me</span>
        </label>
        <button type="submit" class="btn btn-primary auth-submit" :disabled="loading">
          {{ loading ? $t('common.loading') : $t('auth.loginBtn') }}
        </button>
        <p class="auth-switch">
          {{ $t('auth.noAccount') }}
          <router-link to="/register">{{ $t('nav.register') }}</router-link>
        </p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI } from '@/api/client.js'

const router = useRouter()
const form = ref({ username: '', password: '' })
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await authAPI.login(form.value)
    localStorage.setItem('token', res.data.access_token)
    localStorage.setItem('user', JSON.stringify(res.data.user))
    window.dispatchEvent(new Event('app:auth-changed'))
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.error || 'Login failed'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 2rem;
  background:
    linear-gradient(110deg, rgba(4, 32, 45, .72), rgba(6, 78, 75, .28)),
    url('/static/images/attractions/47.jpg') center / cover no-repeat;
  isolation: isolate;
}
.auth-page::after { content: ''; position: absolute; inset: 0; z-index: -1; background: linear-gradient(0deg, rgba(3, 20, 31, .28), transparent 45%); }
.auth-brand { position: absolute; top: 2rem; left: 2.4rem; display: flex; align-items: center; gap: .65rem; color: #fff; }
.auth-brand > span { width: 38px; height: 38px; display: grid; place-items: center; border: 1px solid rgba(255,255,255,.4); border-radius: 10px; background: rgba(255,255,255,.16); font-weight: 800; }
.auth-brand strong { color: #fff; font-size: 1.05rem; }
.auth-card {
  width: 100%;
  max-width: 430px;
  padding: 2.35rem;
  background: rgba(255,255,255,.96);
  border: 1px solid rgba(255,255,255,.7);
  border-radius: 14px;
  box-shadow: 0 24px 60px rgba(3, 20, 31, .3);
  backdrop-filter: blur(16px);
}
.auth-heading { margin-bottom: 1.5rem; text-align: center; }
.auth-kicker { color: var(--brand-600); font-size: .7rem; font-weight: 800; letter-spacing: .16em; }
.auth-card h2 { margin: .35rem 0 .4rem; color: #16313d; font-size: 1.7rem; }
.auth-heading p { margin: 0; color: #64748b; font-size: .88rem; }
.form-group { margin-bottom: 1.05rem; }
.form-group label { color: #475569; }
.auth-card input:not([type='checkbox']) { background: #f8fafc; color: #0f172a; }
.remember-row { display: flex; align-items: center; gap: .5rem; margin: -.15rem 0 1.1rem; color: #64748b; font-size: .8rem; font-weight: 500; }
.remember-row input { width: 15px; height: 15px; accent-color: var(--brand-600); }
.auth-submit { width: 100%; min-height: 44px; }
.auth-switch { margin: 1.15rem 0 0; color: #64748b; text-align: center; font-size: .84rem; }
.auth-switch a { color: var(--brand-700); font-weight: 700; }
@media (max-width: 600px) {
  .auth-page { padding: 5.5rem 1rem 2rem; align-items: flex-start; }
  .auth-brand { top: 1.3rem; left: 1.25rem; }
  .auth-card { padding: 1.7rem 1.35rem; }
}
</style>
