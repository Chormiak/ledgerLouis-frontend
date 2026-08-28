import axiosInstance from '@/plugins/axios';
import { useCompanyStore } from '@/stores/CompanyStore';

export type RecurringFrequency = 'weekly' | 'monthly' | 'yearly';
export type RecurringStatus = 'active' | 'paused' | 'finished';
export type RecurringEntryType = 'debit' | 'credit';

export interface RecurringTransactionDto {
  id: string;
  companyId: string;
  description: string | null;
  amount: number;
  entryType: RecurringEntryType;
  frequency: RecurringFrequency;
  intervalValue: number | null;
  startDate: string;
  endDate: string | null;
  nextRunDate: string;
  lastRunDate: string | null;
  status: RecurringStatus;
}

export interface CreateRecurringTransactionDto {
  description?: string;
  amount: number;
  entryType: RecurringEntryType;
  frequency: RecurringFrequency;
  intervalValue?: number;
  startDate: string;
  endDate?: string;
}

export interface UpdateRecurringTransactionDto {
  description?: string;
  amount?: number;
  entryType?: RecurringEntryType;
  frequency?: RecurringFrequency;
  intervalValue?: number;
  endDate?: string;
  status?: RecurringStatus;
}

export interface RunRecurringTransactionDto {
  id: string;
  created: number;
  status: RecurringStatus;
  nextRunDate: string;
}

export default class RecurringTransactionService {
  private getCompanyId(): string {
    const companyStore = useCompanyStore();
    const companyId = companyStore.company.id;
    if (!companyId) {
      throw new Error('Nenhuma empresa selecionada');
    }
    return companyId;
  }

  async getRecurringTransactions(): Promise<RecurringTransactionDto[]> {
    const companyId = this.getCompanyId();
    const response = await axiosInstance.get<RecurringTransactionDto[]>(
      `/companies/${companyId}/recurring-transactions`,
    );
    return response.data;
  }

  async getRecurringTransaction(id: string): Promise<RecurringTransactionDto> {
    const companyId = this.getCompanyId();
    const response = await axiosInstance.get<RecurringTransactionDto>(
      `/companies/${companyId}/recurring-transactions/${id}`,
    );
    return response.data;
  }

  async createRecurringTransaction(
    data: CreateRecurringTransactionDto,
  ): Promise<RecurringTransactionDto> {
    const companyId = this.getCompanyId();
    const response = await axiosInstance.post<RecurringTransactionDto>(
      `/companies/${companyId}/recurring-transactions`,
      data,
    );
    return response.data;
  }

  async updateRecurringTransaction(
    id: string,
    data: UpdateRecurringTransactionDto,
  ): Promise<RecurringTransactionDto> {
    const companyId = this.getCompanyId();
    const response = await axiosInstance.patch<RecurringTransactionDto>(
      `/companies/${companyId}/recurring-transactions/${id}`,
      data,
    );
    return response.data;
  }

  async deleteRecurringTransaction(id: string): Promise<void> {
    const companyId = this.getCompanyId();
    await axiosInstance.delete(`/companies/${companyId}/recurring-transactions/${id}`);
  }

  async runNow(id: string): Promise<RunRecurringTransactionDto> {
    const companyId = this.getCompanyId();
    const response = await axiosInstance.post<RunRecurringTransactionDto>(
      `/companies/${companyId}/recurring-transactions/${id}/run`,
    );
    return response.data;
  }
}
