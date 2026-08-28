import axiosInstance from '@/plugins/axios';
import { useCompanyStore } from '@/stores/CompanyStore';

export type TransactionEntryType = 'debit' | 'credit';

export interface TransactionDto {
  id: string;
  amount: number;
  description: string;
  entryType: TransactionEntryType;
  date: string;
  companyId: string;
  projectId?: string | null;
}

export interface CreateTransactionDto {
  amount: number;
  description: string;
  entryType: TransactionEntryType;
  date: string;
  projectId?: string;
}

export interface AccountValueResponse {
  value: number;
}

export default class TransactionService {
  private getCompanyId(): string {
    const companyStore = useCompanyStore();
    const companyId = companyStore.company.id;
    if (!companyId) {
      throw new Error('Nenhuma empresa selecionada');
    }
    return companyId;
  }

  async getTransactions(): Promise<TransactionDto[]> {
    const companyId = this.getCompanyId();
    const response = await axiosInstance.get<TransactionDto[]>(`/companies/${companyId}/transactions`);
    return response.data;
  }

  async getTransaction(id: string): Promise<TransactionDto> {
    const companyId = this.getCompanyId();
    const response = await axiosInstance.get<TransactionDto>(`/companies/${companyId}/transactions/${id}`);
    return response.data;
  }

  async createTransaction(data: CreateTransactionDto): Promise<TransactionDto> {
    const companyId = this.getCompanyId();
    const response = await axiosInstance.post<TransactionDto>(`/companies/${companyId}/transactions`, data);
    return response.data;
  }

  async deleteTransaction(id: string): Promise<void> {
    const companyId = this.getCompanyId();
    await axiosInstance.delete(`/companies/${companyId}/transactions/${id}`);
  }

  async getAccountValue(): Promise<number> {
    const companyId = this.getCompanyId();
    const response = await axiosInstance.get<AccountValueResponse>(`/companies/${companyId}/accountValue`);
    return response.data.value;
  }
}