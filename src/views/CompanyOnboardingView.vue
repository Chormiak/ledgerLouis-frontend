<template>
  <main class="onboarding-page">
    <section class="onboarding-container">
      <header class="header-block">
        <p class="kicker">Comece por aqui</p>
        <h1>Vamos configurar sua <span class="accent-text">empresa</span></h1>
        <p class="description">
          Escolha se quer entrar em uma empresa existente ou criar a sua do zero.
        </p>
      </header>

      <div class="option-list">
        <button class="option-row" @click="goToJoin">
          <span class="option-icon">
            <KeyRound :size="20" />
          </span>
          <span class="option-copy">
            <strong>Entrar em uma empresa</strong>
            <span>Usar convite ou código para acessar a conta de uma empresa já existente.</span>
          </span>
          <ArrowRight class="option-arrow" :size="18" />
        </button>

        <button class="option-row" @click="goToCreate">
          <span class="option-icon">
            <Building2 :size="20" />
          </span>
          <span class="option-copy">
            <strong>Criar nova empresa</strong>
            <span>Começar do zero e configurar sua empresa dentro do Ledger Louis.</span>
          </span>
          <ArrowRight class="option-arrow" :size="18" />
        </button>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { KeyRound, Building2, ArrowRight } from 'lucide-vue-next';
import { useCompanyStore } from '@/stores/CompanyStore';

const router = useRouter();
const companyStore = useCompanyStore();

const goToJoin = () => {
  router.push({ name: 'companyJoin' });
};

const goToCreate = () => {
  router.push({ name: 'companyCreate' });
};

onMounted(() => {
  if (companyStore.company.hasCompany) {
    router.replace({ name: 'companySettings' });
  }
});
</script>

<style scoped>
.onboarding-page {
  min-height: calc(100vh - 65px);
  display: flex;
  justify-content: center;
  padding: 64px 20px;
  background: var(--color-bg);
}

.onboarding-container {
  width: 100%;
  max-width: 560px;
}

.kicker {
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-primary);
  margin-bottom: 14px;
}

h1 {
  font-family: var(--font-display);
  font-size: clamp(1.65rem, 4vw, 2.25rem);
  font-weight: 800;
  line-height: 1.2;
  color: var(--color-text);
  margin-bottom: 14px;
  text-wrap: balance;
}

.accent-text {
  background: var(--color-success-gradient);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.description {
  color: var(--color-text-secondary);
  font-size: 16px;
  line-height: 1.7;
  max-width: 440px;
}

.option-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 36px;
}

.option-row {
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 20px 22px;
  border-radius: 14px;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  cursor: pointer;
  text-align: left;
  transition: border-color 0.2s ease, background 0.2s ease;
}

.option-row:hover {
  border-color: var(--color-primary);
  background: var(--color-surface-alt);
}

.option-icon {
  flex-shrink: 0;
  width: 42px;
  height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: var(--color-primary-glow);
  color: var(--color-primary);
}

.option-copy {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.option-copy strong {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 700;
  color: var(--color-text);
}

.option-copy span {
  font-size: 14px;
  line-height: 1.5;
  color: var(--color-text-secondary);
}

.option-arrow {
  flex-shrink: 0;
  color: var(--color-text-tertiary);
  transition: transform 0.2s ease, color 0.2s ease;
}

.option-row:hover .option-arrow {
  transform: translateX(3px);
  color: var(--color-primary);
}

/* Responsividade */
@media (max-width: 640px) {
  .onboarding-page {
    padding: 40px 16px;
  }

  .option-row {
    padding: 16px 18px;
    gap: 14px;
  }

  .option-copy span {
    font-size: 13px;
  }
}
</style>
