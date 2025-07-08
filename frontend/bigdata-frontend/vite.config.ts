import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
        onError: (err, req, res) => {
          console.warn('代理错误:', err.message)
          // 当后端服务不可用时，提供一些基本的响应，避免前端完全挂掉
          if (req.url?.includes('/health')) {
            res.writeHead(200, { 'Content-Type': 'application/json' })
            res.end(JSON.stringify({ code: 1, msg: '后端服务未启动', data: null }))
          }
        }
      }
    }
  }
})
