<template>
  <article class="dashboard-card" :class="toneClass">
    <header class="card-top">
      <div>
        <p class="card-title">{{ title }}</p>
        <p class="card-value">{{ value }}</p>
      </div>

      <slot name="icon" />
    </header>

    <p class="card-description">{{ description }}</p>

    <div class="card-footer">
      <div class="trend-pill" :class="trendClass">
        <ArrowUpRight v-if="tone !== 'negative'" :size="14" />
        <ArrowDownRight v-else :size="14" />
        <span>{{ trendValue }}</span>
      </div>

      <span class="trend-label">{{ trendLabel }}</span>
    </div>

    <div v-if="$slots.sparkline" class="sparkline-wrap">
      <slot name="sparkline" />
    </div>
  </article>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { ArrowDownRight, ArrowUpRight } from 'lucide-vue-next';

type Tone = 'positive' | 'negative' | 'neutral';

const props = defineProps<{
  title: string;
  value: string;
  description: string;
  trendValue: string;
  trendLabel: string;
  tone?: Tone;
}>();

const tone = computed(() => props.tone ?? 'neutral');

const toneClass = computed(() => ({
  'dashboard-card--positive': tone.value === 'positive',
  'dashboard-card--negative': tone.value === 'negative',
  'dashboard-card--neutral': tone.value === 'neutral',
}));

const trendClass = computed(() => ({
  'trend-pill--positive': tone.value !== 'negative',
  'trend-pill--negative': tone.value === 'negative',
}));
</script>

<style scoped>
.dashboard-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 100%;
  padding: 18px;
  border: 1px solid var(--color-border);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 14px 40px rgba(15, 23, 42, 0.06);
}

.dashboard-card--positive {
  box-shadow: 0 14px 40px rgba(29, 205, 108, 0.08);
}

.dashboard-card--negative {
  box-shadow: 0 14px 40px rgba(229, 33, 36, 0.08);
}

.card-top {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: flex-start;
}

.card-title {
  color: var(--color-text-secondary);
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 6px;
}

.card-value {
  color: var(--color-text);
  font-family: var(--font-display);
  font-size: clamp(1.2rem, 2.6vw, 1.7rem);
  font-weight: 800;
  line-height: 1.1;
}

.card-description {
  color: var(--color-text-secondary);
  font-size: 13px;
  line-height: 1.6;
}

.card-footer {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  justify-content: space-between;
}

.trend-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.trend-pill--positive {
  color: var(--color-success-dark);
  background: rgba(29, 205, 108, 0.12);
}

.trend-pill--negative {
  color: var(--color-danger);
  background: rgba(229, 33, 36, 0.12);
}

.trend-label {
  color: var(--color-text-tertiary);
  font-size: 12px;
  font-weight: 600;
}

.sparkline-wrap {
  margin-top: auto;
}
</style>
