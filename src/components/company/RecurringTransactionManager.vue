<script setup lang="ts">
import { onMounted, reactive, ref, watch, onUnmounted, computed } from 'vue';
import { Plus, Trash2, Play, Pause, PlayCircle } from 'lucide-vue-next';
import { useRecurringTransactionStore } from '@/stores/recurringTransactionStore';
import type { RecurringEntryType, RecurringFrequency } from '@/services/recurringTransactionService';

const store = useRecurringTransactionStore();

const showForm = ref(false);
const isLoading = ref(false);
const runningId = ref<string | null>(null);
const message = reactive({ status: '', text: '', show: false });

const formData = reactive({
  description: '',
  entryType: 'debit' as RecurringEntryType,
  unitValue: 0,
  quantity: 1,
  frequency: 'monthly' as RecurringFrequency,
  startDate: new Date().toISOString().slice(0, 10),
  endDate: '',
});

const frequencyLabels: Record<RecurringFrequency, string> = {
  weekly: 'Semanal',
  monthly: 'Mensal',
  yearly: 'Anual',
};

const statusLabels: Record<string, string> = {
  active: 'Ativo',
  paused: 'Pausado',
  finished: 'Finalizado',
};

const sortedItems = computed(() =>
  [...store.items].sort((a, b) => a.nextRunDate.localeCompare(b.nextRunDate)),
);

const totalValue = () => formData.unitValue * formData.quantity;

const formatDate = (value: string | null) => {
  if (!value) return '—';
  const [year, month, day] = value.split('-');
  return `${day}/${month}/${year}`;
};

const formatCurrency = (value: number) =>
  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);

const resetForm = () => {
  formData.description = '';
  formData.entryType = 'debit';
  formData.unitValue = 0;
  formData.quantity = 1;
  formData.frequency = 'monthly';
  formData.startDate = new Date().toISOString().slice(0, 10);
  formData.endDate = '';
  showForm.value = false;
};

const handleCloseForm = () => {
  resetForm();
  message.show = false;
};

watch(showForm, (isOpen) => {
  document.body.style.overflow = isOpen ? 'hidden' : '';
});

onUnmounted(() => {
  document.body.style.overflow = '';
});

const notify = (status: 'success' | 'error', text: string) => {
  message.status = status;
  message.text = text;
  message.show = true;
  setTimeout(() => {
    message.show = false;
  }, 2500);
};

const handleCreate = async () => {
  if (!formData.description.trim()) {
    notify('error', 'Digite a descrição do lançamento');
    return;
  }

  if (formData.unitValue <= 0) {
    notify('error', 'Digite um valor maior que zero');
    return;
  }

  if (formData.quantity < 1) {
    notify('error', 'Quantidade deve ser maior que zero');
    return;
  }

  try {
    isLoading.value = true;

    await store.createRecurringTransaction({
      description: formData.description.trim(),
      amount: totalValue(),
      entryType: formData.entryType,
      frequency: formData.frequency,
      startDate: formData.startDate,
      endDate: formData.endDate || undefined,
    });

    notify('success', 'Lançamento recorrente criado com sucesso!');
    resetForm();
  } catch (error: any) {
    notify('error', error?.response?.data?.message || 'Erro ao criar lançamento recorrente');
  } finally {
    isLoading.value = false;
  }
};

const handleDelete = async (id: string) => {
  try {
    await store.deleteRecurringTransaction(id);
    notify('success', 'Lançamento recorrente removido!');
  } catch {
    notify('error', 'Erro ao remover lançamento recorrente');
  }
};

const handleToggleStatus = async (id: string, currentStatus: string) => {
  try {
    await store.updateRecurringTransaction(id, {
      status: currentStatus === 'active' ? 'paused' : 'active',
    });
  } catch {
    notify('error', 'Erro ao atualizar status');
  }
};

const handleRunNow = async (id: string) => {
  runningId.value = id;
  try {
    const result = await store.runNow(id);
    notify(
      'success',
      result.created > 0 ? 'Lançamento gerado com sucesso!' : 'Nada vencido para lançar ainda.',
    );
  } catch {
    notify('error', 'Erro ao lançar agora');
  } finally {
    runningId.value = null;
  }
};

onMounted(() => {
  store.fetchRecurringTransactions();
});
</script>

<script lang="ts">
export default {
  name: 'RecurringTransactionManager',
};
</script>

<template>
  <div class="recurring-manager">
    <div class="manager-header">
      <div>
        <h3>Lançamentos Recorrentes</h3>
        <p class="manager-hint">Entradas e saídas que se repetem — a cobrança é lançada automaticamente quando a data chegar.</p>
      </div>
      <button class="btn-add" @click="showForm = true">
        <Plus :size="18" />
        Novo lançamento
      </button>
    </div>

    <div v-if="message.show" class="message" :class="message.status">
      {{ message.text }}
    </div>

    <div class="items-list" v-if="sortedItems.length > 0">
      <div v-for="item in sortedItems" :key="item.id" class="item-card">
        <div class="item-header">
          <div class="item-title">
            <span class="entry-dot" :class="item.entryType"></span>
            <h5>{{ item.description || 'Lançamento recorrente' }}</h5>
            <span class="status-badge" :class="item.status">{{ statusLabels[item.status] }}</span>
          </div>
          <div class="item-value">
            <span class="amount" :class="item.entryType">
              {{ item.entryType === 'credit' ? '+' : '-' }} {{ formatCurrency(item.amount) }}
            </span>
          </div>
        </div>

        <div class="item-details">
          <div class="detail-item">
            <span class="detail-label">Frequência</span>
            <span class="detail-value">{{ frequencyLabels[item.frequency] }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Próximo lançamento</span>
            <span class="detail-value">{{ formatDate(item.nextRunDate) }}</span>
          </div>
          <div v-if="item.lastRunDate" class="detail-item">
            <span class="detail-label">Último lançamento</span>
            <span class="detail-value">{{ formatDate(item.lastRunDate) }}</span>
          </div>
          <div v-if="item.endDate" class="detail-item">
            <span class="detail-label">Termina em</span>
            <span class="detail-value">{{ formatDate(item.endDate) }}</span>
          </div>
        </div>

        <div class="item-actions">
          <button
            v-if="item.status !== 'finished'"
            class="btn-icon-text"
            @click="handleRunNow(item.id)"
            :disabled="runningId === item.id"
          >
            <PlayCircle :size="15" />
            {{ runningId === item.id ? 'Lançando...' : 'Lançar agora' }}
          </button>

          <button
            v-if="item.status !== 'finished'"
            class="btn-icon-text"
            @click="handleToggleStatus(item.id, item.status)"
          >
            <Pause v-if="item.status === 'active'" :size="15" />
            <Play v-else :size="15" />
            {{ item.status === 'active' ? 'Pausar' : 'Retomar' }}
          </button>

          <button class="btn-delete" @click="handleDelete(item.id)" title="Remover">
            <Trash2 :size="16" />
          </button>
        </div>
      </div>
    </div>

    <div v-else class="empty-state">
      Nenhum lançamento recorrente criado ainda.
    </div>

    <div v-if="showForm" class="modal-overlay" @click.self="handleCloseForm">
      <div class="modal-dialog">
        <div class="modal-header">
          <h4>Novo lançamento recorrente</h4>
          <button class="btn-close" @click="handleCloseForm" aria-label="Fechar">×</button>
        </div>

        <div class="modal-body">
          <div class="entry-toggle">
            <button
              type="button"
              class="entry-toggle-btn"
              :class="{ active: formData.entryType === 'debit' }"
              @click="formData.entryType = 'debit'"
            >
              Saída
            </button>
            <button
              type="button"
              class="entry-toggle-btn"
              :class="{ active: formData.entryType === 'credit' }"
              @click="formData.entryType = 'credit'"
            >
              Entrada
            </button>
          </div>

          <div class="form-group">
            <label>Descrição *</label>
            <input
              v-model="formData.description"
              type="text"
              placeholder="Ex: Aluguel, Salário fixo..."
              class="input"
            />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Valor unitário (R$) *</label>
              <input
                v-model.number="formData.unitValue"
                type="number"
                step="0.01"
                min="0"
                placeholder="1500.00"
                class="input"
              />
            </div>

            <div class="form-group">
              <label>Quantidade *</label>
              <input
                v-model.number="formData.quantity"
                type="number"
                step="1"
                min="1"
                placeholder="1"
                class="input"
              />
            </div>
          </div>

          <div class="form-group">
            <label>Frequência</label>
            <select v-model="formData.frequency" class="input">
              <option value="weekly">Semanal</option>
              <option value="monthly">Mensal</option>
              <option value="yearly">Anual</option>
            </select>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Data de início</label>
              <input v-model="formData.startDate" type="date" class="input" />
            </div>

            <div class="form-group">
              <label>Data de término (opcional)</label>
              <input v-model="formData.endDate" type="date" class="input" />
            </div>
          </div>

          <div class="total-preview">
            <span class="preview-label">Total por ocorrência</span>
            <span class="preview-value">{{ formatCurrency(totalValue()) }}</span>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-cancel" @click="handleCloseForm">Cancelar</button>
          <button class="btn-success" @click="handleCreate" :disabled="isLoading">
            {{ isLoading ? 'Salvando...' : 'Confirmar' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.recurring-manager {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  padding: 24px;
}

.manager-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--color-border);
}

.manager-header h3 {
  margin: 0 0 6px;
  font-family: var(--font-display);
  font-size: 1.15rem;
  color: var(--color-text);
}

.manager-hint {
  color: var(--color-text-secondary);
  font-size: 0.85rem;
  max-width: 44ch;
}

.btn-add {
  flex-shrink: 0;
  background: var(--color-primary);
  color: var(--color-surface);
  border: none;
  padding: 10px 16px;
  border-radius: var(--radius-input);
  cursor: pointer;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
}

.message {
  padding: 12px 16px;
  border-radius: var(--radius-input);
  margin-bottom: 16px;
  font-weight: 600;
  font-size: 0.9rem;
}

.message.success {
  background: var(--color-primary-glow);
  color: var(--color-primary);
}

.message.error {
  background: var(--color-danger-soft);
  color: var(--color-danger);
}

.items-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.item-card {
  background: var(--color-surface-soft);
  border: 1px solid var(--color-border);
  border-radius: 14px;
  padding: 16px;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--color-border);
}

.item-title {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.entry-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  flex-shrink: 0;
}

.entry-dot.credit {
  background: var(--color-primary);
}

.entry-dot.debit {
  background: var(--color-danger);
}

.item-title h5 {
  margin: 0;
  color: var(--color-text);
  font-size: 0.95rem;
}

.status-badge {
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.status-badge.active {
  background: var(--color-primary-glow);
  color: var(--color-primary);
}

.status-badge.paused {
  background: var(--color-surface-alt);
  color: var(--color-text-secondary);
}

.status-badge.finished {
  background: var(--color-border);
  color: var(--color-text-tertiary);
}

.amount {
  font-weight: 700;
  font-size: 1.05rem;
}

.amount.credit {
  color: var(--color-primary);
}

.amount.debit {
  color: var(--color-danger);
}

.item-details {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-bottom: 14px;
  font-size: 0.85rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.detail-label {
  font-weight: 600;
  color: var(--color-text-tertiary);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.detail-value {
  color: var(--color-text);
}

.item-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.btn-icon-text {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 12px;
  border-radius: var(--radius-input);
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-text-secondary);
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-icon-text:hover:not(:disabled) {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.btn-icon-text:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-delete {
  margin-left: auto;
  background: transparent;
  color: var(--color-danger);
  border: 1px solid var(--color-border);
  padding: 7px;
  border-radius: var(--radius-input);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-delete:hover {
  border-color: var(--color-danger);
  background: var(--color-danger-soft);
}

.empty-state {
  text-align: center;
  padding: 32px;
  color: var(--color-text-secondary);
  border: 1px dashed var(--color-border);
  border-radius: 14px;
}

.entry-toggle {
  display: flex;
  gap: 4px;
  padding: 4px;
  border-radius: var(--radius-input);
  background: var(--color-surface-alt);
  border: 1px solid var(--color-border);
  margin-bottom: 18px;
}

.entry-toggle-btn {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: calc(var(--radius-input) - 4px);
  background: transparent;
  font-weight: 700;
  font-size: 14px;
  color: var(--color-text-secondary);
  cursor: pointer;
}

.entry-toggle-btn.active {
  background: var(--color-surface);
  color: var(--color-primary);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--color-text-secondary);
}

.input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-input);
  font-size: 0.95rem;
  font-family: inherit;
  background: var(--color-surface);
  color: var(--color-text);
}

.input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.total-preview {
  background: var(--color-surface-soft);
  padding: 12px 16px;
  border-radius: var(--radius-input);
  border: 1px solid var(--color-primary);
  margin: 4px 0 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preview-label {
  font-weight: 600;
  color: var(--color-text);
  font-size: 0.9rem;
}

.preview-value {
  font-weight: 800;
  font-size: 1.1rem;
  color: var(--color-primary);
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 99999;
  padding: 20px;
  overflow-y: auto;
}

.modal-dialog {
  display: flex;
  flex-direction: column;
  width: min(100%, 720px);
  max-width: 720px;
  max-height: calc(100vh - 40px);
  background: var(--color-surface);
  border-radius: 16px;
  overflow: hidden;
}

.modal-body {
  padding: 20px 24px;
  overflow-y: auto;
  flex: 1 1 auto;
  min-height: 0;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: var(--color-surface-soft);
  border-bottom: 1px solid var(--color-border);
}

.modal-header h4 {
  margin: 0;
  font-size: 1.1rem;
  color: var(--color-text);
}

.btn-close {
  background: transparent;
  border: none;
  font-size: 1.4rem;
  cursor: pointer;
  color: var(--color-text-secondary);
  padding: 4px;
}

.modal-footer {
  position: sticky;
  bottom: 0;
  display: flex;
  gap: 12px;
  padding: 16px 24px 24px;
  background: var(--color-surface-soft);
  justify-content: flex-end;
  flex-shrink: 0;
}

.btn-success,
.btn-cancel {
  min-width: 120px;
  padding: 12px;
  border-radius: var(--radius-input);
  font-weight: 700;
  cursor: pointer;
}

.btn-success {
  background: var(--color-primary);
  color: var(--color-surface);
  border: none;
}

.btn-success:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-cancel {
  background: transparent;
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}

@media (max-width: 768px) {
  .modal-header,
  .modal-body,
  .modal-footer {
    padding-left: 16px;
    padding-right: 16px;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .total-preview {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }
}
</style>
