<template>
  <main class="settings-page">
    <div class="settings-container">
      <header class="page-header">
        <div class="identity">
          <div class="avatar">{{ companyName.charAt(0).toUpperCase() }}</div>
          <div>
            <p class="kicker">Sua empresa</p>
            <h1>{{ companyName }}</h1>
          </div>
        </div>
        <button class="danger-button" @click="leaveCompany">Sair da empresa</button>
      </header>

      <section class="panel">
        <h2 class="panel-title">Dados da empresa</h2>

        <div class="field-list">
          <div class="field-row">
            <span class="field-label">Nome</span>
            <span class="field-value">{{ companyStore.company.name || 'Não informado' }}</span>
          </div>
          <div class="field-row">
            <span class="field-label">CNPJ</span>
            <span class="field-value">{{ companyStore.company.cnpj || 'Não informado' }}</span>
          </div>
          <div class="field-row">
            <span class="field-label">Email</span>
            <span class="field-value">{{ companyStore.company.email || 'Não informado' }}</span>
          </div>
          <div class="field-row">
            <span class="field-label">Telefone</span>
            <span class="field-value">{{ companyStore.company.phone || 'Não informado' }}</span>
          </div>
        </div>
      </section>

      <section class="panel">
        <header class="panel-header">
          <div>
            <h2 class="panel-title">Membros</h2>
            <p class="panel-subtitle">Convide e acompanhe quem faz parte da sua empresa.</p>
          </div>
          <button class="ghost-button" @click="loadMembers">Atualizar</button>
        </header>

        <p v-if="membersLoading" class="empty-state">Carregando membros...</p>
        <p v-else-if="members.length === 0" class="empty-state">Nenhum membro encontrado para esta empresa.</p>

        <ul v-else class="member-list">
          <li v-for="member in members" :key="member.userId">
            <div>
              <strong>{{ member.name }}</strong>
              <span>{{ member.email }}</span>
            </div>
            <span class="role-badge" :data-role="member.role">{{ member.role }}</span>
          </li>
        </ul>

        <form class="invite-row" @submit.prevent="handleCreateInvitation">
          <div class="invite-field">
            <BaseInput
              id="memberEmail"
              label="Email do membro"
              type="email"
              placeholder="email@dominio.com"
              v-model="newInvite.email"
              :error="errors.email"
              required
            />
          </div>

          <div class="invite-role">
            <label for="memberRole">Função</label>
            <select id="memberRole" v-model="newInvite.role">
              <option value="owner">Owner</option>
              <option value="admin">Admin</option>
              <option value="viewer">Viewer</option>
            </select>
          </div>

          <PrimaryButton type="submit" :loading="inviteLoading" :disabled="!companyStore.company.id">
            Convidar
          </PrimaryButton>
        </form>
        <p v-if="inviteError" class="error-message">{{ inviteError }}</p>

        <section class="panel" style="margin-top: 24px;">
          <header class="panel-header">
            <div>
              <h2 class="panel-title">Convites pendentes</h2>
              <p class="panel-subtitle">Gerencie convites enviados.</p>
            </div>
            <button class="ghost-button" @click="loadInvitations">Atualizar</button>
          </header>
          <p v-if="invitationsLoading" class="empty-state">Carregando convites...</p>
          <p v-else-if="invitations.length === 0" class="empty-state">Nenhum convite pendente.</p>
          <ul v-else class="member-list">
            <li v-for="invitation in invitations" :key="invitation.id">
              <div>
                <strong>{{ invitation.email }}</strong>
                <span>Função: {{ invitation.role }}</span>
                <p class="invitation-meta">Expira em: {{ formatDate(invitation.expiresAt) }}</p>
              </div>
              <button class="danger-button" @click="handleRevoke(invitation)">Revogar</button>
            </li>
          </ul>
        </section>
      </section>

      <div class="management-stack">
        <TagManager />
        <CategoryManager />
        <RecurringTransactionManager />
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useCompanyStore } from '@/stores/CompanyStore';
import CompanyService, { type CompanyRole } from '@/services/companyService';
import CategoryManager from '@/components/company/CategoryManager.vue';
import RecurringTransactionManager from '@/components/company/RecurringTransactionManager.vue';
import TagManager from '@/components/company/TagManager.vue';
import BaseInput from '@/components/ui/BaseInput.vue';
import PrimaryButton from '@/components/ui/PrimaryButton.vue';

const router = useRouter();
const companyStore = useCompanyStore();
const service = new CompanyService();

const companyName = computed(() => companyStore.company.name || 'Minha Empresa');
const membersLoading = ref(false);
const inviteLoading = ref(false);
const inviteError = ref('');

const members = ref([] as Array<{ userId: string; name: string; email: string; role: CompanyRole; createdAt: string }>);
const newInvite = reactive<{ email: string; role: CompanyRole }>({ email: '', role: 'viewer' });
const errors = reactive({ email: false });
const invitations = ref<Array<{ id: string; email: string; role: CompanyRole; expiresAt: string }>>([]);
const invitationsLoading = ref(false);

const setCompanyFromUserCompany = (userCompany: { companyId: string; companyName: string; role: string }) => {
  const safeRole: CompanyRole =
    userCompany.role === 'owner' || userCompany.role === 'admin' || userCompany.role === 'viewer'
      ? userCompany.role
      : 'viewer';

  companyStore.setCompanyData({
    id: userCompany.companyId,
    name: userCompany.companyName,
    role: safeRole,
    hasCompany: true,
  });
};

const ensureCompanyId = async () => {
  if (companyStore.company.id) return;
  try {
    const userCompanies = await service.getUserCompanies();
    if (userCompanies.length > 0) {
      setCompanyFromUserCompany(userCompanies[0]!);
    }
  } catch (error) {
    console.error('Erro ao buscar empresas do usuário:', error);
  }
};

const loadMembers = async () => {
  if (!companyStore.company.id) return;

  membersLoading.value = true;
  try {
    const response = await service.getCompanyMembers(companyStore.company.id);
    members.value = response.items;
  } catch (error) {
    console.error('Erro ao carregar membros:', error);
    members.value = [];
  } finally {
    membersLoading.value = false;
  }
};

const loadInvitations = async () => {
  if (!companyStore.company.id) return;
  invitationsLoading.value = true;
  try {
    const response = await service.listInvitations(companyStore.company.id, { limit: 50 });
    invitations.value = response.items;
  } catch (error) {
    console.error('Erro ao carregar convites:', error);
    invitations.value = [];
  } finally {
    invitationsLoading.value = false;
  }
};

const handleCreateInvitation = async () => {
  errors.email = false;
  inviteError.value = '';

  if (!newInvite.email.trim()) {
    errors.email = true;
    return;
  }

  if (!companyStore.company.id) {
    inviteError.value = 'Empresa não selecionada.';
    return;
  }

  inviteLoading.value = true;
  try {
    await service.createInvitation(companyStore.company.id, newInvite.email.trim(), newInvite.role);
    newInvite.email = '';
    newInvite.role = 'viewer';
    inviteError.value = '';
    await loadInvitations();
  } catch (error) {
    console.error('Erro ao criar convite:', error);
    const resp =
      typeof error === 'object' && error !== null && 'response' in error
        ? (error as { response?: { data?: { error?: string } } }).response?.data
        : undefined;

    if (resp?.error === 'USER_NOT_FOUND') {
      inviteError.value = 'Usuário não encontrado: peça para a pessoa se cadastrar antes de convidá-la.';
    } else if (resp?.error === 'MEMBER_ALREADY_EXISTS') {
      inviteError.value = 'Este usuário já é membro da empresa.';
    } else if (resp?.error === 'FORBIDDEN') {
      inviteError.value = 'Permissão insuficiente: apenas o owner pode convidar novos membros.';
    } else {
      inviteError.value = 'Erro ao convidar membro. Verifique o console para mais detalhes.';
    }
  } finally {
    inviteLoading.value = false;
  }
};

const handleRevoke = async (invitation: { id: string }) => {
  if (!companyStore.company.id) return;
  try {
    await service.revokeInvitation(companyStore.company.id, invitation.id);
    await loadInvitations();
  } catch (error) {
    console.error('Erro ao revogar convite:', error);
  }
};

const formatDate = (value: string) => {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString('pt-BR');
};

const leaveCompany = () => {
  companyStore.clearCompany();
  router.replace({ name: 'company' });
};

onMounted(() => {
  if (!companyStore.company.hasCompany) {
    router.replace({ name: 'company' });
  }
});

onMounted(async () => {
  if (!companyStore.company.hasCompany) return;
  await ensureCompanyId();
  await loadMembers();
  await loadInvitations();
});
</script>

<style scoped>
.settings-page {
  min-height: calc(100vh - 65px);
  padding: 48px 20px 64px;
  background: var(--color-bg);
}

.settings-container {
  max-width: 760px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  margin-bottom: 36px;
}

.identity {
  display: flex;
  align-items: center;
  gap: 18px;
  min-width: 0;
}

.avatar {
  flex-shrink: 0;
  width: 56px;
  height: 56px;
  border-radius: 14px;
  background: var(--color-success-gradient);
  color: var(--color-surface);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-display);
  font-size: 1.5rem;
  font-weight: 800;
}

.kicker {
  font-size: 12.5px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-primary);
  margin-bottom: 4px;
}

h1 {
  font-family: var(--font-display);
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--color-text);
  margin: 0;
}

.danger-button {
  flex-shrink: 0;
  padding: 12px 20px;
  border-radius: var(--radius-input);
  border: 1.5px solid var(--color-danger);
  background: transparent;
  color: var(--color-danger);
  font-family: var(--font-body);
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.2s ease, color 0.2s ease;
}

.danger-button:hover {
  background: var(--color-danger);
  color: var(--color-surface);
}

.panel {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  padding: 28px;
  margin-bottom: 20px;
}

.panel-header {
  display: flex;
  align-items: center;
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
}

.panel-subtitle {
  margin-top: 4px;
  color: var(--color-text-secondary);
  font-size: 0.9rem;
}

.field-list {
  display: flex;
  flex-direction: column;
}

.field-row {
  display: grid;
  grid-template-columns: 140px 1fr;
  gap: 20px;
  padding: 16px 0;
  border-bottom: 1px solid var(--color-border);
}

.field-row:first-child {
  border-top: 1px solid var(--color-border);
}

.field-label {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.field-value {
  font-size: 14.5px;
  color: var(--color-text);
}

.ghost-button {
  padding: 10px 18px;
  border-radius: var(--radius-input);
  font-family: var(--font-body);
  font-weight: 700;
  font-size: 13.5px;
  cursor: pointer;
  border: 1.5px solid var(--color-text-tertiary);
  background: transparent;
  color: var(--color-text-secondary);
  transition: border-color 0.2s ease, color 0.2s ease, background 0.2s ease;
  white-space: nowrap;
}

.ghost-button:hover {
  border-color: var(--color-text-secondary);
  color: var(--color-text);
  background: var(--color-surface-alt);
}

.empty-state {
  padding: 16px;
  border-radius: 12px;
  border: 1px dashed var(--color-border);
  color: var(--color-text-secondary);
  font-size: 0.9rem;
  margin-bottom: 20px;
}

.member-list {
  list-style: none;
  padding: 0;
  margin: 0 0 24px;
  display: flex;
  flex-direction: column;
}

.member-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  padding: 14px 0;
  border-bottom: 1px solid var(--color-border);
}

.member-list li:first-child {
  border-top: 1px solid var(--color-border);
}

.member-list strong {
  display: block;
  color: var(--color-text);
  font-size: 14.5px;
}

.member-list span {
  color: var(--color-text-secondary);
  font-size: 13px;
}

.role-badge {
  flex-shrink: 0;
  padding: 5px 12px;
  border-radius: 999px;
.invitation-meta {
  margin: 4px 0 0;
  font-size: 12px;
  color: var(--color-text-secondary);
}

  font-size: 12px;
  font-weight: 700;
  text-transform: capitalize;
  background: var(--color-surface-alt);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}

.role-badge[data-role='owner'] {
  background: var(--color-primary-glow);
  color: var(--color-primary);
  border-color: transparent;
}

.invite-row {
  display: flex;
  align-items: flex-end;
  gap: 16px;
  flex-wrap: wrap;
  padding-top: 20px;
  border-top: 1px solid var(--color-border);
}

.invite-field {
  flex: 1;
  min-width: 220px;
}

.invite-role {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.invite-role label {
  font-size: 0.85rem;
  color: var(--color-placeholder);
  font-weight: 600;
  margin-left: 12px;
}

select {
  min-height: 52px;
  border: 2px solid transparent;
  border-radius: var(--radius-input);
  padding: 14px 16px;
  background: var(--color-bg);
  color: var(--color-text);
  font-family: var(--font-body);
  font-size: 1rem;
}

select:focus {
  outline: none;
  border-color: var(--color-primary);
}

.error-message {
  color: var(--color-danger);
  font-size: 0.9rem;
  margin: 12px 0 0;
}

.management-stack {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Responsividade */
@media (max-width: 640px) {
  .settings-page {
    padding: 32px 16px 48px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .danger-button {
    align-self: stretch;
  }

  .panel {
    padding: 22px;
  }

  .field-row {
    grid-template-columns: 1fr;
    gap: 6px;
  }

  .invite-row {
    flex-direction: column;
    align-items: stretch;
  }

  .invite-row :deep(.primary-btn) {
    width: 100%;
  }
}
</style>
