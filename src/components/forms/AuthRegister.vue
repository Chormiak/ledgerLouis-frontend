<script setup lang="ts">
import { reactive } from 'vue';
import { useRouter } from 'vue-router';
import BaseInput from '../ui/BaseInput.vue';
import PrimaryButton from '../ui/PrimaryButton.vue';
import UserService from '../../services/userService';
import ResponsePopUp from './ResponsePopUp.vue';
import type { userRegisterType } from '@/types/UserTypes';

const userService = new UserService();
const router = useRouter();

const formData = reactive<userRegisterType>({
  name: '',
  email: '',
  password: '',
  // passwordConfirmation: ''
});

const response = reactive({
  status: '',
  message: '',
  show: false
});

const handleRegister = async () => {
  try {
    if (!formData.name || !formData.email || !formData.password) {
      response.status = 'error';
      response.message = 'Preencha todos os campos';
      response.show = true;
      return;
    }


    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailRegex.test(formData.email)) {
      response.status = 'error';
      response.message = 'Digite um e-mail válido';
      response.show = true;
      return;
    }


    if (formData.password.length < 8) {
      response.status = 'error';
      response.message = 'A senha deve ter no mínimo 8 caracteres';
      response.show = true;
      return;
    }
    // validação se tem numero
    if (!/\d/.test(formData.password)) {
      response.status = 'error';
      response.message = 'A senha deve conter pelo menos um número';
      response.show = true;
      return;
    }
    if (formData.name.length < 7) {
      response.status = 'error';
      response.message = 'O nome deve conter pelo menos 7 caracteres';
      response.show = true;
      return;
    }
    await userService.register(formData);

    response.status = 'success';
    response.message = 'Cadastro realizado com sucesso!';
    response.show = true;
  // Redirecionar para login após 2 segundos
    setTimeout(() => {
      router.push('/entrar');
    }, 2000);


  } catch (error: any) {
    response.status = 'error';
    response.message =
      error?.response?.data?.message || 'Erro ao cadastrar usuário';
    response.show = true;
  }

  setTimeout(() => {
    response.show = false;
  }, 3000);
};
</script>
<template>
  <ResponsePopUp :status="response.status" :message="response.message" :show="response.show"
    @close="response.show = false" />

  <form @submit.prevent="handleRegister" class="auth-form">
    <div class="field-list">
      <div class="field-row">
        <label for="registerName" class="field-label">Nome</label>
        <BaseInput id="registerName" placeholder="Digite o nome" v-model="formData.name" />
      </div>

      <div class="field-row">
        <label for="registerEmail" class="field-label">E-mail</label>
        <BaseInput id="registerEmail" placeholder="exemplo@email.com" v-model="formData.email" />
      </div>

      <div class="field-row">
        <label for="registerPassword" class="field-label">Senha</label>
        <BaseInput id="registerPassword" type="password" placeholder="••••••••" v-model="formData.password" />
      </div>

      <!-- <div class="field-row">
        <label for="registerPasswordConfirmation" class="field-label">Confirmar senha</label>
        <BaseInput id="registerPasswordConfirmation" type="password" placeholder="••••••••" v-model="formData.passwordConfirmation" />
      </div> -->
    </div>

    <PrimaryButton type="submit">Cadastrar</PrimaryButton>
  </form>
</template>

<style scoped>
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.field-list {
  display: flex;
  flex-direction: column;
}

.field-row {
  display: grid;
  grid-template-columns: 100px 1fr;
  align-items: center;
  gap: 16px;
  padding: 16px 0;
  border-bottom: 1px solid var(--color-border);
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

.field-label {
  font-size: 13.5px;
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
  font-size: 15px;
}

.field-row :deep(.custom-input:focus) {
  box-shadow: none;
  background: transparent;
}

@media (max-width: 400px) {
  .field-row {
    grid-template-columns: 1fr;
    gap: 6px;
  }
}
</style>
