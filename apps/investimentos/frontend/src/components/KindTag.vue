<script setup lang="ts">
// Etiqueta fixa da spec: fato (cinza), estimativa (azul), interpretação da IA (roxo).
const props = defineProps<{ kind: 'fato' | 'estimativa' | 'ia' }>()
const LABEL = { fato: 'Fato', estimativa: 'Estimativa', ia: 'Interpretação da IA' }
const CLS = { fato: 'border-muted/60 text-muted', estimativa: 'border-est/60 text-est', ia: 'border-ai/60 text-ai' }
</script>

<template>
  <span class="inline-block rounded border px-1.5 text-xs leading-5" :class="CLS[props.kind]">{{ LABEL[props.kind] }}</span>
</template>
