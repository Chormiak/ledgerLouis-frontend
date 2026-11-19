import { VueQueryPlugin } from '@tanstack/vue-query'
import { createApp } from 'vue'
import App from './App.vue'
import { apiFetch } from './api'
import { router } from './router'
import './style.css'

const retry = (count: number, error: Error) => !error.message.includes('404') && count < 2

apiFetch('sync-trigger', { method: 'POST' }).catch(() => {}) // dispara a atualização dos dados; cada job já é protegido por TTL

createApp(App)
  .use(VueQueryPlugin, { queryClientConfig: { defaultOptions: { queries: { retry } } } })
  .use(router)
  .mount('#app')
