<template>
  <div class="app-layout">
    <TopNav />

    <main class="main-content">
      <router-view />
    </main>

    <BottomNav />

    <svg width="0" height="0" style="position: absolute;">
      <defs>
        <linearGradient id="green-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#27B969;stop-opacity:1" />
          <stop offset="100%" style="stop-color:#1DE276;stop-opacity:1" />
        </linearGradient>
      </defs>
    </svg>
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import BottomNav from './components/layout/BottomNav.vue';
import TopNav from './components/layout/TopNav.vue';
import { useCompanyStore } from './stores/CompanyStore';
import { useUserStore } from './stores/userStore';
import { useTransactionStore } from './stores/transactionStore';

const router = useRouter();
const companyStore = useCompanyStore();
const userStore = useUserStore();
const transactionStore = useTransactionStore();

onMounted(async () => {
  companyStore.loadCompanyData();
  if (userStore.accessToken) {
    await companyStore.syncFromBackend();
  }
});

// Observar mudanças no accessToken para sincronizar companies após login
watch(
  () => userStore.accessToken,
  async (newToken, oldToken) => {
    // Se o token mudou de vazio para algo, significa que o usuário fez login
    if (!oldToken && newToken) {
      console.log('Token detectado, sincronizando companies...');
      await companyStore.syncFromBackend();
    }
  }
);

// Limpar transações quando não houver empresa selecionada
watch(
  () => companyStore.company.hasCompany,
  (hasCompany) => {
    if (!hasCompany) {
      transactionStore.clearTransactions();
    }
  }
);

// Redirecionar para login quando o token for limpo (apenas se não estiver na página de login)
watch(
  () => userStore.accessToken,
  (newToken, oldToken) => {
    // Se o token foi removido (era algo e agora é vazio) e não estamos na página de login
    if (oldToken && !newToken && router.currentRoute.value.name !== 'entrar') {
      console.log('Token removido, redirecionando para login...');
      router.push({ name: 'entrar' });
    }
  }
);
</script>

<style>
/* Reset básico para garantir que o layout ocupe a tela toda */
body, html {
  margin: 0;
  padding: 0;
  overflow-x: hidden;
  background-color: var(--color-surface-soft);
}
</style>

<style scoped>
/* Recomendo usar grid para a criação dos layouts - William */
.app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-content {
  flex: 1;
  /* Espaço para a TopNav não cobrir o topo (65px de altura + 10px de respiro) */
  padding-top: 75px; 
  
  /* Espaço para a BottomNav não cobrir o rodapé (90px a 100px dependendo do seu design) */
  padding-bottom: 100px; 
  
  box-sizing: border-box;
}
</style>