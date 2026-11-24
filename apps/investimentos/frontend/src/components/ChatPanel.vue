<script setup lang="ts">
import { useQueryClient } from '@tanstack/vue-query'
import { nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { streamChat, TOOL_LABEL } from '../lib/chat'
import { vAutoAnimate } from '@formkit/auto-animate/vue'
import PendingChanges from './PendingChanges.vue'

interface Message {
  role: 'user' | 'claude'
  text: string
  tools: string[]
  error?: string
  warning?: string
}

const STORE = 'ledgerlouis-chat'
const qc = useQueryClient()
const route = useRoute()

// conversa sobrevive a recarregar a página (só neste navegador)
function load(): { sessionId: string | null; messages: Message[] } {
  try {
    return JSON.parse(localStorage.getItem(STORE) ?? '') as { sessionId: string | null; messages: Message[] }
  } catch {
    return { sessionId: null, messages: [] }
  }
}
const saved = load()
const sessionId = ref<string | null>(saved.sessionId)
const messages = ref<Message[]>(saved.messages)
const input = ref('')
const busy = ref(false)
const list = ref<HTMLElement>()
let abort: AbortController | undefined

watch([sessionId, messages], () => {
  try {
    localStorage.setItem(STORE, JSON.stringify({ sessionId: sessionId.value, messages: messages.value.slice(-40) }))
  } catch {
    /* armazenamento indisponível: a conversa só não sobrevive ao recarregar */
  }
}, { deep: true })

const scroll = () => nextTick(() => list.value?.scrollTo({ top: list.value.scrollHeight }))

const SUGGESTIONS = ['O que você acha desta tela?', 'Como está minha carteira?', 'Monte a proposta deste mês', 'Explique os alertas novos']

async function send(text = input.value) {
  const message = text.trim()
  if (!message || busy.value) return
  input.value = ''
  messages.value.push({ role: 'user', text: message, tools: [] })
  const reply: Message = { role: 'claude', text: '', tools: [] }
  messages.value.push(reply)
  const live = messages.value.at(-1)! // a versão reativa, para a tela atualizar enquanto o texto chega
  busy.value = true
  abort = new AbortController()
  scroll()
  try {
    await streamChat(message, sessionId.value, (e) => {
      if (e.type === 'session') sessionId.value = e.session_id
      else if (e.type === 'text') live.text += e.text
      else if (e.type === 'tool') live.tools.push(e.name)
      else if (e.type === 'warning') live.warning = e.text
      else if (e.type === 'done' && e.is_error) live.error = e.error ?? 'O Gemini não conseguiu responder.'
      scroll()
    }, abort.signal)
  } catch (err) {
    if ((err as Error).name !== 'AbortError') live.error = (err as Error).message
  } finally {
    busy.value = false
    // o Claude pode ter gravado proposta, tese ou sugestão: atualizar o que estiver na tela
    for (const k of ['pending-changes', 'proposals', 'proposal', 'scoreboard', 'portfolio']) qc.invalidateQueries({ queryKey: [k] })
  }
}

function stop() {
  abort?.abort()
}

function reset() {
  stop()
  sessionId.value = null
  messages.value = []
}

function onKey(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    send()
  }
}

onBeforeUnmount(stop)
</script>

<template>
  <section aria-label="Conversa com o Gemini" class="flex h-full flex-col">
    <header class="flex items-center justify-between gap-2 border-b border-rule px-4 py-3">
      <div class="flex items-center gap-2">
        <span class="h-2 w-2 rounded-full" :class="busy ? 'animate-pulse bg-accent' : 'bg-up'" aria-hidden="true" />
        <h2 class="font-display text-lg">Gemini</h2>
        <span class="text-xs text-muted">{{ busy ? 'pensando…' : 'pronto' }}</span>
      </div>
      <div class="flex items-center gap-4">
        <button v-if="messages.length" type="button" class="text-xs text-muted hover:text-paper" @click="reset">Nova conversa</button>
        <slot name="actions" />
      </div>
    </header>

    <div ref="list" v-auto-animate class="flex-1 space-y-4 overflow-y-auto px-4 py-4" aria-live="polite">
      <div v-if="!messages.length" class="space-y-3">
        <p class="text-sm text-muted">
          Pergunte sobre o mercado, sua carteira ou o que está na tela. O Gemini lê os dados do LedgerLouis, pode
          abrir telas para você e sugerir mudanças, mas só você aplica.
        </p>
        <div class="flex flex-wrap gap-2">
          <button v-for="s in SUGGESTIONS" :key="s" type="button" class="rounded-full border border-rule px-3 py-1 text-xs text-muted hover:border-accent/60 hover:text-paper" @click="send(s)">
            {{ s }}
          </button>
        </div>
      </div>

      <article v-for="(m, i) in messages" :key="i" :class="m.role === 'user' ? 'ml-8' : 'mr-2'">
        <p v-if="m.role === 'user'" class="rounded-lg bg-raise px-3 py-2 text-sm text-paper">{{ m.text }}</p>
        <template v-else>
          <p class="mb-1 text-xs text-ai">Gemini, interpretação da IA</p>
          <ul v-if="m.tools.length" class="mb-2 flex flex-wrap gap-1">
            <li v-for="(t, j) in m.tools" :key="j" class="rounded border border-rule px-1.5 text-[11px] text-muted">{{ TOOL_LABEL[t] ?? t }}</li>
          </ul>
          <p v-if="m.text" class="whitespace-pre-line text-sm leading-relaxed">{{ m.text }}</p>
          <p v-else-if="busy && i === messages.length - 1" class="text-sm text-muted">…</p>
          <p v-if="m.warning" class="mt-1 text-xs text-accent">{{ m.warning }}</p>
          <p v-if="m.error" role="alert" class="mt-1 text-xs text-down">{{ m.error }}</p>
        </template>
      </article>
    </div>

    <div class="space-y-3 border-t border-rule p-3">
      <PendingChanges />
      <form class="flex items-end gap-2" @submit.prevent="send()">
        <label class="sr-only" for="chat-input">Mensagem para o Gemini</label>
        <textarea
          id="chat-input"
          v-model="input"
          rows="2"
          :placeholder="`Pergunte algo (você está em ${route.path === '/' ? 'Visão geral' : route.path})`"
          class="flex-1 resize-none rounded-lg border border-rule bg-ink px-3 py-2 text-sm text-paper placeholder:text-muted/70"
          @keydown="onKey"
        />
        <button v-if="!busy" type="submit" class="rounded-lg bg-accent px-3 py-2 text-sm font-medium text-ink disabled:opacity-50" :disabled="!input.trim()">Enviar</button>
        <button v-else type="button" class="rounded-lg border border-rule px-3 py-2 text-sm text-muted" @click="stop">Parar</button>
      </form>
    </div>
  </section>
</template>
