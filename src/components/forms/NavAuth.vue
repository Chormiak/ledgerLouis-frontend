<script setup lang="ts">
const props = defineProps<{
  activeTab: string;
}>();

const emit = defineEmits(['change-tab']);
</script>

<template>
  <nav class="auth-tabs">
    <button
      :class="['tab-item', { active: props.activeTab === 'login' }]"
      @click="emit('change-tab', 'login')"
    >
      Entrar
    </button>

    <button
      :class="['tab-item', { active: props.activeTab === 'register' }]"
      @click="emit('change-tab', 'register')"
    >
      Criar conta
    </button>
  </nav>
</template>

<style scoped>
.auth-tabs {
  display: flex;
  border-bottom: 1px solid var(--color-border);
}

.tab-item {
  position: relative;
  flex: 1;
  padding: 16px;
  border: none;
  background: transparent;
  font-family: var(--font-body);
  font-weight: 700;
  font-size: 14px;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: color 0.2s ease;
}

.tab-item:hover {
  color: var(--color-text);
}

.tab-item.active {
  color: var(--color-primary);
}

.tab-item.active::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  bottom: -1px;
  height: 2px;
  background: var(--color-primary);
}
</style>
