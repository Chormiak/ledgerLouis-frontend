import axiosInstance from '@/plugins/axios';

export type CompanyRole = 'owner' | 'admin' | 'viewer';

export interface UserCompanyDto {
  companyId: string;
  companyName: string;
  role: CompanyRole;
  createdAt: string;
}

export interface CompanyMemberDto {
  userId: string;
  name: string;
  email: string;
  role: CompanyRole;
  createdAt: string;
}

interface MembersListResponse {
  items: CompanyMemberDto[];
  total: number;
  limit: number;
  offset: number;
}

interface AddMemberResponse {
  targetUserId: string;
  companyId: string;
  role: CompanyRole;
}

export interface CompanyDto {
  id: string;
  name: string;
  cnpj: string;
}

export default class CompanyService {
  async createCompany(name: string, cnpj: string): Promise<CompanyDto> {
    const response = await axiosInstance.post<CompanyDto>('/companies', { name, cnpj });
    return response.data;
  }

  async getUserCompanies(): Promise<UserCompanyDto[]> {
    const response = await axiosInstance.get<UserCompanyDto[]>('/me/companies');
    return response.data;
  }

  async getCompanyMembers(
    companyId: string,
    options?: { limit?: number; offset?: number },
  ): Promise<MembersListResponse> {
    const response = await axiosInstance.get<MembersListResponse>(`/companies/${companyId}/members`, {
      params: {
        limit: options?.limit,
        offset: options?.offset,
      },
    });

    return response.data;
  }

  async addCompanyMember(
    companyId: string,
    email: string,
    role: CompanyRole,
  ): Promise<AddMemberResponse> {
    const response = await axiosInstance.post<AddMemberResponse>(`/companies/${companyId}/members`, {
      email,
      role,
    });

    return response.data;
  }
}
