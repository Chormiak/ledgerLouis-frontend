import axiosInstance from '@/plugins/axios';
import { useCompanyStore } from '@/stores/CompanyStore';

export interface MonthlyPointDto {
  period: string;
  total: number;
}

export interface ExpenseStatsDto {
  tagId: string | null;
  tagName: string | null;
  months: MonthlyPointDto[];
  count: number;
  mean: number;
  variance: number;
  standardDeviation: number;
  forecastNextMonth: number | null;
}

export interface ExpenseStatsByTagDto extends ExpenseStatsDto {
  tagId: string;
  tagName: string;
}

export default class AnalyticsService {
  private getCompanyId(): string {
    const companyStore = useCompanyStore();
    const companyId = companyStore.company.id;
    if (!companyId) {
      throw new Error('Nenhuma empresa selecionada');
    }
    return companyId;
  }

  async getExpenseStats(tagId?: string): Promise<ExpenseStatsDto> {
    const companyId = this.getCompanyId();
    const response = await axiosInstance.get<ExpenseStatsDto>(
      `/companies/${companyId}/analytics/expenses`,
      { params: tagId ? { tagId } : undefined },
    );
    return response.data;
  }

  async getExpenseStatsByTag(): Promise<ExpenseStatsByTagDto[]> {
    const companyId = this.getCompanyId();
    const response = await axiosInstance.get<ExpenseStatsByTagDto[]>(
      `/companies/${companyId}/analytics/expenses/by-tag`,
    );
    return response.data;
  }
}
