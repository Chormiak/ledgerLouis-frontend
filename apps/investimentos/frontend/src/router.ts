import { createRouter, createWebHistory } from 'vue-router'
import OverviewView from './views/OverviewView.vue'

// Cada tela baixa só o próprio código; a visão geral vem junto por ser a primeira.
export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: OverviewView, meta: { title: 'Visão geral' } },
    { path: '/grupos', component: () => import('./views/GroupsView.vue'), meta: { title: 'Setores e nichos' } },
    { path: '/mercado-eua', component: () => import('./views/MercadoEuaView.vue'), meta: { title: 'Mercado EUA' } },
    { path: '/grupos/:kind(sector|niche)/:slug', component: () => import('./views/GroupView.vue'), props: true },
    { path: '/acoes/:ticker', component: () => import('./views/AssetView.vue'), props: true },
    { path: '/carteira', component: () => import('./views/CarteiraView.vue'), meta: { title: 'Carteira' } },
    { path: '/carteira/propostas/:id(\\d+)', component: () => import('./views/ProposalView.vue'), props: true, meta: { title: 'Proposta' } },
    { path: '/alertas', component: () => import('./views/AlertsView.vue'), meta: { title: 'Alertas' } },
    { path: '/placar', component: () => import('./views/ScoreboardView.vue'), meta: { title: 'Placar' } },
  ],
  scrollBehavior: () => ({ top: 0 }),
})

router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} | LedgerLouis` : 'LedgerLouis'
})
