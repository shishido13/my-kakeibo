import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import ImportVerifyView from '../views/ImportVerifyView.vue'
import { auth } from '../auth.ts'
import LoginView from '../views/LoginView.vue'

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
      path: '/login',
      name: 'Login',
      component: LoginView
    },
    {
      path: '/api/auth/callback/google',
      name: 'AuthCallback',
      component: () => import('../views/AuthCallback.vue')
    }

  ]
})

router.beforeEach((to, from, next) => {
  const publicPages = ['/login', '/api/auth/callback/google'];
  const authRequired = !publicPages.includes(to.path);
  const isAuthenticated = localStorage.getItem('isLoggedIn'); // 暫定的なフラグ

  if (authRequired && !isAuthenticated) {
    next('/login');
  } else {
    next();
  }
});

export default router
