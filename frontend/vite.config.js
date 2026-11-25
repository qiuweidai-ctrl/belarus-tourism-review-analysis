import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': 'http://localhost:5000',
      '/static': 'http://localhost:5000',
      '/media': 'http://localhost:5000'
    }
  },
  // 网页产物单独存，重新构建时不会清掉景点图片。
  build: {
    outDir: '../backend/static/web',
    emptyOutDir: true
  }
})
