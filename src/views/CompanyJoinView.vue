<template>
  <main class="company-join-page">
    <section class="company-join-container">
      <header class="header-block">
        <p class="kicker">Entrar em empresa</p>
        <h1>Conecte-se a uma <span class="accent-text">empresa</span> existente</h1>
        <p class="description">
          Digite o código de acesso para entrar em uma empresa.
        </p>
      </header>

      <form class="company-form" @submit.prevent="handleJoin">
        <div class="code-row" :class="{ 'code-row--error': errors.companyCode }">
          <label for="companyCode" class="field-label">Código de acesso</label>
          <BaseInput
            id="companyCode"
            type="text"
            placeholder="• • • • •"
            v-model="companyCode"
            :error="errors.companyCode"
            required
          />
        </div>

        <div class="form-actions">
          <button type="button" class="ghost-button" @click="goBack">Voltar</button>

          <PrimaryButton type="submit" :loading="loading">
            <span class="btn-label">
              Entrar
              <svg width="18" height="18" viewBox="0 0 20 20" fill="none" aria-hidden="true">
                <path d="M4.16666 10H15.8333M15.8333 10L10 4.16666M15.8333 10L10 15.8333" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </span>
          </PrimaryButton>
        </div>
      </form>
    </section>
  </main>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useCompanyStore } from '@/stores/CompanyStore';
import BaseInput from '@/components/ui/BaseInput.vue';
import PrimaryButton from '@/components/ui/PrimaryButton.vue';

const router = useRouter();
const companyStore = useCompanyStore();
const companyCode = ref('');
const loading = ref(false);

const errors = reactive({
  companyCode: false,
});

const goBack = () => {
  router.back();
};

const handleJoin = () => {
  // Limpar erros anteriores
  errors.companyCode = false;

  // Validar campo obrigatório
  if (!companyCode.value.trim()) {
    errors.companyCode = true;
    return;
  }

  loading.value = true;
  const joinedName = `Empresa ${companyCode.value}`;
  companyStore.setCompanyData({
    name: joinedName,
    cnpj: '',
    address: 'Endereço padrão da empresa',
    email: 'contato@empresa.com',
    website: 'https://www.empresa.com',
    phone: '(00) 00000-0000',
    owner: companyCode.value,
    hasCompany: true,
  });
  router.replace({ name: 'companySettings' });
  loading.value = false;
};
</script>

<style scoped>
.company-join-page {
  min-height: calc(100vh - 65px);
  display: flex;
  justify-content: center;
  padding: 64px 20px;
  background: var(--color-bg);
}

.company-join-container {
  width: 100%;
  max-width: 480px;
}

.header-block {
  margin-bottom: 8px;
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
  font-size: clamp(1.5rem, 4vw, 2rem);
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
}

.code-row {
  margin-top: 40px;
  padding-bottom: 18px;
  border-bottom: 1.5px solid var(--color-border);
  transition: border-color 0.2s ease;
}

.code-row:focus-within {
  border-bottom-color: var(--color-primary);
}

.code-row--error {
  border-bottom-color: var(--color-danger);
}

.field-label {
  display: block;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--color-text-secondary);
  margin-bottom: 18px;
}

.code-row :deep(.input-group) {
  margin-bottom: 0;
}

.code-row :deep(.custom-input) {
  border: none;
  border-radius: 0;
  background: transparent;
  padding: 4px 0;
  text-align: center;
  font-family: var(--font-display);
  font-size: 2rem;
  font-weight: 700;
  letter-spacing: 0.4em;
  text-indent: 0.4em;
}

.code-row :deep(.custom-input:focus) {
  box-shadow: none;
  background: transparent;
}

.form-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  margin-top: 36px;
}

.btn-label {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.ghost-button {
  padding: 15px 24px;
  border-radius: var(--radius-input);
  font-family: var(--font-body);
  font-weight: 700;
  font-size: 15px;
  cursor: pointer;
  border: 1.5px solid var(--color-text-tertiary);
  background: transparent;
  color: var(--color-text-secondary);
  transition: border-color 0.2s ease, color 0.2s ease, background 0.2s ease;
}

.ghost-button:hover {
  border-color: var(--color-text-secondary);
  color: var(--color-text);
  background: var(--color-surface-alt);
}

/* Responsividade */
@media (max-width: 640px) {
  .company-join-page {
    padding: 40px 16px;
  }

  .code-row :deep(.custom-input) {
    font-size: 1.5rem;
    letter-spacing: 0.3em;
  }

  .form-actions {
    flex-direction: column;
  }
}
</style>
