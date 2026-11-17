import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { fetchScreenCommands } from '../api'

/**
 * Executa os pedidos do Claude para o dashboard (ex.: abrir uma ação), venham do chat da página ou do terminal.
 * Consulta o backend a cada poucos segundos; só os comandos criados depois de a página abrir são executados.
 */
export function useScreenCommands(intervalMs = 2500) {
  const router = useRouter()
  const notice = ref<{ path: string; reason: string } | null>(null)
  let after: number | undefined
  let timer: ReturnType<typeof setInterval> | undefined
  let hide: ReturnType<typeof setTimeout> | undefined

  async function poll() {
    try {
      const r = await fetchScreenCommands(after)
      if (after !== undefined) {
        for (const c of r.commands) {
          if (c.action !== 'navigate') continue
          await router.push(c.payload.path)
          notice.value = c.payload
          clearTimeout(hide)
          hide = setTimeout(() => (notice.value = null), 6000)
        }
      }
      after = r.latest_id
    } catch {
      /* backend fora do ar: tenta de novo no próximo ciclo */
    }
  }

  onMounted(() => {
    poll()
    timer = setInterval(poll, intervalMs)
  })
  onBeforeUnmount(() => {
    clearInterval(timer)
    clearTimeout(hide)
  })
  return { notice }
}
