<template>
  <div class="app-layout">
    <aside class="sidebar" :class="{ 'sidebar--collapsed': sidebarCollapsed }">
      <button
        class="sidebar-toggle"
        type="button"
        :aria-label="sidebarCollapsed ? 'Expandir menu' : 'Recolher menu'"
        :title="sidebarCollapsed ? 'Expandir menu' : 'Recolher menu'"
        @click="toggleSidebar"
      >
        <PanelLeftClose v-if="!sidebarCollapsed" :size="15" />
        <PanelLeftOpen v-else :size="15" />
      </button>

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

      <div class="sidebar-actions">
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

    <div class="app-main" :class="{ 'app-main--collapsed': sidebarCollapsed }">
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
import { onMounted, ref, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import {
  Home,
  Layers,
  PieChart,
  Settings,
  ArrowUp,
  ArrowDown,
  PanelLeftClose,
  PanelLeftOpen,
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

const SIDEBAR_STORAGE_KEY = 'sidebarCollapsed';
const sidebarCollapsed = ref(localStorage.getItem(SIDEBAR_STORAGE_KEY) === 'true');

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value;
  localStorage.setItem(SIDEBAR_STORAGE_KEY, String(sidebarCollapsed.value));
};

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
  padding-top: 75px;
  padding-bottom: 100px;
  box-sizing: border-box;
}

@media (min-width: 1024px) {
  .sidebar {
    display: flex;
    flex-direction: column;
    position: fixed;
    top: 65px;
    left: 0;
    bottom: 0;
    width: 232px;
    background-color: var(--color-surface);
    border-right: 1px solid var(--color-border);
    padding: 24px 14px;
    z-index: 900;
    transition: width 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .sidebar--collapsed {
    width: 76px;
  }

  .sidebar-toggle {
    position: absolute;
    top: 22px;
    right: -12px;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    border: 1px solid var(--color-border);
    background: var(--color-surface);
    color: var(--color-text-secondary);
    cursor: pointer;
    transition: color 0.2s ease, border-color 0.2s ease, transform 0.15s ease;
  }

  .sidebar-toggle:hover {
    color: var(--color-primary);
    border-color: var(--color-primary);
  }

  .sidebar-toggle:active {
    transform: scale(0.92);
  }

  .sidebar-nav {
    display: flex;
    flex-direction: column;
    gap: 6px;
    flex: 1;
    margin-top: 20px;
  }

  .sidebar-item {
    position: relative;
    display: flex;
    align-items: center;
    gap: 14px;
    width: 100%;
    padding: 11px 14px;
    border-radius: 10px;
    border: none;
    background: transparent;
    color: var(--color-text-secondary);
    font-family: var(--font-body);
    font-weight: 600;
    font-size: 14.5px;
    cursor: pointer;
    transition: background 0.2s ease, color 0.2s ease;
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
    left: -14px;
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
    opacity: 1;
    transition: opacity 0.15s ease;
  }

  .sidebar--collapsed .sidebar-item {
    justify-content: center;
    padding: 11px;
    gap: 0;
  }

  .sidebar--collapsed .item-label {
    opacity: 0;
    width: 0;
    pointer-events: none;
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
    gap: 9px;
    padding: 13px;
    border-radius: 12px;
    border: none;
    color: white;
    font-size: 14.5px;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    font-family: var(--font-body);
    transition: box-shadow 0.2s ease, transform 0.15s ease;
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

  .sidebar--collapsed .btn-action {
    gap: 0;
    padding: 13px 0;
  }

  .app-main {
    transition: margin-left 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .main-content {
    margin-left: 232px;
    padding-top: 75px;
    padding-bottom: 24px;
    transition: margin-left 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .app-main--collapsed .main-content {
    margin-left: 76px;
  }
}
</style>
