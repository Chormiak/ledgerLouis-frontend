import { Home, Layers, PieChart, Settings, TrendingUp } from 'lucide-vue-next';
import type { Component } from 'vue';

export interface NavItem {
  name: string;
  /** App servido fora do roteador (ex.: /investimentos/): vira um <a> comum em vez de RouterLink. */
  href?: string;
  label: string;
  icon: Component;
  /** Outras rotas que também deixam este item ativo. */
  matches?: string[];
}

/** Itens de navegação principal, compartilhados pela sidebar (desktop) e bottom nav (mobile). */
export const mainNav: NavItem[] = [
  { name: 'home', label: 'Início', icon: Home },
  {
    name: 'companySettings',
    label: 'Gerenciamento',
    icon: Layers,
    matches: ['company', 'companyCreate', 'recurring', 'tags'],
  },
  { name: 'reports', label: 'Relatórios', icon: PieChart, matches: ['transactions'] },
  { name: 'investimentos', href: '/investimentos/', label: 'Investimentos', icon: TrendingUp },
  { name: 'settings', label: 'Configurações', icon: Settings },
];

export const isNavItemActive = (item: NavItem, routeName: unknown) =>
  routeName === item.name || (typeof routeName === 'string' && !!item.matches?.includes(routeName));
