<template>
  <main class="company-create-page">
    <section class="company-create-container">
      <header class="header-block">
        <p class="kicker">Cadastro de empresa</p>
        <h1>Registre sua <span class="accent-text">empresa</span> no Ledger Louis</h1>
        <p class="description">
          Informe os dados principais para começar a organizar as finanças do seu negócio.
        </p>
      </header>

      <form class="company-form" @submit.prevent="handleSubmit">
        <div class="field-list">
          <div class="field-row" :class="{ 'field-row--error': errors.name }">
            <label for="name" class="field-label">Nome da empresa</label>
            <BaseInput
              id="name"
              type="text"
              placeholder="Ex: Studio Louis"
              v-model="form.name"
              :error="errors.name"
              required
            />
          </div>

          <div class="field-row" :class="{ 'field-row--error': errors.cnpj }">
            <label for="cnpj" class="field-label">CNPJ</label>
            <BaseInput
              id="cnpj"
              type="text"
              placeholder="00.000.000/0000-00"
              v-model="form.cnpj"
              :error="errors.cnpj"
              required
            />
          </div>

          <div class="field-row" :class="{ 'field-row--error': errors.email }">
            <label for="email" class="field-label">Email</label>
            <BaseInput
              id="email"
              type="email"
              placeholder="contato@empresa.com"
              v-model="form.email"
              :error="errors.email"
              required
            />
          </div>

          <div class="field-row" :class="{ 'field-row--error': errors.phone }">
            <label for="phone" class="field-label">Telefone</label>
            <BaseInput
              id="phone"
              type="tel"
              placeholder="(11) 99999-9999"
              v-model="form.phone"
              :error="errors.phone"
              required
            />
          </div>
        </div>

        <div class="form-actions">
          <button type="button" class="ghost-button" @click="goBack">Voltar</button>

          <PrimaryButton type="submit" :loading="loading">
            <span class="btn-label">
              Criar empresa
              <svg width="18" height="18" viewBox="0 0 20 20" fill="none" aria-hidden="true">
                <path d="M4.16666 10H15.8333M15.8333 10L10 4.16666M15.8333 10L10 15.8333" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </span>
          </PrimaryButton>
        </div>

        <p v-if="submitError" class="error-message">{{ submitError }}</p>
      </form>
    </section>
  </main>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useCompanyStore } from '@/stores/CompanyStore';
import BaseInput from '@/components/ui/BaseInput.vue';
import PrimaryButton from '@/components/ui/PrimaryButton.vue';
import CompanyService from '@/services/companyService';

const router = useRouter();
const companyStore = useCompanyStore();
const companyService = new CompanyService();
const loading = ref(false);
const submitError = ref('');

const form = reactive({
  name: '',
  cnpj: '',
  email: '',
  phone: '',
});

const errors = reactive({
  name: false,
  cnpj: false,
  email: false,
  phone: false,
});

const goBack = () => {
  router.back();
};

const handleSubmit = async () => {
  submitError.value = '';
  errors.name = false;
  errors.cnpj = false;
  errors.email = false;
  errors.phone = false;

  let isValid = true;
  if (!form.name.trim()) {
    errors.name = true;
    isValid = false;
  }
  if (!form.cnpj.trim()) {
    errors.cnpj = true;
    isValid = false;
  }
  if (!form.email.trim()) {
    errors.email = true;
    isValid = false;
  }
  if (!form.phone.trim()) {
    errors.phone = true;
    isValid = false;
  }

  if (!isValid) {
    return;
  }

  loading.value = true;
  try {
    const created = await companyService.createCompany(form.name.trim(), form.cnpj.trim(), {
      email: form.email.trim(),
      phone: form.phone.replace(/\D/g, ''),
    });

    companyStore.setCompanyData({
      id: created.id,
      name: created.name,
      cnpj: created.cnpj,
      email: form.email,
      phone: form.phone,
      owner: form.email,
      role: 'owner',
      hasCompany: true,
    });

    router.replace({ name: 'companySettings' });
  } catch (error: unknown) {
    const message =
      typeof error === 'object' && error !== null && 'response' in error
        ? (error as { response?: { data?: { message?: string; error?: string } } }).response?.data
            ?.message ||
          (error as { response?: { data?: { message?: string; error?: string } } }).response?.data
            ?.error
        : undefined;
    submitError.value = message || 'Erro ao criar empresa. Verifique o CNPJ e tente novamente.';
    console.error('Erro ao criar empresa:', error);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.company-create-page {
  min-height: calc(100vh - 65px);
  display: flex;
  justify-content: center;
  padding: 64px 20px;
  background: var(--color-bg);
}

.company-create-container {
  width: 100%;
  max-width: 620px;
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
  max-width: 480px;
}

.field-list {
  display: flex;
  flex-direction: column;
  margin-top: 36px;
}

.field-row {
  display: grid;
  grid-template-columns: 180px 1fr;
  align-items: center;
  gap: 24px;
  padding: 22px 0;
  border-bottom: 1px solid var(--color-border);
  transition: border-color 0.2s ease;
}

.field-row:first-child {
  border-top: 1px solid var(--color-border);
}

.field-row:focus-within {
  border-bottom-color: var(--color-primary);
}

.field-row:focus-within .field-label {
  color: var(--color-primary);
}

.field-row--error {
  border-bottom-color: var(--color-danger);
}

.field-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-secondary);
  transition: color 0.2s ease;
}

.field-row :deep(.input-group) {
  margin-bottom: 0;
}

.field-row :deep(.custom-input) {
  border: none;
  border-radius: 0;
  background: transparent;
  padding: 4px 0;
  font-size: 16px;
}

.field-row :deep(.custom-input:focus) {
  box-shadow: none;
  background: transparent;
}

.field-row--error :deep(.custom-input) {
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

.error-message {
  color: var(--color-danger);
  font-size: 0.9rem;
  margin: 0;
}

/* Responsividade */
@media (max-width: 640px) {
  .company-create-page {
    padding: 40px 16px;
  }

  .field-row {
    grid-template-columns: 1fr;
    gap: 8px;
    padding: 18px 0;
  }

  .form-actions {
    flex-direction: column;
  }
}
</style>
