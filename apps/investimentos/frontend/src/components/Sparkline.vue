<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ values: number[] }>()
const W = 64
const H = 22

const points = computed(() => {
  const v = props.values
  if (v.length < 2) return ''
  const lo = Math.min(...v)
  const span = Math.max(...v) - lo || 1
  return v.map((x, i) => `${((i / (v.length - 1)) * W).toFixed(1)},${(H - 2 - ((x - lo) / span) * (H - 4)).toFixed(1)}`).join(' ')
})
const rising = computed(() => props.values.length > 1 && props.values.at(-1)! >= props.values[0])
</script>

<template>
  <svg v-if="points" :viewBox="`0 0 ${W} ${H}`" :width="W" :height="H" aria-hidden="true" class="shrink-0">
    <polyline :points="points" fill="none" :stroke="rising ? 'var(--up)' : 'var(--down)'" stroke-width="1.25" stroke-linejoin="round" />
  </svg>
  <span v-else :style="{ width: `${W}px` }" class="shrink-0" aria-hidden="true" />
</template>
