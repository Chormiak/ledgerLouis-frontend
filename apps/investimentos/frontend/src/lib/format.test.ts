import { describe, expect, it } from 'vitest'
import { formatAsOf, formatBRL, formatCompact, formatFraction, formatPoints, formatRatio } from './format'

const norm = (s: string) => s.replace(/ | /g, ' ')

describe('format', () => {
  it('nulo vira travessão', () => {
    for (const f of [formatBRL, formatCompact, formatFraction, formatPoints, formatRatio, formatAsOf]) {
      expect(f(null)).toBe('—')
    }
  })

  it('moeda em pt-BR', () => {
    expect(norm(formatBRL(37.85))).toBe('R$ 37,85')
  })

  it('variação em pontos tem sinal explícito', () => {
    expect(formatPoints(1.25)).toBe('+1,25%')
    expect(formatPoints(-0.8)).toBe('−0,80%')
    expect(formatPoints(0)).toBe('0,00%')
  })

  it('fração vira porcentagem', () => {
    expect(formatFraction(0.25)).toBe('25,0%')
  })

  it('múltiplo com uma casa', () => {
    expect(formatRatio(10)).toBe('10,0')
  })

  it('valores grandes compactos', () => {
    expect(norm(formatCompact(492_000_000_000))).toBe('R$ 492 bi')
  })

  it('data e hora de São Paulo', () => {
    expect(formatAsOf('2026-10-29T17:05:00Z')).toBe('29/10/2026 14:05')
  })
})
