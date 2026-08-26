<template>
  <div class="app-layout">
    <aside class="sidebar">
      <div class="sidebar-logo">
        <span class="logo-text">LEDGER</span>
      </div>

      <nav class="sidebar-nav">
        <button
          class="sidebar-item"
          :class="{ active: route.path === '/' }"
          @click="handleNavigate('/')"
        >
          <Home :size="22" />
          <span>Início</span>
        </button>

        <button
          class="sidebar-item"
          :class="{ active: route.path === '/company/settings' }"
          @click="handleNavigate('/company/settings')"
        >
          <Layers :size="22" />
          <span>Gerenciamento</span>
        </button>

        <button
          class="sidebar-item"
          :class="{ active: route.path === '/reports' }"
          @click="handleNavigate('/reports')"
        >
          <PieChart :size="22" />
          <span>Relatórios</span>
        </button>

        <button
          class="sidebar-item"
          :class="{ active: route.path === '/settings' }"
          @click="handleNavigate('/settings')"
        >
          <Settings :size="22" />
          <span>Configurações</span>
        </button>
      </nav>

      <div class="sidebar-actions">
        <button class="btn-action btn-income" @click="handleNavigate('/add/income')">
          <ArrowUp :size="20" />
          <span>Entrada</span>
        </button>
        <button class="btn-action btn-expense" @click="handleNavigate('/add/expense')">
          <ArrowDown :size="20" />
          <span>Saída</span>
        </button>
      </div>
    </aside>

    <div class="app-main">
      <TopNav />

      <main class="main-content">
        <router-view />
      </main>
    </div>

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
import { useRouter, useRoute } from 'vue-router';
import { Home, Layers, PieChart, Settings, ArrowUp, ArrowDown } from 'lucide-vue-next';
import { useCompanyStore } from './stores/CompanyStore';
import { useUserStore } from './stores/userStore';
import { useTransactionStore } from './stores/transactionStore';
import { useTagStore } from './stores/tagStore';
import { useAnalyticsStore } from './stores/analyticsStore';
import BottomNav from './components/layout/BottomNav.vue';
import TopNav from './components/layout/TopNav.vue';

const router = useRouter();
const route = useRoute();
const companyStore = useCompanyStore();
const userStore = useUserStore();
const transactionStore = useTransactionStore();
const tagStore = useTagStore();
const analyticsStore = useAnalyticsStore();

const handleNavigate = (path: string) => {
  if (path === '/company/settings') {
    if (!companyStore.company.hasCompany) {
      router.push('/company');
    } else {
      router.push(path);
    }
  } else {
    router.push(path);
  }
};

onMounted(async () => {
  companyStore.loadCompanyData();
  if (userStore.accessToken) {
    await companyStore.syncFromBackend();
  }
});

watch(
  () => userStore.accessToken,
  async (newToken, oldToken) => {
    if (!oldToken && newToken) {
      console.log('Token detectado, sincronizando companies...');
      await companyStore.syncFromBackend();
    }
  }
);

// Limpar dados escopados por empresa quando não houver empresa selecionada
watch(
  () => companyStore.company.hasCompany,
  (hasCompany) => {
    if (!hasCompany) {
      transactionStore.clearTransactions();
      tagStore.clearTags();
      analyticsStore.clearAnalytics();
    }
  }
);

watch(
  () => userStore.accessToken,
  (newToken, oldToken) => {
    if (oldToken && !newToken && router.currentRoute.value.name !== 'entrar') {
      console.log('Token removido, redirecionando para login...');
      router.push({ name: 'entrar' });
    }
  }
);
</script>

<style>
body, html {
  margin: 0;
  padding: 0;
  overflow-x: hidden;
  background-color: var(--color-surface-soft);
}
</style>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
}

.app-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.sidebar {
  display: none;
}

.main-content {
  flex: 1;
  padding-top: 75px;
  padding-bottom: 100px;
  box-sizing: border-box;
}

@media (min-width: 1024px) {
  .sidebar {
    display: flex;
    flex-direction: column;
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    width: 240px;
    background-color: var(--color-surface);
    border-right: 1px solid var(--color-border);
    padding: 20px 16px;
    z-index: 1002;
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
  }

  .sidebar-logo {
    margin-bottom: 24px;
  }

  .logo-text {
    font-family: var(--font-display);
    font-weight: 800;
    font-size: 20px;
    letter-spacing: 1px;
    color: var(--color-text);
  }

  .sidebar-nav {
    display: flex;
    flex-direction: column;
    gap: 10px;
    flex: 1;
  }

  .sidebar-item {
    display: flex;
    align-items: center;
    gap: 14px;
    width: 100%;
    padding: 12px 14px;
    border-radius: 14px;
    border: none;
    background: transparent;
    color: var(--color-text-secondary);
    font-family: var(--font-body);
    font-weight: 600;
    font-size: 15px;
    cursor: pointer;
    transition: background 0.2s ease, color 0.2s ease;
    box-sizing: border-box;
  }

  .sidebar-item:hover {
    background-color: var(--color-surface-soft);
    color: var(--color-text);
  }

  .sidebar-item.active {
    background-color: var(--color-surface-soft);
    color: var(--color-success-alt);
  }

  .sidebar-actions {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-top: 16px;
  }

  .btn-action {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    padding: 14px;
    border-radius: 50px;
    border: none;
    color: white;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 6px 15px rgba(0, 0, 0, 0.15);
    font-family: var(--font-body);
  }

  .btn-income {
    background: var(--color-success-gradient);
  }

  .btn-expense {
    background: var(--color-danger-gradient);
  }

  .main-content {
    margin-left: 240px;
    padding-top: 75px;
    padding-bottom: 24px;
  }
}
</style>
