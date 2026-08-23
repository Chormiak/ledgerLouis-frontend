import axiosInstance from '@/plugins/axios';
import { useCompanyStore } from '@/stores/CompanyStore';

export interface TagDto {
  id: string;
  companyId: string;
  name: string;
}

export interface TransactionTagLinkDto {
  id: string;
  transactionId: string;
  tagId: string;
}

export default class TagService {
  private getCompanyId(): string {
    const companyStore = useCompanyStore();
    const companyId = companyStore.company.id;
    if (!companyId) {
      throw new Error('Nenhuma empresa selecionada');
    }
    return companyId;
  }

  async getTags(): Promise<TagDto[]> {
    const companyId = this.getCompanyId();
    const response = await axiosInstance.get<TagDto[]>(`/companies/${companyId}/tags`);
    return response.data;
  }

  async getTag(id: string): Promise<TagDto> {
    const companyId = this.getCompanyId();
    const response = await axiosInstance.get<TagDto>(`/companies/${companyId}/tags/${id}`);
    return response.data;
  }

  async createTag(name: string): Promise<TagDto> {
    const companyId = this.getCompanyId();
    const response = await axiosInstance.post<TagDto>(`/companies/${companyId}/tags`, { name });
    return response.data;
  }

  async updateTag(id: string, name: string): Promise<TagDto> {
    const companyId = this.getCompanyId();
    const response = await axiosInstance.patch<TagDto>(`/companies/${companyId}/tags/${id}`, { name });
    return response.data;
  }

  async deleteTag(id: string): Promise<void> {
    const companyId = this.getCompanyId();
    await axiosInstance.delete(`/companies/${companyId}/tags/${id}`);
  }

  async getTransactionTags(transactionId: string): Promise<TagDto[]> {
    const companyId = this.getCompanyId();
    const response = await axiosInstance.get<TagDto[]>(
      `/companies/${companyId}/transactions/${transactionId}/tags`,
    );
    return response.data;
  }

  async attachTag(transactionId: string, tagId: string): Promise<TransactionTagLinkDto> {
    const companyId = this.getCompanyId();
    const response = await axiosInstance.post<TransactionTagLinkDto>(
      `/companies/${companyId}/transactions/${transactionId}/tags`,
      { tagId },
    );
    return response.data;
  }

  async detachTag(transactionId: string, tagId: string): Promise<void> {
    const companyId = this.getCompanyId();
    await axiosInstance.delete(`/companies/${companyId}/transactions/${transactionId}/tags/${tagId}`);
  }
}
