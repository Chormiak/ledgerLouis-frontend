import type { CompanyRole } from '@/services/companyService';

export const ROLE_LABELS: Record<CompanyRole, string> = {
  owner: 'Proprietário',
  admin: 'Administrador',
  viewer: 'Leitor',
};

export const ROLE_OPTIONS = (Object.keys(ROLE_LABELS) as CompanyRole[]).map((value) => ({
  value,
  label: ROLE_LABELS[value],
}));

export const roleLabel = (role: string) => ROLE_LABELS[role as CompanyRole] ?? role;
