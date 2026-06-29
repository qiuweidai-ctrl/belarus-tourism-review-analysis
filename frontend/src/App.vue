<template>
  <div id="app">
    <nav class="navbar">
      <div class="nav-brand">
        <router-link to="/">{{ $t('app.title') }}</router-link>
      </div>
      <div class="nav-links">
        <router-link to="/">{{ $t('nav.home') }}</router-link>
        <router-link to="/attractions">{{ $t('nav.attractions') }}</router-link>
        <router-link to="/articles">{{ $t('nav.articles') }}</router-link>
        <router-link to="/qa">Q&amp;A</router-link>
        <router-link to="/recommendations" v-if="isLoggedIn">{{ $t('nav.recommendations') }}</router-link>
        <router-link to="/profile" v-if="isLoggedIn">{{ $t('nav.profile') }}</router-link>
        <router-link to="/admin" v-if="currentUser && (currentUser.role === 'admin' || currentUser.role === 'moderator')">Admin</router-link>
        <router-link to="/login" v-if="!isLoggedIn">{{ $t('nav.login') }}</router-link>
        <router-link to="/register" v-if="!isLoggedIn">{{ $t('nav.register') }}</router-link>
        <button @click="logout" v-if="isLoggedIn" class="btn-link">{{ $t('nav.logout') }}</button>
      </div>
    </nav>
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const isLoggedIn = computed(() => !!localStorage.getItem('token'))
const currentUser = computed(() => JSON.parse(localStorage.getItem('user') || 'null'))

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/login')
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f5f7fa;
  color: #333;
  line-height: 1.6;
}

.navbar {
  background-color: #1a5e63;
  color: white;
  padding: 0 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

.nav-brand a {
  color: white;
  text-decoration: none;
  font-size: 1.3rem;
  font-weight: bold;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.nav-links a {
  color: rgba(255,255,255,0.85);
  text-decoration: none;
  font-size: 0.95rem;
  transition: color 0.2s;
}

.nav-links a:hover,
.nav-links a.router-link-active {
  color: white;
}

.btn-link {
  background: none;
  border: none;
  color: rgba(255,255,255,0.85);
  font-size: 0.95rem;
  cursor: pointer;
  transition: color 0.2s;
}

.btn-link:hover {
  color: white;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.btn-primary {
  background-color: #1a5e63;
  color: white;
  border: none;
  padding: 0.6rem 1.4rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.95rem;
  transition: background-color 0.2s;
}

.btn-primary:hover {
  background-color: #134a4e;
}

.btn-primary:disabled {
  background-color: #aaa;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: white;
  color: #1a5e63;
  border: 1px solid #1a5e63;
  padding: 0.6rem 1.4rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.95rem;
  transition: background-color 0.2s;
}

.btn-secondary:hover {
  background-color: #e8f4f5;
}

.card {
  background: white;
  border-radius: 10px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

input, textarea, select {
  width: 100%;
  padding: 0.6rem 0.8rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.95rem;
  outline: none;
  transition: border-color 0.2s;
}

input:focus, textarea:focus, select:focus {
  border-color: #1a5e63;
}

.page-title {
  font-size: 1.8rem;
  color: #1a5e63;
  margin-bottom: 1.5rem;
}

.loading {
  text-align: center;
  padding: 3rem;
  color: #888;
}

.error-msg {
  background-color: #fee;
  border: 1px solid #fcc;
  color: #c33;
  padding: 0.8rem;
  border-radius: 6px;
  margin-bottom: 1rem;
}

.success-msg {
  background-color: #efe;
  border: 1px solid #cfc;
  color: #383;
  padding: 0.8rem;
  border-radius: 6px;
  margin-bottom: 1rem;
}
</style>
