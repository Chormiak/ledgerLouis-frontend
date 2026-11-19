import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

// Servido pelo Ledger em /investimentos/ (mesma origem: usa o mesmo login). No dev, o Vite do
// Ledger repassa /investimentos para cá; no build, sai em Frontend/dist/investimentos.
export default defineConfig({
  base: '/investimentos/',
  envDir: '../../..', // mesmo .env do Ledger (VITE_API_BASE_URL)
  plugins: [vue(), tailwindcss()],
  server: { port: 5175, strictPort: true },
  build: { outDir: '../../../dist/investimentos', emptyOutDir: true },
})
