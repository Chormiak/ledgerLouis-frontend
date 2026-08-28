<template>
  <div class="app-layout">
    <aside class="sidebar">
      <nav class="sidebar-nav">
        <button
          class="sidebar-item"
          :class="{ active: route.path === '/' }"
          title="Início"
          @click="handleNavigate('/')"
        >
          <Home :size="20" />
          <span class="item-label">Início</span>
        </button>

        <button
          class="sidebar-item"
          :class="{ active: route.path === '/company/settings' }"
          title="Gerenciamento"
          @click="handleNavigate('/company/settings')"
        >
          <Layers :size="20" />
          <span class="item-label">Gerenciamento</span>
        </button>

        <button
          class="sidebar-item"
          :class="{ active: route.path === '/reports' }"
          title="Relatórios"
          @click="handleNavigate('/reports')"
        >
          <PieChart :size="20" />
          <span class="item-label">Relatórios</span>
        </button>

        <button
          class="sidebar-item"
          :class="{ active: route.path === '/settings' }"
          title="Configurações"
          @click="handleNavigate('/settings')"
        >
          <Settings :size="20" />
          <span class="item-label">Configurações</span>
        </button>
      </nav>

      <div v-if="companyStore.company.hasCompany" class="sidebar-actions">
        <button class="btn-action btn-income" title="Entrada" @click="handleNavigate('/add/income')">
          <ArrowUp :size="18" />
          <span class="item-label">Entrada</span>
        </button>
        <button class="btn-action btn-expense" title="Saída" @click="handleNavigate('/add/expense')">
          <ArrowDown :size="18" />
          <span class="item-label">Saída</span>
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
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import {
  Home,
  Layers,
  PieChart,
  Settings,
  ArrowUp,
  ArrowDown,
} from 'lucide-vue-next';
import { useCompanyStore } from './stores/CompanyStore';
import { useUserStore } from './stores/userStore';
import { useTransactionStore } from './stores/transactionStore';
import { useTagStore } from './stores/tagStore';
import { useAnalyticsStore } from './stores/analyticsStore';
import { useRecurringTransactionStore } from './stores/recurringTransactionStore';
import BottomNav from './components/layout/BottomNav.vue';
import TopNav from './components/layout/TopNav.vue';

const router = useRouter();
const route = useRoute();
const companyStore = useCompanyStore();
const userStore = useUserStore();
const transactionStore = useTransactionStore();
const tagStore = useTagStore();
const analyticsStore = useAnalyticsStore();
const recurringTransactionStore = useRecurringTransactionStore();

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
      recurringTransactionStore.clearRecurringTransactions();
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
  padding-top: 62px;
  padding-bottom: 100px;
  box-sizing: border-box;
}

@media (min-width: 1024px) {
  /* Trilho fixo: a sidebar sempre reserva 76px no layout. O hover/foco só
     expande a própria sidebar por cima do conteúdo (overlay), sem empurrar
     nada — por isso .main-content nunca muda de margem. */
  .sidebar {
    display: flex;
    flex-direction: column;
    position: fixed;
    top: 52px;
    left: 0;
    bottom: 0;
    width: 76px;
    background-color: var(--color-surface);
    border-right: 1px solid var(--color-border);
    padding: 24px 10px;
    z-index: 900;
    box-shadow: 0 0 0 rgba(15, 23, 42, 0);
    transition: width 0.22s cubic-bezier(0.4, 0, 0.2, 1),
      padding 0.22s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.22s ease;
  }

  .sidebar:hover,
  .sidebar:focus-within {
    width: 232px;
    padding: 24px 14px;
    box-shadow: 6px 0 30px rgba(15, 23, 42, 0.12);
  }

  .sidebar-nav {
    display: flex;
    flex-direction: column;
    gap: 6px;
    flex: 1;
    margin-top: 4px;
  }

  .sidebar-item {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0;
    width: 100%;
    padding: 11px;
    border-radius: 10px;
    border: none;
    background: transparent;
    color: var(--color-text-secondary);
    font-family: var(--font-body);
    font-weight: 600;
    font-size: 14.5px;
    cursor: pointer;
    transition: background 0.2s ease, color 0.2s ease, justify-content 0.1s, padding 0.1s;
    box-sizing: border-box;
  }

  .sidebar-item svg {
    flex-shrink: 0;
  }

  .sidebar-item:hover {
    background-color: var(--color-surface-soft);
    color: var(--color-text);
  }

  .sidebar-item.active {
    background-color: var(--color-surface-soft);
    color: var(--color-success-alt);
  }

  .sidebar-item.active::before {
    content: '';
    position: absolute;
    left: -10px;
    top: 50%;
    transform: translateY(-50%);
    width: 3px;
    height: 18px;
    border-radius: 0 3px 3px 0;
    background: var(--color-primary);
  }

  .item-label {
    white-space: nowrap;
    overflow: hidden;
    opacity: 0;
    width: 0;
    pointer-events: none;
    transition: opacity 0.15s ease;
  }

  .sidebar:hover .sidebar-item,
  .sidebar:focus-within .sidebar-item {
    justify-content: flex-start;
    gap: 14px;
    padding: 11px 14px;
  }

  .sidebar:hover .sidebar-item.active::before,
  .sidebar:focus-within .sidebar-item.active::before {
    left: -14px;
  }

  .sidebar:hover .item-label,
  .sidebar:focus-within .item-label {
    opacity: 1;
    width: auto;
    pointer-events: auto;
  }

  .sidebar-actions {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-top: 16px;
  }

  .btn-action {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0;
    padding: 13px 0;
    border-radius: 999px;
    border: none;
    color: white;
    font-size: 14.5px;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    font-family: var(--font-body);
    transition: box-shadow 0.2s ease, transform 0.15s ease, gap 0.1s, padding 0.1s;
  }

  .sidebar:hover .btn-action,
  .sidebar:focus-within .btn-action {
    gap: 9px;
    padding: 13px;
  }

  .btn-action:hover {
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.14);
    transform: translateY(-1px);
  }

  .btn-action:active {
    transform: translateY(0);
  }

  .btn-income {
    background: var(--color-success-gradient);
  }

  .btn-expense {
    background: var(--color-danger-gradient);
  }

  .main-content {
    margin-left: 76px;
    padding-top: 62px;
    padding-bottom: 24px;
  }
}
</style>
