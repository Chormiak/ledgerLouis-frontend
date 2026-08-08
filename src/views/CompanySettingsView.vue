<template>
  <main class="company-admin-page">
    <div class="page-inner">
    <!-- Header da Página -->
    <div class="admin-header">
      <div class="header-content">
        <div class="avatar-large">{{ companyName.charAt(0).toUpperCase() }}</div>
        <div>
          <h1>{{ companyName }}</h1>
          <p>Painel de Administração da Empresa</p>
        </div>
      </div>
      <button class="btn-leave" @click="leaveCompany">Sair da Empresa</button>
    </div>

    <!-- Informações da Empresa -->
    <section class="info-section">
      <h3>📋 Informações da Empresa</h3>
      <div class="info-grid">
        <div class="info-item">
          <label>Nome</label>
          <span>{{ companyStore.company.name }}</span>
        </div>
        <div class="info-item">
          <label>CNPJ</label>
          <span>{{ companyStore.company.cnpj || 'Não informado' }}</span>
        </div>
        <div class="info-item">
          <label>Email</label>
          <span>{{ companyStore.company.email || 'Não informado' }}</span>
        </div>
        <div class="info-item">
          <label>Telefone</label>
          <span>{{ companyStore.company.phone || 'Não informado' }}</span>
        </div>
        <div class="info-item">
          <label>Endereço</label>
          <span>{{ companyStore.company.address || 'Não informado' }}</span>
        </div>
        <div class="info-item">
          <label>Site</label>
          <span>{{ companyStore.company.website || 'Não informado' }}</span>
        </div>
      </div>
    </section>

    <section class="members-section">
      <header class="members-header">
        <div>
          <h3>👥 Membros da Empresa</h3>
          <p class="members-subtitle">Convide e acompanhe quem faz parte da sua empresa.</p>
        </div>
        <button class="secondary-button" @click="loadMembers">Atualizar</button>
      </header>

      <div v-if="membersLoading" class="empty-members">
        <p>Carregando membros...</p>
      </div>

      <div v-else-if="members.length === 0" class="empty-members">
        <p>Nenhum membro encontrado para esta empresa.</p>
      </div>

      <ul class="members-list" v-else>
        <li v-for="member in members" :key="member.userId">
          <div>
            <strong>{{ member.name }}</strong>
            <span>{{ member.email }}</span>
          </div>
          <span class="member-role">{{ member.role }}</span>
        </li>
      </ul>

      <section class="invite-card">
        <h4>Convidar novo membro</h4>
        <form @submit.prevent="handleAddMember" class="invite-form">
          <BaseInput
            id="memberEmail"
            label="Email do membro"
            type="email"
            placeholder="email@dominio.com"
            v-model="newMember.email"
            :error="errors.email"
            required
          />

          <label class="select-label" for="memberRole">Função</label>
          <select id="memberRole" v-model="newMember.role">
            <option value="owner">Owner</option>
            <option value="admin">Admin</option>
            <option value="viewer">Viewer</option>
          </select>

          <div class="form-actions">
            <button type="submit" class="primary-button" :disabled="inviteLoading || !companyStore.company.id">
              {{ inviteLoading ? 'Enviando...' : 'Convidar membro' }}
            </button>
          </div>
          <p v-if="inviteError" class="error-message">{{ inviteError }}</p>
        </form>
      </section>
    </section>

    <!-- Componentes de Gerenciamento -->
    <div class="management-container">
      <CategoryManager />
      <RecurringExpenseManager />
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
import RecurringExpenseManager from '@/components/company/RecurringExpenseManager.vue';
import BaseInput from '@/components/ui/BaseInput.vue';

const router = useRouter();
const companyStore = useCompanyStore();
const service = new CompanyService();

const companyName = computed(() => companyStore.company.name || 'Minha Empresa');
const membersLoading = ref(false);
const inviteLoading = ref(false);
const inviteError = ref('');

const members = ref([] as Array<{ userId: string; name: string; email: string; role: CompanyRole; createdAt: string }>);
const newMember = reactive<{ email: string; role: CompanyRole }>({ email: '', role: 'viewer' });
const errors = reactive({ email: false });

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

const handleAddMember = async () => {
  errors.email = false;
  inviteError.value = '';

  if (!newMember.email.trim()) {
    errors.email = true;
    return;
  }

  if (!companyStore.company.id) {
    inviteError.value = 'Empresa não selecionada.';
    return;
  }

  inviteLoading.value = true;
  try {
    await service.addCompanyMember(companyStore.company.id, newMember.email.trim(), newMember.role);
    companyStore.addMember(newMember.email.trim());
    newMember.email = '';
    newMember.role = 'viewer';
    await loadMembers();
  } catch (error) {
    console.error('Erro ao adicionar membro:', error);
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
});
</script>

<style scoped>
.company-admin-page {
  min-height: calc(100vh - 65px);
  padding: 32px 20px;
  background-color: var(--color-surface-soft);
}

.page-inner {
  max-width: 1200px;
  margin: 0 auto;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding: 24px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.header-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.avatar-large {
  width: 80px;
  height: 80px;
  border-radius: 12px;
  background: var(--color-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: 800;
}

.header-content h1 {
  margin: 0 0 8px 0;
  font-size: 2rem;
  color: var(--color-primary);
}

.header-content p {
  margin: 0;
  color: var(--color-text-secondary);
}

.btn-leave {
  background: #ff4444;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
  white-space: nowrap;
}

.btn-leave:hover {
  background: #dd3333;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 68, 68, 0.3);
}

.info-section {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 32px;
}

.members-section {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 32px;
}

.members-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.members-header h3 {
  margin: 0;
  font-size: 1.2rem;
  color: var(--color-primary);
}

.members-subtitle {
  margin-top: 6px;
  color: var(--color-text-secondary);
  font-size: 0.92rem;
}

.members-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 12px;
  margin-bottom: 20px;
}

.members-list li {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding: 14px 18px;
  border-radius: 12px;
  border: 1px solid var(--color-border);
  background: var(--color-surface-alt);
}

.members-list strong {
  display: block;
  margin-bottom: 4px;
  color: var(--color-text);
}

.members-list span {
  color: var(--color-text-secondary);
  font-size: 0.9rem;
}

.member-role {
  font-weight: 700;
  color: var(--color-success-dark) !important;
  text-transform: capitalize;
}

.invite-card {
  margin-top: 10px;
  padding: 18px;
  border-radius: 12px;
  border: 1px solid var(--color-border);
  background: var(--color-surface-alt);
}

.invite-card h4 {
  margin: 0 0 14px;
  color: var(--color-text);
}

.invite-form {
  display: grid;
  gap: 14px;
}

.select-label {
  color: var(--color-text);
  font-weight: 600;
}

select {
  width: 100%;
  min-height: 46px;
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 10px 12px;
  background: var(--color-surface);
  color: var(--color-text);
}

.form-actions {
  display: flex;
  justify-content: flex-start;
}

.error-message {
  color: var(--color-danger);
  font-weight: 600;
}

.empty-members {
  padding: 14px;
  border-radius: 10px;
  border: 1px solid var(--color-border);
  background: var(--color-surface-alt);
  margin-bottom: 16px;
}

.primary-button,
.secondary-button {
  border-radius: 999px;
  padding: 10px 16px;
  cursor: pointer;
  font-weight: 700;
}

.primary-button {
  border: none;
  background: var(--color-success-gradient);
  color: var(--color-surface);
}

.secondary-button {
  border: 1px solid var(--color-success-dark);
  background: transparent;
  color: var(--color-success-dark);
}

.info-section h3 {
  margin: 0 0 20px 0;
  font-size: 1.2rem;
  color: var(--color-primary);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  padding: 12px;
  background: var(--color-bg);
  border-radius: 8px;
  border: 1px solid var(--color-border);
}

.info-item label {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  margin-bottom: 6px;
  text-transform: uppercase;
}

.info-item span {
  font-size: 0.95rem;
  color: var(--color-text);
  margin: 0;
}

.management-container {
  max-width: 1200px;
  margin: 0 auto;
}

/* Responsividade */
@media (max-width: 768px) {
  .company-admin-page {
    padding: 20px 16px;
  }

  .admin-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .btn-leave {
    align-self: flex-start;
  }

  .header-content h1 {
    font-size: 1.5rem;
  }

  .avatar-large {
    width: 60px;
    height: 60px;
    font-size: 1.5rem;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .members-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .members-list li {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 480px) {
  .header-content h1 {
    font-size: 1.3rem;
  }

  .avatar-large {
    width: 50px;
    height: 50px;
    font-size: 1.2rem;
  }
}
</style>
