type N = number | null | undefined

const DASH = '—'
const brl = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })
const usd = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' })
const compact = new Intl.NumberFormat('pt-BR', { notation: 'compact', maximumFractionDigits: 1 })
const two = new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
const one = new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 })
const dateTime = new Intl.DateTimeFormat('pt-BR', {
  dateStyle: 'short',
  timeStyle: 'short',
  timeZone: 'America/Sao_Paulo',
})

const missing = (v: unknown): v is null | undefined => v === null || v === undefined

export const formatBRL = (v: N) => (missing(v) ? DASH : brl.format(v))
export const formatUSD = (v: N) => (missing(v) ? DASH : usd.format(v))

/** Preço na moeda certa pro mercado do ativo ('US' = dólar, senão real). */
export const formatMoney = (v: N, market?: string) => (market === 'US' ? formatUSD(v) : formatBRL(v))

/** Variação em pontos percentuais (1.25 = +1,25%), com sinal sempre visível. */
export const formatPoints = (v: N) => {
  if (missing(v)) return DASH
  const sign = v > 0 ? '+' : v < 0 ? '−' : ''
  return `${sign}${two.format(Math.abs(v))}%`
}

/** Fração (0.25) como porcentagem (25,0%). */
export const formatFraction = (v: N) => (missing(v) ? DASH : `${one.format(v * 100)}%`)

export const formatRatio = (v: N) => (missing(v) ? DASH : one.format(v))

export const formatCompact = (v: N, market?: string) =>
  missing(v) ? DASH : `${market === 'US' ? 'US$' : 'R$'} ${compact.format(v)}`

export const formatAsOf = (iso: string | null | undefined) =>
  missing(iso) ? DASH : dateTime.format(new Date(iso)).replace(',', '')

/** Classe de cor e seta de alta/queda; zero e ausente ficam neutros. Cor nunca sozinha: sempre com seta e sinal. */
export const trendClass = (v: N) => (!v ? '' : v > 0 ? 'text-up' : 'text-down')
export const trendArrow = (v: N) => (!v ? '' : v > 0 ? '▲' : '▼')
