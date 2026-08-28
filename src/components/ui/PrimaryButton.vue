<template>
  <button
    class="primary-btn"
    :class="[
      `primary-btn--${variant}`,
      { 'primary-btn--compact': compact, 'primary-btn--icon': iconOnly },
    ]"
    :disabled="loading"
    @click="$emit('click')"
  >
    <span v-if="loading" class="spinner" />
    <slot v-else />
  </button>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    loading?: boolean;
    /** Cor semântica — mesma forma/tamanho em todas, só muda a cor. */
    variant?: 'primary' | 'danger' | 'neutral';
    /** Versão menor, para ações secundárias/inline (ex: "Atualizar", itens de lista). */
    compact?: boolean;
    /** Botão só com ícone — vira um círculo em vez de pill alongado. */
    iconOnly?: boolean;
  }>(),
  {
    loading: false,
    variant: 'primary',
    compact: false,
    iconOnly: false,
  },
);
defineEmits(['click']);
</script>

<style scoped>
/* Único componente de botão do app: sempre pill (999px), largura pelo
   conteúdo. "variant" muda só a cor; "compact"/"iconOnly" só o tamanho —
   nunca a forma, pra manter um visual consistente em qualquer contexto. */
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
  transition: transform 0.2s ease, box-shadow 0.2s ease, opacity 0.2s ease,
    border-color 0.2s ease, background 0.2s ease;
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

.primary-btn--danger {
  background: var(--color-danger-gradient);
  box-shadow: 0 4px 18px rgba(229, 33, 36, 0.22);
}

.primary-btn--danger:hover:not(:disabled) {
  box-shadow: 0 8px 26px rgba(229, 33, 36, 0.3);
}

.primary-btn--neutral {
  background: var(--color-surface);
  color: var(--color-text-secondary);
  border: 1.5px solid var(--color-border);
  box-shadow: none;
}

.primary-btn--neutral:hover:not(:disabled) {
  color: var(--color-text);
  border-color: var(--color-text-tertiary);
  transform: translateY(-1px);
  box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06);
}

.primary-btn--compact {
  padding: 9px 18px;
  min-height: 38px;
  font-size: 13.5px;
  gap: 6px;
}

.primary-btn--icon {
  padding: 0;
  width: 48px;
  min-height: 48px;
}

.primary-btn--icon.primary-btn--compact {
  width: 36px;
  min-height: 36px;
}

.spinner {
  width: 18px;
  height: 18px;
  border: 2.5px solid rgba(255, 255, 255, 0.35);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  display: inline-block;
}

.primary-btn--neutral .spinner {
  border-color: rgba(17, 24, 39, 0.15);
  border-top-color: var(--color-text-secondary);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
