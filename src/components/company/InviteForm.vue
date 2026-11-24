<script setup lang="ts">
import { reactive, ref } from 'vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import BaseInput from '@/components/ui/BaseInput.vue';
import type { CompanyRole } from '@/services/companyService';
import { ROLE_OPTIONS } from './roles';

const props = defineProps<{ disabled?: boolean; loading: boolean; error: string }>();
const emit = defineEmits<{ submit: [payload: { email: string; role: CompanyRole }] }>();

const form = reactive<{ email: string; role: CompanyRole }>({ email: '', role: 'viewer' });
const localError = ref('');

const onSubmit = () => {
  const email = form.email.trim();
  localError.value = email ? '' : 'Informe o e-mail de quem você quer convidar.';
  if (localError.value) return;
  emit('submit', { email, role: form.role });
};

/** O pai chama depois de um convite enviado com sucesso. */
const reset = () => {
  form.email = '';
  form.role = 'viewer';
};
defineExpose({ reset });
</script>

<template>
  <form class="invite" @submit.prevent="onSubmit">
    <h3>Convidar pessoa</h3>
    <div class="row">
      <BaseInput
        id="memberEmail"
        v-model="form.email"
        type="email"
        placeholder="email@dominio.com"
        autocomplete="off"
        aria-label="E-mail de quem será convidado"
        :error="localError || props.error"
        class="email"
      />
      <select v-model="form.role" class="input role" aria-label="Função">
        <option v-for="option in ROLE_OPTIONS" :key="option.value" :value="option.value">{{ option.label }}</option>
      </select>
      <BaseButton type="submit" :loading="loading" :disabled="disabled">Convidar</BaseButton>
    </div>
  </form>
</template>

<style scoped>
.invite {
  margin-top: var(--space-5);
  padding-top: var(--space-5);
  border-top: 1px solid var(--color-border);
}

h3 {
  margin-bottom: var(--space-3);
  font-size: var(--text-sm);
  font-weight: 500;
}

.row {
  display: grid;
  gap: var(--space-3);
  align-items: start;
}

@media (min-width: 640px) {
  .row {
    grid-template-columns: minmax(0, 1fr) 150px auto;
  }
}
</style>
