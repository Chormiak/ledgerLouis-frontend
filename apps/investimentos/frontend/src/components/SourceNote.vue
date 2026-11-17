<script setup lang="ts">
import { formatAsOf } from '../lib/format'

defineProps<{ source: string | null | undefined; at: string | null | undefined; label?: string }>()
</script>

<template>
  <p class="text-xs text-muted">
    <template v-if="source">
      {{ label ?? 'Fonte' }}: {{ source }}, atualizado em <time :datetime="at ?? undefined" class="num">{{ formatAsOf(at) }}</time>
    </template>
    <template v-else>{{ label ?? 'Fonte' }}: sem dados ainda</template>
  </p>
</template>
