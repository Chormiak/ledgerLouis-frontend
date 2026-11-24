<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useCompanyStore } from '@/stores/CompanyStore';
import CompanyService, { type CompanyRole } from '@/services/companyService';
import CompanyHeader from '@/components/company/CompanyHeader.vue';
import CompanyDetails from '@/components/company/CompanyDetails.vue';
import CompanyShortcuts from '@/components/company/CompanyShortcuts.vue';
import MemberList, { type Member } from '@/components/company/MemberList.vue';
import InviteForm from '@/components/company/InviteForm.vue';
import InvitationList, { type Invitation } from '@/components/company/InvitationList.vue';
import { useToast } from '@/composables/useToast';
import { useConfirm } from '@/composables/useConfirm';
import { apiErrorCode } from '@/utils/apiError';

const router = useRouter();
const companyStore = useCompanyStore();
const service = new CompanyService();
const toast = useToast();
const { confirm } = useConfirm();

const companyName = computed(() => companyStore.company.name || 'Minha empresa');

const members = ref<Member[]>([]);
const membersLoading = ref(false);
const invitations = ref<Invitation[]>([]);
const invitationsLoading = ref(false);

const inviteForm = ref<InstanceType<typeof InviteForm>>();
const inviteError = ref('');
const inviteLoading = ref(false);

const inviteErrorMessages: Record<string, string> = {
  USER_NOT_FOUND: 'Usuário não encontrado. Peça para a pessoa se cadastrar antes de convidá-la.',
  MEMBER_ALREADY_EXISTS: 'Este usuário já é membro da empresa.',
  FORBIDDEN: 'Permissão insuficiente: apenas o proprietário pode convidar novos membros.',
};

const ensureCompanyId = async () => {
  if (companyStore.company.id) return;
  try {
    const userCompanies = await service.getUserCompanies();
    if (userCompanies.length > 0) companyStore.selectCompany(userCompanies[0]!);
  } catch (error) {
    console.error('Erro ao buscar empresas do usuário:', error);
  }
};

const loadMembers = async () => {
  if (!companyStore.company.id) return;
  membersLoading.value = true;
  try {
    members.value = (await service.getCompanyMembers(companyStore.company.id)).items;
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
    invitations.value = (await service.listInvitations(companyStore.company.id, { limit: 50 })).items;
  } catch (error) {
    console.error('Erro ao carregar convites:', error);
    invitations.value = [];
  } finally {
    invitationsLoading.value = false;
  }
};

const handleInvite = async ({ email, role }: { email: string; role: CompanyRole }) => {
  inviteError.value = '';
  if (!companyStore.company.id) {
    inviteError.value = 'Empresa não selecionada.';
    return;
  }

  inviteLoading.value = true;
  try {
    await service.createInvitation(companyStore.company.id, email, role);
    inviteForm.value?.reset();
    toast.success(`Convite enviado para ${email}.`);
    await loadInvitations();
  } catch (error) {
    console.error('Erro ao criar convite:', error);
    inviteError.value = inviteErrorMessages[apiErrorCode(error) ?? ''] ?? 'Não foi possível enviar o convite.';
  } finally {
    inviteLoading.value = false;
  }
};

const handleRevoke = async (invitation: Invitation) => {
  if (!companyStore.company.id) return;
  const confirmed = await confirm({
    title: 'Revogar convite?',
    message: `${invitation.email} não poderá mais usar este convite para entrar na empresa.`,
    confirmLabel: 'Revogar',
    tone: 'danger',
  });
  if (!confirmed) return;

  try {
    await service.revokeInvitation(companyStore.company.id, invitation.id);
    toast.success('Convite revogado.');
    await loadInvitations();
  } catch (error) {
    console.error('Erro ao revogar convite:', error);
    toast.error('Não foi possível revogar o convite.');
  }
};

const leaveCompany = async () => {
  const confirmed = await confirm({
    title: 'Sair desta empresa?',
    message: 'Você voltará para a tela de seleção de empresas.',
    confirmLabel: 'Sair',
    tone: 'danger',
  });
  if (!confirmed) return;

  companyStore.clearCompany();
  router.replace({ name: 'company' });
};

onMounted(async () => {
  await ensureCompanyId();
  await Promise.all([loadMembers(), loadInvitations()]);
});
</script>

<template>
  <div class="page">
    <div class="page-shell company-shell">
      <CompanyHeader :name="companyName" :role="companyStore.company.role" @leave="leaveCompany" />

      <div class="layout">
        <div class="layout-main">
          <MemberList :members="members" :loading="membersLoading" @refresh="loadMembers">
            <InviteForm
              ref="inviteForm"
              :loading="inviteLoading"
              :error="inviteError"
              :disabled="!companyStore.company.id"
              @submit="handleInvite"
            />
          </MemberList>

          <InvitationList
            :invitations="invitations"
            :loading="invitationsLoading"
            @refresh="loadInvitations"
            @revoke="handleRevoke"
          />
        </div>

        <aside class="layout-rail">
          <CompanyDetails
            :name="companyStore.company.name"
            :cnpj="companyStore.company.cnpj"
            :email="companyStore.company.email"
            :phone="companyStore.company.phone"
          />
          <CompanyShortcuts />
        </aside>
      </div>
    </div>
  </div>
</template>

<style scoped>
.company-shell {
  max-width: 1080px;
  gap: var(--space-6);
}

.layout {
  display: grid;
  gap: var(--space-4);
  align-items: start;
}

.layout-main,
.layout-rail {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  min-width: 0;
}

@media (min-width: 960px) {
  .layout {
    grid-template-columns: minmax(0, 1fr) 340px;
  }

  /* trilho lateral acompanha a rolagem enquanto as listas crescem */
  .layout-rail {
    position: sticky;
    top: calc(var(--topbar-height) + var(--space-4));
  }
}
</style>
