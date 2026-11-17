import { afterEach, describe, expect, it, vi } from 'vitest'
import { streamChat, type ChatEvent } from './chat'

function sseResponse(chunks: string[]) {
  const body = new ReadableStream({
    start(c) {
      for (const ch of chunks) c.enqueue(new TextEncoder().encode(ch))
      c.close()
    },
  })
  return new Response(body, { status: 200, headers: { 'Content-Type': 'text/event-stream' } })
}

afterEach(() => vi.unstubAllGlobals())

describe('streamChat', () => {
  it('junta eventos que chegam partidos entre pedaços', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => sseResponse([
      'data: {"type":"session","session_id":"s1"}\n\ndata: {"type":"te',
      'xt","text":"Olá"}\n\n',
      'data: {"type":"done","is_error":false,"error":null}\n\n',
    ])))
    const got: ChatEvent[] = []
    await streamChat('oi', null, (e) => got.push(e))
    expect(got).toEqual([
      { type: 'session', session_id: 's1' },
      { type: 'text', text: 'Olá' },
      { type: 'done', is_error: false, error: null },
    ])
  })

  it('erro HTTP vira exceção com a mensagem do servidor', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => new Response(JSON.stringify({ error: 'envie JSON' }), { status: 415 })))
    await expect(streamChat('oi', null, () => {})).rejects.toThrow('envie JSON')
  })
})
