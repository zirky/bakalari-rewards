import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/login' },
    { path: '/login', component: () => import('../views/LoginView.vue') },
    {
      path: '/parent',
      meta: { requiresAuth: true, role: 'parent' },
      children: [
        { path: 'dashboard', component: () => import('../views/parent/DashboardView.vue') },
        { path: 'payouts',   component: () => import('../views/parent/PayoutsView.vue') },
        { path: 'settings',  component: () => import('../views/parent/SettingsView.vue') },
        { path: 'audit',     component: () => import('../views/parent/AuditLogView.vue') },
      ]
    },
    {
      path: '/child',
      meta: { requiresAuth: true, role: 'child' },
      children: [
        { path: 'dashboard', component: () => import('../views/child/DashboardView.vue') },
        { path: 'history',   component: () => import('../views/child/HistoryView.vue') },
      ]
    },
  ]
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.token) return '/login'
})

export default router
