// Contrato de GET /api/assets e GET /api/macro (backend/ledgerlouis/market/views.py).
export interface Quote {
  price: number | null
  change_pct: number | null
  volume: number | null
  market_cap: number | null
  source: string
  fetched_at: string
}

export interface Indicators {
  pe: number | null
  ev_ebitda: number | null
  net_debt_ebitda: number | null
  net_margin: number | null
  roe: number | null
}

export interface Asset {
  ticker: string
  name: string
  market: 'B3' | 'US'
  sector: string
  subsector: string
  logo_url: string
  quote: Quote | null
  indicators: Indicators
  fundamentals_source: string | null
  fundamentals_fetched_at: string | null
}

export interface MacroPoint {
  code: string
  name: string
  unit: string
  date: string
  value: number
  source: string
  fetched_at: string
}

const API = `${(import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000').replace(/\/+$/, '')}/investments/`

/** Chama o backend do LedgerLouis com o login do app principal (mesma origem, mesmo localStorage). */
export async function apiFetch(path: string, init: RequestInit = {}): Promise<Response> {
  const token = localStorage.getItem('token')
  const r = await fetch(API + path, {
    ...init,
    headers: {
      ...(init.body === undefined ? {} : { 'Content-Type': 'application/json' }),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  })
  if (r.status === 401) location.assign('/entrar') // sem login (ou expirado): volta para o Ledger entrar
  return r
}

async function get<T>(path: string): Promise<T> {
  const r = await apiFetch(path)
  if (!r.ok) throw new Error(`A API respondeu ${r.status} em /investments/${path}`)
  return r.json()
}

export const fetchAssets = () => get<Asset[]>('assets')
export const fetchMacro = () => get<MacroPoint[]>('macro')

export interface Medians {
  pe: number | null
  ev_ebitda: number | null
  net_debt_ebitda: number | null
  net_margin: number | null
  roe: number | null
}

export interface GroupSummary {
  kind: 'sector' | 'niche'
  slug: string
  name: string
  count: number
  market_cap: number | null
  change_pct: number | null
  medians: Partial<Medians>
}

export interface NewsItem {
  title: string
  url: string
  source: string
  kind: 'fato_relevante' | 'comunicado' | 'noticia'
  published_at: string
  tickers: string[]
}

export interface GroupDetail extends GroupSummary {
  description: string
  members: Asset[]
  macro: MacroPoint[]
  news: NewsItem[]
}

export const fetchGroups = () => get<{ sectors: GroupSummary[]; niches: GroupSummary[] }>('groups')
export const fetchGroup = (kind: string, slug: string) => get<GroupDetail>(`groups/${kind}/${slug}`)

// ---- Carteira (fase 4) ----

export interface Profile {
  horizon_years: number | null
  risk_tolerance: '' | 'conservador' | 'moderado' | 'arrojado'
  monthly_contribution: number | null
  avoid_sectors: string[]
  notes: string
  alert_daily_drop_pct: number
  alert_max_asset_weight: number
  alert_max_sector_weight: number
  missing: string[]
}

export interface Position {
  ticker: string
  name: string
  sector: string
  quantity: number
  avg_price: number | null
  price: number | null
  change_pct: number | null
  gain_pct: number | null
  value: number | null
  weight: number | null
  source: string | null
  fetched_at: string | null
}

export interface Portfolio {
  positions: Position[]
  total: number | null
  unpriced: string[]
  exposure: { sector: Record<string, number> }
  profile: Profile
}

export type Decision = 'pendente' | 'aprovado' | 'recusado' | 'ajustado'

export interface ProposalItem {
  id: string
  ticker: string
  name: string
  sector: string
  action: 'entrar' | 'sair' | 'aumentar' | 'reduzir' | 'manter'
  target_weight: number
  thesis: string
  risks: string
  invalidation: string
  sources: string[]
  price_at_proposal: number | null
  current_price: number | null
  decision: Decision
  adjusted_weight: number | null
  comment: string
  decided_at: string | null
}

export interface ProposalHead {
  id: string
  period: string
  created_at: string
  status: 'rascunho' | 'em_revisao' | 'concluida'
  count: number
}

export interface Proposal extends ProposalHead {
  summary: string
  profile_snapshot: Record<string, unknown>
  items: ProposalItem[]
  approved_weight: number
}

export interface Alert {
  id: string
  kind: 'queda_forte' | 'concentracao_ativo' | 'concentracao_setor' | 'fato_relevante'
  title: string
  ticker: string | null
  detail: Record<string, string>
  created_on: string
  seen: boolean
}

export interface ScoreRow {
  ticker: string
  summary: string
  expectation: 'alta' | 'baixa' | 'neutra'
  origin: string
  decision: string
  entry_price: number | null
  current_price: number | null
  return_pct: number | null
  hit: boolean | null
  created_at: string
  price_source: string | null
  price_fetched_at: string | null
}

export interface Scoreboard {
  rows: ScoreRow[]
  scored: number
  hits: number
  hit_rate: number | null
}

async function send<T>(method: string, path: string, body?: unknown): Promise<T> {
  const r = await apiFetch(path, { method, body: body === undefined ? undefined : JSON.stringify(body) })
  if (!r.ok) {
    const data = await r.json().catch(() => ({}))
    throw new Error(data.detail ?? data.message ?? `A API respondeu ${r.status}`)
  }
  return r.status === 204 ? (undefined as T) : r.json()
}

export const fetchProfile = () => get<Profile>('profile')
export const saveProfile = (p: Partial<Profile>) => send<Profile>('PUT', 'profile', p)
export const fetchPortfolio = () => get<Portfolio>('portfolio')
export const saveHolding = (ticker: string, quantity: string, avg_price: string) =>
  send<Portfolio>('PUT', `holdings/${ticker}`, { quantity, avg_price: avg_price || null })
export const deleteHolding = (ticker: string) => send<void>('DELETE', `holdings/${ticker}`)
export const fetchProposals = () => get<ProposalHead[]>('proposals')
export const fetchProposal = (id: string) => get<Proposal>(`proposals/${id}`)
export const decide = (itemId: string, decision: Decision, adjusted_weight: number | null, comment: string) =>
  send<ProposalItem>('POST', `proposal-items/${itemId}/decision`, { decision, adjusted_weight, comment })
export const fetchAlerts = () => get<Alert[]>('alerts')
export const markAlertSeen = (id: string) => send<void>('POST', `alerts/${id}/seen`)
export const fetchScoreboard = () => get<Scoreboard>('scoreboard')

// ---- Página da ação ----

export type Health = 'melhor' | 'na_media' | 'pior' | null

export interface Bar {
  date: string
  open: number | null
  high: number | null
  low: number | null
  close: number
  volume: number | null
}

export interface AssetFull extends Asset {
  history: {
    source: string | null
    fetched_at: string | null
    days: number
    rsi14: number | null
    volatility: number | null
    return_1m: number | null
    return_period: number | null
    bars: Bar[]
    sma20: (number | null)[]
  }
  sector_group: { slug: string; name: string; count: number; medians: Partial<Medians> } | null
  health: Record<keyof Indicators, Health>
  niches: { slug: string; name: string }[]
  news: NewsItem[]
}

export const fetchAssetFull = (ticker: string) => get<AssetFull>(`assets/${ticker}`)

// ---- Claude no dashboard ----

export interface PendingChange {
  id: string
  kind: 'holding' | 'profile'
  payload: Record<string, unknown>
  reason: string
  status: 'pendente' | 'aplicada' | 'recusada'
  created_at: string
}

export interface ScreenCommand {
  id: string
  action: 'navigate'
  payload: { path: string; reason: string }
}

export const fetchSparklines = () => get<Record<string, number[]>>('sparklines')
export const fetchCategoryNews = (category: 'geopolitica' | 'ia_bolha') => get<NewsItem[]>(`news/${category}`)
export const fetchPendingChanges = () => get<PendingChange[]>('pending-changes')
export const decideChange = (id: string, verb: 'apply' | 'reject') => send<PendingChange>('POST', `pending-changes/${id}/${verb}`)
export const fetchScreenCommands = (after?: string) =>
  get<{ latest_id: string; commands: ScreenCommand[] }>(`screen-commands${after === undefined ? '' : `?after=${after}`}`)
