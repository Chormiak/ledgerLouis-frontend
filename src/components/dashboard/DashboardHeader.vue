<template>
  <section class="dashboard-header">
    <div class="header-copy">
      <p class="eyebrow">Resumo financeiro</p>
      <h1>Dashboard de relatórios</h1>
      <p class="subtitle">
        Acompanhe saldo, entradas, saídas e a distribuição dos gastos com uma leitura rápida e visual.
      </p>
    </div>

    <div class="header-actions">
      <div class="period-chip" aria-label="Período atual">
        <CalendarDays :size="18" />
        <span>Mensal</span>
      </div>

      <button class="action-button action-button--ghost" type="button">
        <Download :size="18" />
        Exportar
      </button>

      <button class="action-button action-button--primary" type="button">
        <Plus :size="18" />
        Novo lançamento
      </button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { CalendarDays, Download, Plus } from 'lucide-vue-next';
</script>

<style scoped>
.dashboard-header {
  display: grid;
  gap: 18px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.65);
  border-radius: 28px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.92), rgba(248, 250, 252, 0.88));
  box-shadow: 0 18px 50px rgba(15, 23, 42, 0.08);
  backdrop-filter: blur(18px);
}

.eyebrow {
  color: var(--color-success-dark);
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 10px;
}

h1 {
  font-family: var(--font-display);
  font-size: clamp(1.8rem, 4vw, 3rem);
  line-height: 1.05;
  color: var(--color-text);
  margin-bottom: 12px;
}

.subtitle {
  max-width: 58ch;
  color: var(--color-text-secondary);
  line-height: 1.7;
}

.header-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.period-chip,
.action-button {
  min-height: 46px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 0 16px;
  font-weight: 700;
}

.period-chip {
  border: 1px solid var(--color-border);
  background: rgba(255, 255, 255, 0.86);
  color: var(--color-text-secondary);
}

.action-button {
  border: none;
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.action-button:active {
  transform: scale(0.98);
}

.action-button--ghost {
  background: var(--color-surface);
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.action-button--primary {
  color: white;
  background: var(--color-success-gradient);
  box-shadow: 0 16px 24px rgba(29, 205, 108, 0.24);
}

@media (min-width: 900px) {
  .dashboard-header {
    grid-template-columns: minmax(0, 1.6fr) auto;
    align-items: center;
    padding: 28px 30px;
  }

  .header-actions {
    justify-content: flex-end;
  }
}
</style>
