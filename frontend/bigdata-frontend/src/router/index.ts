import { createRouter, createWebHistory } from 'vue-router'
import { ROUTES, STORAGE_KEYS } from '@/constants'
import Login from '@/views/Login.vue'
import MainLayout from '@/layouts/MainLayout.vue'
import Dashboard from '@/views/Dashboard.vue'
import UserManagement from '@/views/UserManagement.vue'
import AlertRules from '@/views/AlertRules.vue'
import AlertTemplates from '@/views/AlertTemplates.vue'
import AlertHistory from '@/views/AlertHistory.vue'
import Monitoring from '@/views/Monitoring.vue'
import ClusterOverview from '@/views/ClusterOverview.vue'
import ClusterComponents from '@/views/ClusterComponents.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: Login
    },
    {
      path: '/',
      component: MainLayout,
      redirect: ROUTES.DASHBOARD,
      children: [
        {
          path: 'dashboard',
          name: 'dashboard',
          component: Dashboard,
          meta: { title: '首页' }
        },
        {
          path: 'users',
          name: 'users',
          component: UserManagement,
          meta: { title: 'LDAP用户管理' }
        },
        {
          path: 'alert-rules',
          name: 'alert-rules',
          component: AlertRules,
          meta: { title: '告警规则' }
        },
        {
          path: 'alert-templates',
          name: 'alert-templates',
          component: AlertTemplates,
          meta: { title: '告警模板' }
        },
        {
          path: 'alert-history',
          name: 'alert-history',
          component: AlertHistory,
          meta: { title: '告警历史' }
        },
        {
          path: 'monitoring',
          name: 'monitoring',
          component: Monitoring,
          meta: { title: '集群监控' }
        },
        {
          path: 'cluster/overview',
          name: 'cluster-overview',
          component: ClusterOverview,
          meta: { title: '集群总览' }
        },
        {
          path: 'cluster/components',
          name: 'cluster-components',
          component: ClusterComponents,
          meta: { title: '组件监控' }
        }
      ]
    }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem(STORAGE_KEYS.TOKEN)
  if (to.path !== ROUTES.LOGIN && !token) {
    next(ROUTES.LOGIN)
  } else if (to.path === ROUTES.LOGIN && token) {
    next(ROUTES.DASHBOARD)
  } else {
    next()
  }
})

export default router
