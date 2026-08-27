<template>
  <button class="primary-btn" :disabled="loading" @click="$emit('click')">
    <span v-if="loading" class="spinner" />
    <span v-else><slot /></span>
  </button>
</template>

<script setup lang="ts">
defineProps({ loading: { type: Boolean, default: false } })
defineEmits(['click'])
</script>

<style scoped>
/* Pill inspirado no CTA do hero: largura pelo conteúdo (nunca 100%) e
   auto-centralizado, pra não dominar a linha em formulários verticais. */
.primary-btn {
  align-self: center;
  width: auto;
  padding: 14px 28px;
  background: var(--color-success-gradient);
  color: white;
  font-family: var(--font-body);
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 0.02em;
  border: none;
  border-radius: 999px;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, opacity 0.2s ease;
  box-shadow: 0 4px 18px var(--color-primary-glow);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 48px;
  white-space: nowrap;
}
.primary-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 26px var(--color-primary-glow);
}
.primary-btn:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 3px 12px var(--color-primary-glow);
}
.primary-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}
.spinner {
  width: 18px; height: 18px;
  border: 2.5px solid rgba(255,255,255,0.35);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  display: inline-block;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>