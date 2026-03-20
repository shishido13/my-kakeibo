import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import ImportVerifyView from '../views/ImportVerifyView.vue'
import { GOOGLE_AUTH_CALLBACK_PATH } from '../auth.ts'
import LoginView from '../views/LoginView.vue'
import SettlementView from '../views/SettlementView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: DashboardView
    },
    {
      path: '/import',
      name: 'importVerify',
      component: ImportVerifyView
    },
    {
      path: '/analytics',
      name: 'analytics',
      component: () => import('../views/AnalyticsView.vue')
    },
    {
      path: '/settlement',
      name: 'settlement',
      component: SettlementView
    },
    {
      path: '/login',
      name: 'Login',
      component: LoginView
    },
    {
      path: GOOGLE_AUTH_CALLBACK_PATH,
      name: 'AuthCallback',
      component: () => import('../views/AuthCallback.vue')
    }

  ]
})

router.beforeEach((to, from, next) => {
  const publicPages = ['/login', GOOGLE_AUTH_CALLBACK_PATH];
  const authRequired = !publicPages.includes(to.path);
  const isAuthenticated = localStorage.getItem('isLoggedIn'); // 暫定的なフラグ

  if (authRequired && !isAuthenticated) {
    next('/login');
  } else {
    next();
  }
});

export default router
