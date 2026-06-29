<template>
  <div class="auth-page">
    <div class="auth-card card">
      <h2>{{ $t('auth.registerTitle') }}</h2>
      <div v-if="error" class="error-msg">{{ error }}</div>
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label>{{ $t('auth.username') }}</label>
          <input v-model="form.username" type="text" required />
        </div>
        <div class="form-group">
          <label>{{ $t('auth.email') }}</label>
          <input v-model="form.email" type="email" required />
        </div>
        <div class="form-group">
          <label>{{ $t('auth.password') }}</label>
          <input v-model="form.password" type="password" required />
        </div>
        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? $t('common.loading') : $t('auth.registerBtn') }}
        </button>
        <p class="auth-switch">
          {{ $t('auth.hasAccount') }}
          <router-link to="/login">{{ $t('nav.login') }}</router-link>
        </p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI } from '../api/client.js'

const router = useRouter()
const form = ref({ username: '', email: '', password: '' })
const loading = ref(false)
const error = ref('')

const handleRegister = async () => {
  loading.value = true
  error.value = ''
  try {
    await authAPI.register(form.value)
    router.push('/login')
  } catch (e) {
    error.value = e.response?.data?.error || 'Registration failed'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 50vh;
}

.auth-card {
  width: 100%;
  max-width: 420px;
  padding: 2.5rem;
}

.auth-card h2 {
  text-align: center;
  color: #1a5e63;
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.2rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.4rem;
  font-weight: 500;
  color: #555;
}

.auth-card button {
  width: 100%;
  margin-top: 0.5rem;
}

.auth-switch {
  text-align: center;
  margin-top: 1rem;
  font-size: 0.9rem;
  color: #666;
}

.auth-switch a {
  color: #1a5e63;
  font-weight: 600;
}
</style>
