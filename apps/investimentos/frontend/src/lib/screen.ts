import { watch } from 'vue'
import { useRoute } from 'vue-router'

/**
 * Publica no backend o que está aberto, para o Claude (via MCP) saber de que tela o Erick está falando.
 * Falha em silêncio: não ter contexto não pode quebrar o dashboard.
 */
export function usePublishScreen(details: () => Record<string, unknown>) {
  const route = useRoute()
  watch(
    () => ({ path: route.fullPath, ...details() }),
    (body) => {
      fetch('/api/screen-context', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...body, title: document.title, at: new Date().toISOString() }),
      }).catch((e) => console.warn('contexto da tela não publicado', e))
    },
    { immediate: true, deep: true },
  )
}
