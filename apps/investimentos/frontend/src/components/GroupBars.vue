<script setup lang="ts">
import { computed } from 'vue'
import type { GroupSummary } from '../api'
import { formatCompact, formatPoints, trendArrow, trendClass } from '../lib/format'

// scale: maior variação absoluta entre as listas comparadas, para barras iguais significarem o mesmo
const props = defineProps<{ groups: GroupSummary[]; scale?: number }>()

const sorted = computed(() => [...props.groups].sort((a, b) => (b.change_pct ?? -Infinity) - (a.change_pct ?? -Infinity)))
const scale = computed(() => props.scale ?? Math.max(1, ...props.groups.map((g) => Math.abs(g.change_pct ?? 0))))
const width = (v: number | null) => `${(Math.abs(v ?? 0) / scale.value) * 50}%`
</script>

<template>
  <ul class="divide-y divide-rule/60 border-y border-rule">
    <li v-for="g in sorted" :key="g.slug">
      <RouterLink
        :to="`/grupos/${g.kind}/${g.slug}`"
        class="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-x-4 gap-y-2 py-3 hover:bg-panel sm:grid-cols-[14rem_minmax(0,1fr)_6rem]"
      >
        <span class="col-start-1 row-start-1">
          <span class="text-paper">{{ g.name }}</span>
          <span class="block text-xs text-muted">{{ g.count }} {{ g.count === 1 ? 'ação' : 'ações' }}, {{ formatCompact(g.market_cap) }}</span>
        </span>
        <span class="relative col-span-2 row-start-2 h-3 sm:col-span-1 sm:col-start-2 sm:row-start-1" aria-hidden="true">
          <span class="absolute inset-y-0 left-1/2 w-px bg-rule" />
          <span
            v-if="g.change_pct"
            class="absolute inset-y-0 rounded-sm"
            :class="g.change_pct > 0 ? 'left-1/2 bg-up' : 'right-1/2 bg-down'"
            :style="{ width: width(g.change_pct) }"
          />
        </span>
        <span
          class="num col-start-2 row-start-1 text-right sm:col-start-3"
          :class="trendClass(g.change_pct)"
        >
          <span aria-hidden="true" class="mr-1 text-[10px]">{{ trendArrow(g.change_pct) }}</span>{{ formatPoints(g.change_pct) }}
        </span>
      </RouterLink>
    </li>
  </ul>
</template>
