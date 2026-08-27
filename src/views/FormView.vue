<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import AuthLogin from '@/components/forms/AuthLogin.vue';
import AuthRegister from '@/components/forms/AuthRegister.vue';
import NavAuth from '@/components/forms/NavAuth.vue';

const route = useRoute();
const router = useRouter();
const activeTab = ref(route.meta.tab === 'login' ? 'login' : 'register');

const toggleTab = (tab: string) => {
  activeTab.value = tab;
  router.replace({ name: tab === 'login' ? 'entrar' : 'cadastro' });
};

watch(
  () => route.meta.tab,
  (tab) => {
    activeTab.value = tab === 'login' ? 'login' : 'register';
  }
);

const kicker = computed(() => (activeTab.value === 'login' ? 'Bem-vindo de volta' : 'Comece agora'));
const description = computed(() =>
  activeTab.value === 'login'
    ? 'Entre com seu e-mail e senha para continuar.'
    : 'Leva menos de um minuto para organizar as finanças do seu negócio.',
);
</script>

<template>
  <main class="auth-page">
    <section class="auth-container">
      <header class="header-block">
        <p class="kicker">{{ kicker }}</p>
        <h1 v-if="activeTab === 'login'">Acesse sua <span class="accent-text">conta</span></h1>
        <h1 v-else>Crie sua <span class="accent-text">conta</span></h1>
        <p class="description">{{ description }}</p>
      </header>

      <div class="auth-card">
        <NavAuth :active-tab="activeTab" @change-tab="toggleTab" />

        <div class="auth-body">
          <AuthRegister v-if="activeTab === 'register'" />
          <AuthLogin v-else />
        </div>
      </div>
    </section>
  </main>
</template>

<style scoped>
.auth-page {
  min-height: calc(100vh - 65px);
  display: flex;
  justify-content: center;
  padding: 64px 20px;
  background: var(--color-bg);
}

.auth-container {
  width: 100%;
  max-width: 440px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.header-block {
  text-align: left;
}

.kicker {
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-primary);
  margin-bottom: 14px;
}

h1 {
  font-family: var(--font-display);
  font-size: clamp(1.6rem, 4vw, 2rem);
  font-weight: 800;
  line-height: 1.2;
  color: var(--color-text);
  margin-bottom: 14px;
  text-wrap: balance;
}

.accent-text {
  background: var(--color-success-gradient);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.description {
  color: var(--color-text-secondary);
  font-size: 15.5px;
  line-height: 1.7;
}

.auth-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-input);
  overflow: hidden;
}

.auth-body {
  padding: 28px;
}

@media (max-width: 480px) {
  .auth-page {
    padding: 40px 16px;
  }
}
</style>
