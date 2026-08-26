<script setup lang="ts">
import { reactive } from 'vue';
import { useTransactionStore } from '@/stores/transactionStore';
import { useRouter } from 'vue-router';

const router = useRouter();
const transactionStore = useTransactionStore();

const expenseData = reactive({
  amount: '',
  description: '',
  date: new Date().toISOString().split('T')[0],
});

const response = reactive({
  status: '',
  message: '',
  show: false,
});

const handleAddExpense = async (e: Event) => {
  e.preventDefault();
  
  try {
    if (!expenseData.amount || !expenseData.description || !expenseData.date) {
      response.status = 'error';
      response.message = 'Preencha todos os campos obrigatórios';
      response.show = true;
      return;
    }

    const amount = parseFloat(expenseData.amount);
    if (isNaN(amount) || amount <= 0) {
      response.status = 'error';
      response.message = 'Digite um valor válido e maior que zero';
      response.show = true;
      return;
    }

    await transactionStore.createTransaction({
      amount,
      description: expenseData.description,
      entryType: 'debit',
      date: expenseData.date,
    });

    response.status = 'success';
    response.message = 'Despesa registrada com sucesso!';
    response.show = true;

    setTimeout(() => {
      router.push({ name: 'management' });
    }, 2000);
  } catch {
    response.status = 'error';
    response.message = 'Erro ao registrar despesa. Tente novamente.';
    response.show = true;
  }
};

const handleCancel = () => {
  router.push({ name: 'management' });
};
</script>

<template>
  <div class="container">
    <div class="card">
      <h2 class="title">Nova Saída</h2>
      
      <div v-if="response.show" class="response-popup" :class="response.status">
        <div class="popup-content">
          <div class="icon" :class="response.status">
            <span v-if="response.status === 'success'">✔</span>
            <span v-else>✖</span>
          </div>
          <h3 class="popup-title">{{ response.status === 'success' ? 'Sucesso!' : 'Erro!' }}</h3>
          <p class="popup-message">{{ response.message }}</p>
        </div>
      </div>

      <form @submit="handleAddExpense" class="form">
        
        <div class="form-group">
          <label class="form-label">Descrição</label>
          <input 
            v-model="expenseData.description"
            type="text" 
            placeholder="EX: Conta de água" 
            class="form-input"
          >
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Valor (R$)</label>
            <input 
              v-model="expenseData.amount"
              type="number" 
              step="0.01" 
              placeholder="0.00" 
              class="form-input"
            >
          </div>
          
          <div class="form-group">
            <label class="form-label">Data</label>
            <input 
              v-model="expenseData.date"
              type="date" 
              class="form-input"
            >
          </div>
        </div>
         
        
        <div class="form-actions">
          <button 
            type="button" 
            @click="handleCancel"
            class="btn btn-secondary"
          >
            Cancelar
          </button>
          <button 
            type="submit" 
            class="btn btn-danger"
          >
            Salvar
          </button>
        </div>
        
      </form>
    </div>
  </div>
</template>

<style scoped>
.container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 175px);
  background-color: var(--color-surface-soft);
  padding: 20px;
}

.card {
  background: var(--color-surface);
  border-radius: 32px;
  padding: 32px;
  width: 100%;
  max-width: 440px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  position: relative;
}

.title {
  font-size: 28px;
  font-weight: bold;
  color: var(--color-text);
  margin: 0 0 24px 0;
}

.response-popup {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

.response-popup.success .popup-content {
  border-top: 4px solid var(--color-success);
}

.response-popup.error .popup-content {
  border-top: 4px solid var(--color-danger);
}

.popup-content {
  background: var(--color-surface);
  border-radius: 16px;
  padding: 24px;
  text-align: center;
  max-width: 320px;
}

.icon {
  width: 60px;
  height: 60px;
  margin: 0 auto 16px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  color: white;
}

.icon.success {
  background-color: var(--color-success);
}

.icon.error {
  background-color: var(--color-danger);
}

.popup-title {
  font-size: 18px;
  font-weight: bold;
  color: var(--color-text);
  margin: 0 0 8px 0;
}

.popup-message {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin: 0;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--color-border);
  border-radius: 9999px;
  font-size: 16px;
  font-family: inherit;
  background-color: var(--color-surface);
  color: var(--color-text);
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: var(--color-danger);
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.form-input.small {
  width: 80px;
  text-align: center;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}



.form-select {
  width: 100%;
  appearance: none;
  padding: 12px 16px;
  padding-right: 40px;
  border: 1px solid var(--color-border);
  border-radius: 9999px;
  font-size: 16px;
  font-family: inherit;
  background-color: var(--color-surface);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-select:focus {
  outline: none;
  border-color: var(--color-danger);
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.select-wrapper {
  position: relative;
}

.select-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  color: var(--color-text);
  pointer-events: none;
}

.recurring-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-bottom: 8px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  user-select: none;
  font-size: 16px;
  font-weight: 500;
  color: var(--color-text);
  padding-left: 4px;
}

.checkbox-input {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: var(--color-danger);
}

.recurring-input {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-left: 4px;
}

.recurring-text {
  font-size: 14px;
  color: var(--color-text-tertiary);
}

.form-actions {
  display: flex;
  gap: 16px;
  padding-top: 16px;
}

.btn {
  flex: 1;
  padding: 14px 16px;
  font-size: 16px;
  font-weight: 500;
  border: none;
  border-radius: 9999px;
  cursor: pointer;
  transition: all 0.2s;
  text-transform: none;
}

.btn-secondary {
  background-color: var(--color-surface-alt);
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.btn-secondary:hover {
  background-color: var(--color-border);
}

.btn-secondary:active {
  transform: scale(0.98);
}

.btn-danger {
  background-color: var(--color-danger);
  color: white;
  box-shadow: 0 4px 6px rgba(239, 68, 68, 0.2);
}

.btn-danger:hover {
  background-color: #dc2626;
}

.btn-danger:active {
  transform: scale(0.98);
}

@media (max-width: 768px) {
  .container {
    min-height: calc(100vh - 150px);
    padding: 15px;
  }

  .card {
    padding: 24px;
    border-radius: 24px;
  }

  .title {
    font-size: 24px;
  }

  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
