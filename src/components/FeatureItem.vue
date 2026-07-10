<template>
  <div class="feature-item">
    <div class="feature-number">
      {{ number }}
    </div>
    <div class="feature-text">
      <h3>{{ title }}</h3>
      <p>{{ description }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  number: string;
  title: string;
  description: string;
}>();
</script>

<style scoped>
.feature-item {
  display: flex;
  gap: 20px;
  margin-bottom: 40px;
  padding: 20px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
}

.feature-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.feature-number {
  font-size: 32px;
  font-weight: 800;
  color: var(--color-success-dark);
  line-height: 1;
  min-width: 30px;
  border-left: 4px solid var(--color-success-alt);
  padding-left: 16px;
  flex-shrink: 0;
}

.feature-text {
  flex: 1;
}

.feature-text h3 {
  font-size: 18px;
  color: var(--color-text);
  margin: 0 0 8px 0;
  font-weight: 700;
  line-height: 1.3;
}

.feature-text p {
  font-size: 14px;
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin: 0;
}
</style>
