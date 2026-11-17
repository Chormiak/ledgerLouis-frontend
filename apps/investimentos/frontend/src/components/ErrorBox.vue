<script setup lang="ts">
defineProps<{ error: Error | null | undefined }>()
</script>

<template>
  <div v-if="error" role="alert" class="mb-6 rounded border border-down/50 px-4 py-3 text-sm">
    Não foi possível falar com a API. Confira se o backend está rodando em <code class="num">localhost:8000</code>.
    <span class="text-muted">({{ error.message }})</span>
  </div>
</template>
