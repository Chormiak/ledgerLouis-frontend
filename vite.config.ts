import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import { VitePWA } from 'vite-plugin-pwa'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
    VitePWA({
      registerType: 'autoUpdate',
      // /investimentos/ é outro app (apps/investimentos): o service worker não pode responder com o index do Ledger
      workbox: { navigateFallbackDenylist: [/^\/investimentos/] },
      includeAssets: ['favicon.ico', 'robots.txt'],
      manifest: {
        name: 'Ledger Louis',
        short_name: 'Ledger',
        description: 'PWA mobile para Ledger Frontend',
        theme_color: '#0a0b0b',
        background_color: '#0a0b0b',
        display: 'standalone',
        scope: '/',
        start_url: '/',
        icons: [
          {
            src: '/icons/icon-192x192.png',
            sizes: '192x192',
            type: 'image/png',
            purpose: 'any maskable'
          },
          {
            src: '/icons/icon-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any maskable'
          }
        ]
      }
    })
  ],
  // dev: o app de investimentos roda no próprio Vite (npm run dev:investimentos, porta 5175)
  server: { proxy: { '/investimentos': { target: 'http://localhost:5175', ws: true } } },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
})
