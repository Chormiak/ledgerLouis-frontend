<script setup lang="ts">
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ArrowLeft } from 'lucide-vue-next';
import TagManager from '@/components/company/TagManager.vue';
import { useCompanyStore } from '@/stores/CompanyStore';

const router = useRouter();
const companyStore = useCompanyStore();

onMounted(() => {
  if (!companyStore.company.hasCompany) {
    router.replace({ name: 'company' });
  }
});
</script>

<template>
  <main class="tags-page">
    <div class="tags-shell">
      <header class="tags-header">
        <button class="back-button" type="button" @click="router.back()">
          <ArrowLeft :size="18" />
          Voltar
        </button>

        <div>
          <p class="eyebrow">Organização financeira</p>
          <h1>Tags</h1>
          <p class="subtitle">
            Crie, renomeie e remova tags para catalogar suas transações com um ou mais rótulos livres.
          </p>
        </div>
      </header>

      <TagManager />
    </div>
  </main>
</template>

<style scoped>
.tags-page {
  min-height: calc(100vh - 165px);
  padding: 20px 16px 32px;
  background: linear-gradient(180deg, #f4f7fb 0%, #eef3f8 100%);
}

.tags-shell {
  max-width: 900px;
  margin: 0 auto;
  display: grid;
  gap: 20px;
}

.tags-header {
  display: grid;
  gap: 14px;
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.65);
  border-radius: 28px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.92), rgba(248, 250, 252, 0.88));
  box-shadow: 0 18px 50px rgba(15, 23, 42, 0.08);
}

.back-button {
  justify-self: start;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text);
  border-radius: 999px;
  padding: 8px 14px;
  font-weight: 700;
  font-size: 13px;
  cursor: pointer;
}

.eyebrow {
  color: var(--color-success-dark);
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 8px;
}

h1 {
  font-family: var(--font-display);
  font-size: clamp(1.6rem, 4vw, 2.4rem);
  color: var(--color-text);
  margin-bottom: 8px;
}

.subtitle {
  max-width: 58ch;
  color: var(--color-text-secondary);
  line-height: 1.7;
}

@media (min-width: 640px) {
  .tags-page {
    padding-inline: 20px;
  }
}

@media (min-width: 1024px) {
  .tags-page {
    padding: 28px 24px 40px;
  }
}
</style>
