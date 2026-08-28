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
        <PrimaryButton variant="danger" compact @click="leaveCompany">
          <LogOut :size="15" />
          Sair da empresa
        </PrimaryButton>
      </header>

      <section class="panel">
        <h2 class="panel-title">
          <Building2 :size="18" />
          Dados da empresa
        </h2>

        <div class="info-grid">
          <div class="info-tile">
            <div class="info-icon"><Building2 :size="16" /></div>
            <div>
              <span class="info-label">Nome</span>
              <strong class="info-value">{{ companyStore.company.name || 'Não informado' }}</strong>
            </div>
          </div>

          <div class="info-tile">
            <div class="info-icon"><Fingerprint :size="16" /></div>
            <div>
              <span class="info-label">CNPJ</span>
              <strong class="info-value">{{ companyStore.company.cnpj || 'Não informado' }}</strong>
            </div>
          </div>

          <div class="info-tile">
            <div class="info-icon"><Mail :size="16" /></div>
            <div>
              <span class="info-label">Email</span>
              <strong class="info-value">{{ companyStore.company.email || 'Não informado' }}</strong>
            </div>
          </div>

          <div class="info-tile">
            <div class="info-icon"><Phone :size="16" /></div>
            <div>
              <span class="info-label">Telefone</span>
              <strong class="info-value">{{ companyStore.company.phone || 'Não informado' }}</strong>
            </div>
          </div>
        </div>
      </section>

      <section class="panel">
        <header class="panel-header">
          <div>
            <h2 class="panel-title">
              <Users :size="18" />
              Membros
            </h2>
            <p class="panel-subtitle">Convide e acompanhe quem faz parte da sua empresa.</p>
          </div>
          <PrimaryButton variant="neutral" compact @click="loadMembers">
            <RefreshCw :size="14" />
            Atualizar
          </PrimaryButton>
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
      </section>

      <section class="panel">
        <header class="panel-header">
          <div>
            <h2 class="panel-title">
              <MailCheck :size="18" />
              Convites pendentes
            </h2>
            <p class="panel-subtitle">Gerencie convites enviados.</p>
          </div>
          <PrimaryButton variant="neutral" compact @click="loadInvitations">
            <RefreshCw :size="14" />
            Atualizar
          </PrimaryButton>
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
            <PrimaryButton variant="danger" compact @click="handleRevoke(invitation)">Revogar</PrimaryButton>
          </li>
        </ul>
      </section>

      <section class="management-section">
        <header class="section-header">
          <div class="section-icon"><SlidersHorizontal :size="18" /></div>
          <div>
            <h2 class="section-title">Gerenciamento</h2>
            <p class="section-subtitle">Organize tags e configure lançamentos que se repetem automaticamente.</p>
          </div>
        </header>

        <div class="management-stack">
          <TagManager />
          <RecurringTransactionManager />
        </div>
      </section>
    </div>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { LogOut, RefreshCw, Building2, Fingerprint, Mail, Phone, Users, MailCheck, SlidersHorizontal } from 'lucide-vue-next';
import { useCompanyStore } from '@/stores/CompanyStore';
import CompanyService, { type CompanyRole } from '@/services/companyService';
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
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
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

.panel {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  padding: 28px;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: var(--font-display);
  font-size: 1.1rem;
  font-weight: 800;
  color: var(--color-text);
  margin: 0 0 18px;
}

.panel-header .panel-title {
  margin: 0;
}

.panel-title svg {
  color: var(--color-primary);
  flex-shrink: 0;
}

.panel-subtitle {
  margin-top: 4px;
  color: var(--color-text-secondary);
  font-size: 0.9rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.info-tile {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  border-radius: 14px;
  background: var(--color-surface-soft);
  min-width: 0;
}

.info-icon {
  flex-shrink: 0;
  width: 34px;
  height: 34px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary-glow);
  color: var(--color-primary);
}

.info-label {
  display: block;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-text-secondary);
  margin-bottom: 4px;
}

.info-value {
  display: block;
  font-size: 14.5px;
  font-weight: 700;
  color: var(--color-text);
  overflow-wrap: anywhere;
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

.member-list:last-child {
  margin-bottom: 0;
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

.invitation-meta {
  margin: 4px 0 0;
  font-size: 12px;
  color: var(--color-text-secondary);
}

.role-badge {
  flex-shrink: 0;
  padding: 5px 12px;
  border-radius: 999px;
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

.management-section {
  border-radius: 20px;
  padding: 24px;
  background: linear-gradient(180deg, var(--color-primary-glow) 0%, transparent 140px);
  border: 1px solid var(--color-border);
}

.section-header {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  margin-bottom: 20px;
}

.section-icon {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-success-gradient);
  color: white;
}

.section-title {
  font-family: var(--font-display);
  font-size: 1.2rem;
  font-weight: 800;
  color: var(--color-text);
}

.section-subtitle {
  margin-top: 4px;
  color: var(--color-text-secondary);
  font-size: 0.9rem;
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

  .page-header :deep(.primary-btn) {
    align-self: stretch;
  }

  .panel {
    padding: 22px;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .management-section {
    padding: 18px;
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
