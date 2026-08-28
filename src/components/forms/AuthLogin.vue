<script setup lang="ts">
import { reactive } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import BaseInput from '../ui/BaseInput.vue';
import PrimaryButton from '../ui/PrimaryButton.vue';
import UserService from '../../services/userService';
import ResponsePopUp from './ResponsePopUp.vue';
import { useUserStore } from '@/stores/userStore';

const userStore = useUserStore();
const router = useRouter();
const route = useRoute();
const loginData = userStore.userLoginData;
const userService = new UserService();

const response = reactive({
  status: '',
  message: '',
  show: false
});

const handleLogin = async () => {
  try {
    loginData.email = loginData.email.trim().toLowerCase();

    if (!loginData.email || !loginData.password) {
      response.status = 'error';
      response.message = 'Preencha todos os campos';
      response.show = true;
      return;
    }


    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailRegex.test(loginData.email)) {
      response.status = 'error';
      response.message = 'Digite um e-mail válido';
      response.show = true;
      return;
    }
    if (loginData.password.length < 8) {
      response.status = 'error';
      response.message = 'A senha deve ter no mínimo 8 caracteres';
      response.show = true;
      return;
    }

    if (loginData.rememberMe) {
      localStorage.setItem('rememberMe', 'true');
    } else {
      localStorage.removeItem('rememberMe');
    }

    // Limpar avatar da conta anterior
    userStore.setavatar('');

    await userService.login(loginData);

    response.status = 'success';
    response.message = 'Login realizado com sucesso!';
    response.show = true;
  // Redirecionar para tela inicial após 1 segundo
    setTimeout(() => {
      const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/';
      router.push(redirect);
    }, 1000);


  } catch (error: any) {
    response.status = 'error';
    const status = error?.response?.status;
    response.message = status === 429
      ? 'Muitas tentativas. Aguarde alguns segundos e tente novamente.'
      : status === 401
        ? 'E-mail ou senha inválidos.'
        : error?.response?.data?.message || 'Não foi possível conectar ao servidor.';
    response.show = true;
  }

  setTimeout(() => {
    response.show = false;
  }, 3000);
};

</script>

<template>
  <ResponsePopUp :status="response.status" :message="response.message" :show="response.show" @close="response.show = false" />

  <form @submit.prevent="handleLogin" class="auth-form">
    <div class="field-list">
      <div class="field-row">
        <label for="loginEmail" class="field-label">E-mail ou CNPJ</label>
        <BaseInput id="loginEmail" placeholder="Digite seu acesso" v-model="loginData.email" />
      </div>

      <div class="field-row">
        <label for="loginPassword" class="field-label">Senha</label>
        <BaseInput id="loginPassword" type="password" placeholder="••••••••" v-model="loginData.password" />
      </div>
    </div>

    <div class="extra-options">
      <label class="remember-me">
        <input type="checkbox" v-model="loginData.rememberMe">
        Lembrar de mim
      </label>
      <a href="#" class="forgot-password">Esqueceu a senha?</a>
    </div>

    <PrimaryButton type="submit">Entrar</PrimaryButton>
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

.extra-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-family: var(--font-body);
  font-size: 0.85rem;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--color-text-secondary);
  cursor: pointer;
}

.forgot-password {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: 600;
}

.forgot-password:hover {
  text-decoration: underline;
}

@media (max-width: 400px) {
  .field-row {
    grid-template-columns: 1fr;
    gap: 6px;
  }
}
</style>
