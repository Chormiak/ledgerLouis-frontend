<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue';
import BaseModal from '@/components/ui/BaseModal.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import BaseInput from '@/components/ui/BaseInput.vue';
import AnimatedNumber from '@/components/ui/AnimatedNumber.vue';
import { CalendarDays, Hash, Type, Wallet } from 'lucide-vue-next';
import { useRecurringTransactionStore } from '@/stores/recurringTransactionStore';
import type { RecurringEntryType, RecurringFrequency } from '@/services/recurringTransactionService';
import { useToast } from '@/composables/useToast';
import { apiErrorMessage } from '@/utils/apiError';
import { formatCurrency, todayIso } from '@/utils/format';

const open = defineModel<boolean>('open', { default: false });

const store = useRecurringTransactionStore();
const toast = useToast();

const createEmptyForm = () => ({
  description: '',
  entryType: 'debit' as RecurringEntryType,
  unitValue: '',
  quantity: '1',
  frequency: 'monthly' as RecurringFrequency,
  startDate: todayIso(),
  endDate: '',
});

const form = reactive(createEmptyForm());
const error = ref('');
const saving = ref(false);

const total = computed(() => (Number(form.unitValue) || 0) * (Number(form.quantity) || 0));

watch(open, (isOpen) => {
  if (isOpen) {
    Object.assign(form, createEmptyForm());
    error.value = '';
  }
});

const validate = () => {
  if (!form.description.trim()) return 'Digite a descrição do lançamento.';
  if (!(Number(form.unitValue) > 0)) return 'Digite um valor maior que zero.';
  if (!(Number(form.quantity) >= 1)) return 'A quantidade deve ser pelo menos 1.';
  if (form.endDate && form.endDate < form.startDate) return 'A data de término deve ser depois do início.';
  return '';
};

const handleSubmit = async () => {
  error.value = validate();
  if (error.value) return;

  saving.value = true;
  try {
    await store.createRecurringTransaction({
      description: form.description.trim(),
      amount: total.value,
      entryType: form.entryType,
      frequency: form.frequency,
      startDate: form.startDate,
      endDate: form.endDate || undefined,
    });
    toast.success('Lançamento recorrente criado!');
    open.value = false;
  } catch (err) {
    error.value = apiErrorMessage(err, 'Erro ao criar lançamento recorrente.');
  } finally {
    saving.value = false;
  }
};
</script>

<template>
  <BaseModal v-model:open="open" title="Novo lançamento recorrente" size="sm">
    <form id="recurring-form" class="form form--lg" :data-type="form.entryType" @submit.prevent="handleSubmit">
      <p class="form-lead">Lançado sozinho na data certa: aluguel, salários, assinaturas.</p>

      <div class="segmented segmented--block segmented--slide" :style="{ '--idx': form.entryType === 'credit' ? 1 : 0 }" role="radiogroup" aria-label="Tipo">
        <span class="segmented-thumb" aria-hidden="true" />
        <button
          type="button"
          role="radio"
          class="segmented-item"
          data-tone="expense"
          :aria-checked="form.entryType === 'debit'"
          :class="{ 'is-active': form.entryType === 'debit' }"
          @click="form.entryType = 'debit'"
        >
          Saída
        </button>
        <button
          type="button"
          role="radio"
          class="segmented-item"
          data-tone="income"
          :aria-checked="form.entryType === 'credit'"
          :class="{ 'is-active': form.entryType === 'credit' }"
          @click="form.entryType = 'credit'"
        >
          Entrada
        </button>
      </div>

      <BaseInput v-model="form.description" label="Descrição" :icon="Type" placeholder="Ex: Aluguel, salários, assinatura..." />

      <div class="field-grid">
        <BaseInput
          v-model="form.unitValue"
          label="Valor unitário (R$)"
          :icon="Wallet"
          type="number"
          step="0.01"
          min="0"
          placeholder="0,00"
          inputmode="decimal"
        />
        <BaseInput
          v-model="form.quantity"
          label="Quantidade"
          :icon="Hash"
          type="number"
          step="1"
          min="1"
          hint="Ex: 14 funcionários × salário"
        />
      </div>

      <div class="field">
        <label for="recurring-frequency" class="field-label">Frequência</label>
        <select id="recurring-frequency" v-model="form.frequency" class="input">
          <option value="weekly">Semanal</option>
          <option value="monthly">Mensal</option>
          <option value="yearly">Anual</option>
        </select>
      </div>

      <div class="field-grid">
        <BaseInput v-model="form.startDate" label="Início" :icon="CalendarDays" type="date" />
        <BaseInput v-model="form.endDate" label="Término (opcional)" :icon="CalendarDays" type="date" />
      </div>

      <div class="total-preview">
        <span>Total por ocorrência</span>
        <strong class="tabular"><AnimatedNumber :value="total" :format="formatCurrency" :duration="380" /></strong>
      </div>

      <p v-if="error" class="alert alert--error" role="alert">{{ error }}</p>
    </form>

    <template #footer>
      <BaseButton variant="secondary" @click="open = false">Cancelar</BaseButton>
      <BaseButton type="submit" form="recurring-form" :loading="saving">Criar lançamento</BaseButton>
    </template>
  </BaseModal>
</template>

<style scoped>
/* Cor e valor acompanham o tipo escolhido (--tone vem do .form--lg). */
.total-preview {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  background: color-mix(in srgb, var(--tone) 10%, transparent);
  color: var(--tone-strong);
  font-size: var(--text-sm);
  font-weight: 600;
}

.total-preview strong {
  font-family: var(--font-display);
  font-size: var(--text-lg);
  letter-spacing: -0.03em;
}
</style>
