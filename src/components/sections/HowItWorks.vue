<template>
  <section class="how-it-works">
    <div class="section-heading">
      <p class="eyebrow">Como funciona</p>
      <h2 class="title">Do cadastro ao primeiro relatório, em minutos</h2>
    </div>

    <div class="path">
      <div
        v-for="(step, index) in steps"
        :key="step.title"
        class="stop"
        :class="index % 2 === 0 ? 'stop--left' : 'stop--right'"
      >
        <span class="stop-mark" aria-hidden="true">{{ step.number }}</span>
        <div class="stop-card">
          <h3>{{ step.title }}</h3>
          <p>{{ step.description }}</p>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const steps = [
  {
    number: '1',
    title: 'Crie sua conta',
    description: 'Cadastre-se de graça e monte sua empresa em menos de um minuto, sem burocracia.',
  },
  {
    number: '2',
    title: 'Registre o que entra e sai',
    description: 'Lance suas movimentações em poucos toques. Chega de planilha perdida.',
  },
  {
    number: '3',
    title: 'Entenda para onde vai o dinheiro',
    description: 'Relatórios e gráficos claros pra você decidir com mais confiança.',
  },
];
</script>

<style scoped>
.how-it-works {
  padding: 70px 25px 80px;
}

.section-heading {
  text-align: center;
  max-width: 520px;
  margin: 0 auto 56px;
}

.eyebrow {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  color: var(--color-success-dark);
  margin-bottom: 10px;
}

.title {
  font-family: var(--font-display);
  font-size: clamp(1.4rem, 3vw, 1.9rem);
  font-weight: 700;
  color: var(--color-text);
  line-height: 1.3;
}

.path {
  position: relative;
  max-width: 640px;
  margin: 0 auto;
  padding-left: 44px;
  border-left: 2px dashed var(--color-border);
}

.stop {
  position: relative;
  padding-bottom: 48px;
}

.stop:last-child {
  padding-bottom: 0;
}

.stop-mark {
  position: absolute;
  top: -2px;
  left: -63px;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-success-gradient);
  box-shadow: 0 0 0 5px var(--color-primary-glow);
  color: white;
  font-family: var(--font-display);
  font-size: 15px;
  font-weight: 800;
}

.stop-card {
  max-width: 420px;
}

.stop--left .stop-card { transform: rotate(-0.3deg); }
.stop--right .stop-card { transform: rotate(0.3deg); }

.stop-card h3 {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 8px;
}

.stop-card p {
  font-size: 14px;
  line-height: 1.6;
  color: var(--color-text-secondary);
}

@media (min-width: 700px) {
  .path {
    padding-left: 56px;
  }

  .stop-mark {
    left: -75px;
  }
}

@media (min-width: 1100px) {
  .how-it-works {
    padding: 56px 40px 64px;
  }

  .path {
    max-width: 680px;
  }
}
</style>
