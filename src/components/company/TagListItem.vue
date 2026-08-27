<script setup lang="ts">
import { ref } from 'vue';
import type { TagDto } from '@/services/tagService';
import { Check, Pencil, Trash2, X } from 'lucide-vue-next';
import { colorForTag } from '@/utils/tagColor';

interface Props {
  tag: TagDto;
}

interface Emits {
  (e: 'rename', id: string, name: string): void;
  (e: 'delete', id: string): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const isEditing = ref(false);
const draftName = ref(props.tag.name);

const startEdit = () => {
  draftName.value = props.tag.name;
  isEditing.value = true;
};

const cancelEdit = () => {
  isEditing.value = false;
};

const confirmEdit = () => {
  const trimmed = draftName.value.trim();
  if (trimmed && trimmed !== props.tag.name) {
    emit('rename', props.tag.id, trimmed);
  }
  isEditing.value = false;
};
</script>

<script lang="ts">
export default {
  name: 'TagListItem',
};
</script>

<template>
  <div class="category-item">
    <div class="category-content">
      <span class="tag-dot" :style="{ backgroundColor: colorForTag(tag.id) }" aria-hidden="true"></span>

      <div class="category-info" v-if="!isEditing">
        <h5>{{ tag.name }}</h5>
      </div>

      <input
        v-else
        v-model="draftName"
        type="text"
        class="tag-edit-input"
        @keyup.enter="confirmEdit"
        @keyup.escape="cancelEdit"
      />
    </div>

    <div class="item-actions">
      <template v-if="isEditing">
        <button class="btn-icon" title="Salvar" @click="confirmEdit">
          <Check :size="16" />
        </button>
        <button class="btn-icon" title="Cancelar" @click="cancelEdit">
          <X :size="16" />
        </button>
      </template>
      <template v-else>
        <button class="btn-icon" title="Renomear" @click="startEdit">
          <Pencil :size="16" />
        </button>
        <button class="btn-delete" :title="`Remover ${tag.name}`" @click="$emit('delete', tag.id)">
          <Trash2 :size="18" />
        </button>
      </template>
    </div>
  </div>
</template>

<style scoped>
.category-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  transition: all 0.2s;
}

.category-item:hover {
  border-color: var(--color-primary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.category-content {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.tag-dot {
  width: 12px;
  height: 12px;
  border-radius: 999px;
  flex-shrink: 0;
}

.category-info h5 {
  margin: 0;
  font-size: 0.95rem;
  color: var(--color-text);
  font-weight: 600;
}

.tag-edit-input {
  flex: 1;
  padding: 8px 10px;
  border: 1px solid var(--color-primary);
  border-radius: 6px;
  font-size: 0.95rem;
  font-family: inherit;
  background: var(--color-surface);
  color: var(--color-text);
}

.tag-edit-input:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(29, 185, 84, 0.1);
}

.item-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.btn-icon {
  background: none;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  padding: 6px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-icon:hover {
  color: var(--color-primary);
  transform: scale(1.1);
}

.btn-delete {
  background: none;
  border: none;
  color: var(--color-error);
  cursor: pointer;
  padding: 6px;
  transition: all 0.2s;
  opacity: 0.6;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-delete:hover {
  opacity: 1;
  transform: scale(1.1);
}
</style>
