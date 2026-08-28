import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { ExpenseStatsDto, ExpenseStatsByTagDto } from '@/services/analyticsService';
import AnalyticsService from '@/services/analyticsService';

export const useAnalyticsStore = defineStore('analytics', () => {
  const overallStats = ref<ExpenseStatsDto | null>(null);
  const byTagStats = ref<ExpenseStatsByTagDto[]>([]);
  const groupByTag = ref(false);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const setLoading = (value: boolean) => {
    loading.value = value;
  };

  const setError = (message: string | null) => {
    error.value = message;
  };

  const fetchOverallStats = async () => {
    try {
      setLoading(true);
      setError(null);
      const service = new AnalyticsService();
      overallStats.value = await service.getExpenseStats();
    } catch (err) {
      console.error('Erro ao buscar estatísticas de gastos:', err);
      setError('Erro ao carregar estatísticas');
    } finally {
      setLoading(false);
    }
  };

  const fetchByTagStats = async () => {
    try {
      setLoading(true);
      setError(null);
      const service = new AnalyticsService();
      byTagStats.value = await service.getExpenseStatsByTag();
    } catch (err) {
      console.error('Erro ao buscar estatísticas por tag:', err);
      setError('Erro ao carregar estatísticas por tag');
    } finally {
      setLoading(false);
    }
  };

  const setGroupByTag = async (value: boolean) => {
    groupByTag.value = value;
    if (value) {
      if (byTagStats.value.length === 0) await fetchByTagStats();
    } else {
      if (!overallStats.value) await fetchOverallStats();
    }
  };

  const clearAnalytics = () => {
    overallStats.value = null;
    byTagStats.value = [];
    groupByTag.value = false;
    error.value = null;
  };

  return {
    overallStats,
    byTagStats,
    groupByTag,
    loading,
    error,
    fetchOverallStats,
    fetchByTagStats,
    setGroupByTag,
    clearAnalytics,
  };
});
