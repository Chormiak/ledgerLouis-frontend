<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { Plus, Tag as TagIcon, X } from 'lucide-vue-next';
import TagListItem from './TagListItem.vue';
import PrimaryButton from '@/components/ui/PrimaryButton.vue';
import { useTagStore } from '@/stores/tagStore';
import { useCompanyStore } from '@/stores/CompanyStore';

const tagStore = useTagStore();
const companyStore = useCompanyStore();

const showForm = ref(false);
const newTagName = ref('');
const message = reactive({ status: '', text: '', show: false });

const extractErrorCode = (error: unknown): string | undefined => {
  if (typeof error === 'object' && error !== null && 'response' in error) {
    return (error as { response?: { data?: { error?: string } } }).response?.data?.error;
  }
  return undefined;
};

const notify = (status: 'success' | 'error', text: string) => {
  message.status = status;
  message.text = text;
  message.show = true;
  setTimeout(() => {
    message.show = false;
  }, 2500);
};

const resetForm = () => {
  newTagName.value = '';
  showForm.value = false;
};

const handleAddTag = async () => {
  if (!newTagName.value.trim()) {
    notify('error', 'Digite um nome para a tag');
    return;
  }

  try {
    await tagStore.createTag(newTagName.value.trim());
    notify('success', 'Tag criada com sucesso!');
    resetForm();
  } catch (error) {
    const code = extractErrorCode(error);
    notify('error', code === 'TAG_ALREADY_EXISTS' ? 'Já existe uma tag com esse nome' : 'Erro ao criar tag');
  }
};

const handleRenameTag = async (id: string, name: string) => {
  try {
    await tagStore.renameTag(id, name);
    notify('success', 'Tag atualizada!');
  } catch (error) {
    const code = extractErrorCode(error);
    notify('error', code === 'TAG_ALREADY_EXISTS' ? 'Já existe uma tag com esse nome' : 'Erro ao renomear tag');
  }
};

const handleDeleteTag = async (id: string) => {
  try {
    await tagStore.deleteTag(id);
    notify('success', 'Tag removida!');
  } catch {
    notify('error', 'Erro ao remover tag');
  }
};

onMounted(() => {
  if (companyStore.company.hasCompany) {
    tagStore.fetchTags();
  }
});
</script>

<script lang="ts">
export default {
  name: 'TagManager',
};
</script>

<template>
  <div class="panel">
    <div class="panel-header">
      <div>
        <h2 class="panel-title">
          <TagIcon :size="18" />
          Tags
        </h2>
        <p class="panel-subtitle">Use tags para catalogar transações com um ou mais rótulos livres.</p>
      </div>

      <PrimaryButton v-if="!showForm" variant="neutral" compact @click="showForm = true">
        <Plus :size="15" />
        Nova Tag
      </PrimaryButton>
    </div>

    <div v-if="message.show" class="message" :class="message.status">
      {{ message.text }}
    </div>

    <div v-if="showForm" class="form-container">
      <div class="form-group">
        <label>Nome da Tag</label>
        <input
          v-model="newTagName"
          type="text"
          placeholder="Ex: Fornecedores"
          class="input"
          autofocus
          @keyup.enter="handleAddTag"
        />
      </div>

      <div class="form-actions">
        <PrimaryButton compact :loading="tagStore.loading" @click="handleAddTag">Adicionar</PrimaryButton>
        <PrimaryButton variant="neutral" compact @click="resetForm">
          <X :size="15" />
          Cancelar
        </PrimaryButton>
      </div>
    </div>

    <p v-if="!tagStore.loading && tagStore.tags.length === 0" class="empty-state">
      Nenhuma tag cadastrada ainda. Crie tags para organizar suas transações.
    </p>

    <div class="tags-list" v-else>
      <TagListItem
        v-for="tag in tagStore.tags"
        :key="tag.id"
        :tag="tag"
        @rename="handleRenameTag"
        @delete="handleDeleteTag"
      />
    </div>
  </div>
</template>

<style scoped>
.panel {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  padding: 28px;
}

.panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.panel-title {
  font-family: var(--font-display);
  font-size: 1.1rem;
  font-weight: 800;
  color: var(--color-text);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.panel-subtitle {
  margin-top: 4px;
  color: var(--color-text-secondary);
  font-size: 0.9rem;
}

.message {
  padding: 12px 16px;
  border-radius: 12px;
  margin-bottom: 16px;
  font-weight: 600;
  font-size: 0.9rem;
}

.message.success {
  background: var(--color-primary-glow);
  color: var(--color-success-dark);
}

.message.error {
  background: var(--color-danger-soft);
  color: var(--color-danger);
}

.form-container {
  background: var(--color-surface-soft);
  padding: 20px;
  border-radius: 14px;
  margin-bottom: 20px;
  border: 1px solid var(--color-border);
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--color-text-secondary);
}

.input {
  width: 100%;
  padding: 12px 14px;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-input);
  font-size: 0.95rem;
  font-family: inherit;
  background: var(--color-surface);
  color: var(--color-text);
  transition: border-color 0.2s;
}

.input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-glow);
}

.form-actions {
  display: flex;
  gap: 10px;
}

.empty-state {
  color: var(--color-text-secondary);
  font-size: 0.9rem;
  padding: 16px;
  background: var(--color-surface-soft);
  border-radius: 12px;
  border: 1px dashed var(--color-border);
}

.tags-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
</style>
