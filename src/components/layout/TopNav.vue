<template>
  <header class="top-navbar">
    <router-link to="/" class="logo-section">
      <span class="logo-text">LEDGER</span>
    </router-link>

    <div class="nav-actions">
      <button class="icon-button" @click="goToInvitations" title="Convites">
        <Mail :size="20" stroke-width="2.5" />
        <span v-if="pendingInvitations > 0" class="badge">{{ pendingInvitations }}</span>
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { Mail } from 'lucide-vue-next';
import { useRouter } from 'vue-router';
import { ref, onMounted } from 'vue';
import CompanyService from '@/services/companyService';

const router = useRouter();
const pendingInvitations = ref(0);
const service = new CompanyService();

const loadPendingInvitations = async () => {
  try {
    const response = await service.listUserInvitations();
    pendingInvitations.value = response.items.length;
  } catch {
    pendingInvitations.value = 0;
  }
};

const goToInvitations = () => {
  router.push({ name: 'invitations' });
};

onMounted(() => {
  loadPendingInvitations();
});
</script>

<style scoped>
.top-navbar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 52px;
  background-color: var(--color-surface);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 18px;
  box-sizing: border-box;
  z-index: 1001;

  border-bottom: 1px solid var(--color-border);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02);
}

.logo-section {
  display: inline-flex;
  align-items: center;
  text-decoration: none;
}

.logo-text {
  font-family: var(--font-display);
  font-weight: 800;
  font-size: 15px;
  letter-spacing: 1px;
  color: var(--color-text);
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon-button {
  position: relative;
  background: none;
  border: none;
  cursor: pointer;
  padding: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text);
  transition: transform 0.2s ease;
}

.icon-button:active {
  transform: scale(0.92);
}

.badge {
  position: absolute;
  top: 0;
  right: 0;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  border-radius: 999px;
  background: var(--color-danger);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  line-height: 16px;
  text-align: center;
}
</style>
