import { defineStore } from 'pinia';
import { reactive } from 'vue';
import CompanyService from '@/services/companyService';

const STORAGE_KEY = 'ledger_company_data';

export const useCompanyStore = defineStore('company', () => {
  const defaultCompany = {
    id: '',
    role: 'viewer' as 'owner' | 'admin' | 'viewer',
    name: '',
    cnpj: '',
    address: '',
    email: '',
    website: '',
    phone: '',
    owner: '',
    members: [] as string[],
    hasCompany: false,
  };

  const company = reactive({
    ...defaultCompany,
  });

  // Carregar dados do localStorage na inicialização
  const loadCompanyData = () => {
    try {
      const savedData = localStorage.getItem(STORAGE_KEY);
      if (savedData) {
        const parsedData = JSON.parse(savedData);
        Object.assign(company, parsedData);
      }
    } catch (error) {
      console.error('Erro ao carregar dados da empresa:', error);
    }
  };

  const setCompanyData = (companyData: Partial<typeof company>) => {
    Object.assign(company, companyData);
    // Persistir em localStorage
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(company));
    } catch (error) {
      console.error('Erro ao salvar dados da empresa:', error);
    }
  };

  const addMember = (member: string) => {
    if (member && !company.members.includes(member)) {
      company.members.push(member);
      // Persistir em localStorage
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(company));
      } catch (error) {
        console.error('Erro ao salvar dados da empresa:', error);
      }
    }
  };

  const clearCompany = () => {
    Object.assign(company, defaultCompany);
    // Limpar localStorage
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (error) {
      console.error('Erro ao limpar dados da empresa:', error);
    }
  };

  const syncFromBackend = async () => {
    try {
      const service = new CompanyService();
      const userCompanies = await service.getUserCompanies();
      if (userCompanies.length === 0) return;

      const current = userCompanies.find((c) => c.companyId === company.id) ?? userCompanies[0]!;
      const safeRole =
        current.role === 'owner' || current.role === 'admin' || current.role === 'viewer'
          ? current.role
          : 'viewer';

      setCompanyData({
        id: current.companyId,
        name: current.companyName,
        role: safeRole,
        hasCompany: true,
      });
    } catch (error) {
      console.error('Erro ao sincronizar empresa com backend:', error);
    }
  };

  return {
    company,
    setCompanyData,
    addMember,
    clearCompany,
    loadCompanyData,
    syncFromBackend,
  };
});
