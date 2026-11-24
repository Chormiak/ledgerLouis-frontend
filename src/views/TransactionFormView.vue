<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ArrowDownRight, ArrowUpRight, CalendarDays, Type } from 'lucide-vue-next';
import BaseButton from '@/components/ui/BaseButton.vue';
import BaseInput from '@/components/ui/BaseInput.vue';
import TagPicker from '@/components/forms/TagPicker.vue';
import { useTransactionStore } from '@/stores/transactionStore';
import { useTagStore } from '@/stores/tagStore';
import { useToast } from '@/composables/useToast';
import { apiErrorMessage } from '@/utils/apiError';
import { todayIso } from '@/utils/format';

const route = useRoute();
const router = useRouter();
const transactionStore = useTransactionStore();
const tagStore = useTagStore();
const toast = useToast();

// Entrada e saída usam a mesma tela; o tipo vem do meta da rota.
const entryType = computed(() => route.meta.entryType ?? 'debit');
const isIncome = computed(() => entryType.value === 'credit');

const copy = computed(() =>
  isIncome.value
    ? { title: 'Nova entrada', placeholder: 'Ex: Venda, serviço prestado...', success: 'Entrada registrada!' }
    : { title: 'Nova saída', placeholder: 'Ex: Conta de luz, fornecedor...', success: 'Saída registrada!' },
);

const createEmptyForm = () => ({ amount: '', description: '', date: todayIso() });

const form = reactive(createEmptyForm());
const selectedTagIds = ref<string[]>([]);
const errors = reactive({ description: '', amount: '' });
const saving = ref(false);

watch(entryType, () => {
  errors.description = '';
  errors.amount = '';
});

const validate = () => {
  errors.description = form.description.trim() ? '' : 'Informe uma descrição.';
  const amount = Number(form.amount);
  errors.amount = amount > 0 ? '' : 'Digite um valor maior que zero.';
  return !errors.description && !errors.amount && !!form.date;
};

const handleSubmit = async () => {
  if (!validate()) return;

  saving.value = true;
  try {
    const created = await transactionStore.createTransaction({
      amount: Number(form.amount),
      description: form.description.trim(),
      entryType: entryType.value,
      date: form.date,
    });

    if (selectedTagIds.value.length > 0) {
      await Promise.all(selectedTagIds.value.map((tagId) => tagStore.attachTag(created.id, tagId)));
    }

    toast.success(copy.value.success);
    router.push({ name: 'reports' });
  } catch (error) {
    toast.error(apiErrorMessage(error, 'Não foi possível registrar. Tente novamente.'));
  } finally {
    saving.value = false;
  }
};
</script>

<template>
  <div class="page entry-page" :data-type="entryType">
    <div class="page-shell page-shell--entry">
      <div class="card form-card entry-card" :data-type="entryType">
        <header class="form-head">
          <span class="icon-tile" :class="{ 'icon-tile--danger': !isIncome }">
            <ArrowUpRight v-if="isIncome" :size="20" />
            <ArrowDownRight v-else :size="20" />
          </span>
          <div>
            <h1>{{ copy.title }}</h1>
            <p class="form-lead">Informe o valor, a data e, se quiser, as tags.</p>
          </div>
        </header>

        <nav class="segmented segmented--block segmented--slide" :style="{ '--idx': isIncome ? 1 : 0 }" aria-label="Tipo de lançamento">
          <span class="segmented-thumb" aria-hidden="true" />
          <RouterLink
            :to="{ name: 'addExpense' }"
            replace
            class="segmented-item"
            data-tone="expense"
            :class="{ 'is-active': !isIncome }"
          >
            Saída
          </RouterLink>
          <RouterLink
            :to="{ name: 'addIncome' }"
            replace
            class="segmented-item"
            data-tone="income"
            :class="{ 'is-active': isIncome }"
          >
            Entrada
          </RouterLink>
        </nav>

        <form class="form form--lg" novalidate @submit.prevent="handleSubmit">
          <div class="amount-field" :class="{ 'is-invalid': errors.amount }">
            <label for="amount" class="field-label">Valor</label>
            <div class="amount-input">
              <span aria-hidden="true">R$</span>
              <input
                id="amount"
                v-model="form.amount"
                type="number"
                inputmode="decimal"
                step="0.01"
                min="0"
                placeholder="0,00"
                autofocus
              />
            </div>
            <span v-if="errors.amount" class="field-error">{{ errors.amount }}</span>
          </div>

          <BaseInput
            v-model="form.description"
            label="Descrição"
            :icon="Type"
            :placeholder="copy.placeholder"
            :error="errors.description"
          />

          <BaseInput v-model="form.date" label="Data" :icon="CalendarDays" type="date" required />

          <TagPicker v-model="selectedTagIds" />

          <div class="form-actions">
            <BaseButton variant="secondary" @click="router.back()">Cancelar</BaseButton>
            <BaseButton type="submit" :variant="isIncome ? 'primary' : 'danger'" :loading="saving">
              Salvar {{ isIncome ? 'entrada' : 'saída' }}
            </BaseButton>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.amount-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

/* Valor com a mesma linha dos outros campos; a linha de foco cresce do centro, na cor do tipo. */
.amount-input {
  display: flex;
  align-items: baseline;
  gap: var(--space-2);
  padding: 2px 2px 0;
  border-bottom: 1px solid var(--color-border-strong);
  background-image: linear-gradient(var(--tone), var(--tone));
  background-repeat: no-repeat;
  background-position: 50% 100%;
  background-size: 0% 2px;
  background-origin: border-box;
  transition: background-size 460ms var(--ease-out);
}

.amount-input:focus-within {
  background-size: 100% 2px;
  border-bottom-color: transparent;
}

.amount-field.is-invalid .amount-input {
  background-image: linear-gradient(var(--color-danger), var(--color-danger));
  background-size: 100% 2px;
  border-bottom-color: transparent;
}

.amount-input span {
  font-family: var(--font-display);
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-text-subtle);
}

.amount-input input {
  flex: 1;
  min-width: 0;
  border: none;
  background: transparent;
  outline: none;
  font-family: var(--font-mono);
  font-size: 1.625rem;
  font-weight: 400;
  letter-spacing: -0.04em;
  font-variant-numeric: tabular-nums;
  color: var(--tone-strong);
  caret-color: var(--tone);
}

.amount-input input::-webkit-outer-spin-button,
.amount-input input::-webkit-inner-spin-button {
  appearance: none;
  margin: 0;
}

.amount-input input[type='number'] {
  appearance: textfield;
}

.amount-input input::placeholder {
  color: var(--color-border-strong);
}

.form-actions {
  display: grid;
  grid-template-columns: 1fr 1.6fr;
  gap: var(--space-3);
  padding-top: var(--space-1);
}

/* Brilho no topo da tela, na cor do tipo: duas camadas que trocam de opacidade. */
.entry-page {
  position: relative;
}

.entry-page::before,
.entry-page::after {
  content: '';
  position: absolute;
  inset: 0 0 auto;
  height: 520px;
  pointer-events: none;
  transition: opacity 700ms var(--ease-out);
}

.entry-page::before {
  background: radial-gradient(55% 60% at 50% 0%, rgba(52, 181, 133, 0.15), transparent 70%);
}

.entry-page::after {
  background: radial-gradient(55% 60% at 50% 0%, rgba(238, 107, 120, 0.14), transparent 70%);
  opacity: 0;
}

.entry-page[data-type='debit']::before {
  opacity: 0;
}

.entry-page[data-type='debit']::after {
  opacity: 1;
}

.entry-page .page-shell {
  position: relative;
  z-index: 1;
}
</style>
