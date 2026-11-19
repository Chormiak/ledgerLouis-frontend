import { apiFetch } from '../api'
// Cliente do chat: POST /api/chat devolve eventos SSE (session, text, tool, warning, done).
export type ChatEvent =
  | { type: 'session'; session_id: string }
  | { type: 'text'; text: string }
  | { type: 'tool'; name: string }
  | { type: 'warning'; text: string }
  | { type: 'done'; is_error: boolean; error: string | null }

/** Lê o stream e chama onEvent a cada evento. Termina quando o servidor fecha a conexão. */
export async function streamChat(
  message: string,
  sessionId: string | null,
  onEvent: (e: ChatEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  const r = await apiFetch('chat', {
    method: 'POST',
    body: JSON.stringify({ message, session_id: sessionId }),
    signal,
  })
  if (!r.ok || !r.body) {
    const data = await r.json().catch(() => ({}))
    throw new Error(data.detail ?? data.message ?? `O chat respondeu ${r.status}`)
  }
  const reader = r.body.pipeThrough(new TextDecoderStream()).getReader()
  let buffer = ''
  for (;;) {
    const { value, done } = await reader.read()
    if (done) break
    buffer += value
    const parts = buffer.split('\n\n')
    buffer = parts.pop() ?? '' // o último pedaço pode estar incompleto
    for (const part of parts) {
      if (part.startsWith('data: ')) onEvent(JSON.parse(part.slice(6)))
    }
  }
}

/** Nome da ferramenta MCP -> o que o Erick lê enquanto o Claude trabalha. */
export const TOOL_LABEL: Record<string, string> = {
  get_screen_context: 'olhou a tela aberta',
  list_groups: 'consultou setores e nichos',
  get_group: 'abriu um grupo',
  list_assets: 'consultou as ações',
  get_asset: 'consultou uma ação',
  get_macro: 'consultou a macro',
  get_news: 'leu as notícias',
  get_profile: 'leu seu perfil',
  get_portfolio: 'leu sua carteira',
  get_latest_proposal: 'leu a última proposta',
  save_proposal_draft: 'gravou um rascunho de proposta',
  record_thesis: 'registrou uma tese no placar',
  get_alerts: 'leu os alertas',
  get_scoreboard: 'leu o placar',
  show_on_screen: 'abriu uma tela',
  propose_holding_change: 'sugeriu uma mudança na carteira',
  propose_profile_change: 'sugeriu uma mudança no perfil',
  get_pending_changes: 'conferiu as sugestões pendentes',
}
