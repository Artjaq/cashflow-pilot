import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { title: 'Tableau de bord' },
  },
  {
    path: '/transactions',
    name: 'transactions',
    component: () => import('@/views/TransactionsView.vue'),
    meta: { title: 'Transactions' },
  },
  {
    path: '/treasury',
    name: 'treasury',
    component: () => import('@/views/TreasuryView.vue'),
    meta: { title: 'Trésorerie' },
  },
  {
    path: '/payment-plans',
    name: 'payment-plans',
    component: () => import('@/views/PaymentPlansView.vue'),
    meta: { title: 'Plans de paiement' },
  },
  {
    path: '/budgets',
    name: 'budgets',
    component: () => import('@/views/BudgetsView.vue'),
    meta: { title: 'Budgets' },
  },
  {
    path: '/categories',
    name: 'categories',
    component: () => import('@/views/CategoriesView.vue'),
    meta: { title: 'Catégories' },
  },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
