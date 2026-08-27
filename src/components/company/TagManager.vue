<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { Plus, Tag as TagIcon } from 'lucide-vue-next';
import TagListItem from './TagListItem.vue';
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
  <div class="category-manager">
    <div class="manager-header">
      <h3>
        <TagIcon :size="18" />
        Tags
      </h3>
      <button class="btn-add" @click="showForm = !showForm" v-if="!showForm">
        <Plus :size="18" />
        Nova Tag
      </button>
    </div>

    <p class="manager-hint">Use tags para catalogar transações com um ou mais rótulos livres.</p>

    <div v-if="message.show" class="message" :class="message.status">
      {{ message.text }}
    </div>

    <div v-if="showForm" class="form-container">
      <h4>Adicionar Nova Tag</h4>

      <div class="form-group">
        <label>Nome da Tag</label>
        <input
          v-model="newTagName"
          type="text"
          placeholder="Ex: Fornecedores"
          class="input"
          @keyup.enter="handleAddTag"
        />
      </div>

      <div class="form-actions">
        <button class="btn-success" @click="handleAddTag" :disabled="tagStore.loading">
          {{ tagStore.loading ? 'Salvando...' : 'Adicionar' }}
        </button>
        <button class="btn-cancel" @click="resetForm">Cancelar</button>
      </div>
    </div>

    <p v-if="!tagStore.loading && tagStore.tags.length === 0" class="empty-hint">
      Nenhuma tag cadastrada ainda. Crie tags para organizar suas transações.
    </p>

    <div class="categories-list" v-else>
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
.category-manager {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
}

.manager-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  padding-bottom: 16px;
  border-bottom: 2px solid var(--color-border);
}

.manager-header h3 {
  margin: 0;
  font-size: 1.3rem;
  color: var(--color-primary);
  display: flex;
  align-items: center;
  gap: 8px;
}

.manager-hint {
  margin: 12px 0 20px;
  color: var(--color-text-secondary);
  font-size: 0.88rem;
}

.btn-add {
  background: var(--color-primary);
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-add:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(29, 185, 84, 0.3);
}

.message {
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  font-weight: 500;
  animation: slideIn 0.3s ease;
}

.message.success {
  background: rgba(29, 185, 84, 0.1);
  color: #27ae60;
  border: 1px solid rgba(29, 185, 84, 0.2);
}

.message.error {
  background: rgba(255, 68, 68, 0.1);
  color: #c41e3a;
  border: 1px solid rgba(255, 68, 68, 0.2);
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.form-container {
  background: var(--color-bg);
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  border: 1px solid var(--color-border);
}

.form-container h4 {
  margin: 0 0 16px 0;
  color: var(--color-text);
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
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  font-size: 0.95rem;
  font-family: inherit;
  background: var(--color-surface);
  color: var(--color-text);
  transition: border-color 0.2s;
}

.input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(29, 185, 84, 0.1);
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.btn-success {
  flex: 1;
  background: var(--color-primary);
  color: white;
  border: none;
  padding: 12px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-success:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(29, 185, 84, 0.3);
}

.btn-success:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-cancel {
  flex: 1;
  background: var(--color-border);
  color: var(--color-text);
  border: none;
  padding: 12px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-cancel:hover {
  background: var(--color-text-secondary);
  color: white;
}

.empty-hint {
  color: var(--color-text-secondary);
  font-size: 0.9rem;
  padding: 14px;
  background: var(--color-bg);
  border-radius: 8px;
  border: 1px dashed var(--color-border);
}

.categories-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
</style>
