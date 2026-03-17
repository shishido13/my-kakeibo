<template>
  <div class="login-wrapper">
    <!-- Animated background layers -->
    <div class="bg-layer"></div>
    
    <main class="login-container">
      <div class="auth-card animate-fade-in-up">
        <header class="auth-header">
          <div class="app-logo">
            <i class="pi pi-wallet logo-icon"></i>
          </div>
          <h1>シシド家計簿</h1>
          <p class="subtitle">シンプルでスマートな家計管理を</p>
        </header>

        <section class="auth-content">
          <div v-if="error" class="error-notification animate-shake">
            <i class="pi pi-exclamation-circle"></i>
            {{ errorMessage }}
          </div>

          <button @click="handleGoogleLogin" class="google-login-btn premium-btn">
            <div class="google-btn-content">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="24px" height="24px">
                <path fill="#fbc02d" d="M43.611,20.083H42V20H24v8h11.303c-1.649,4.657-6.08,8-11.303,8c-6.627,0-12-5.373-12-12s5.373-12,12-12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C12.955,4,4,12.955,4,24s8.955,20,20,20s20-8.955,20-20C44,22.659,43.862,21.35,43.611,20.083z"/>
                <path fill="#e53935" d="M6.306,14.691l6.571,4.819C14.655,15.108,18.961,12,24,12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C16.318,4,9.656,8.337,6.306,14.691z"/>
                <path fill="#4caf50" d="M24,44c5.166,0,9.86-1.977,13.409-5.192l-6.19-5.238C29.211,35.091,26.715,36,24,36c-5.202,0-9.619-3.317-11.283-7.946l-6.522,5.025C9.505,39.556,16.227,44,24,44z"/>
                <path fill="#1565c0" d="M43.611,20.083L43.595,20L42,20H24v8h11.303c-0.792,2.237-2.231,4.166-4.087,5.571c0.001-0.001,0.002-0.001,0.003-0.002l6.19,5.238C36.971,39.205,44,34,44,24C44,22.659,43.862,21.35,43.611,20.083z"/>
              </svg>
              <span>Googleでログイン</span>
            </div>
          </button>
        </section>

        <footer class="auth-footer">
          <p>© 2024 Shishido Kakeibo</p>
        </footer>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { auth } from '../auth'

const route = useRoute()
const error = computed(() => route.query.error)

const errorMessage = computed(() => {
  if (error.value === 'auth_failed') return '認証に失敗しました。時間をおいて再度お試しください。'
  if (error.value === 'access_denied') return 'アクセスが許可されていません（ホワイトリスト外）。'
  return 'ログインエラーが発生しました。'
})

const handleGoogleLogin = () => {
  auth()
}
</script>

<style scoped>
.login-wrapper {
  --font-primary: 'Outfit', sans-serif;
  --font-secondary: 'Inter', sans-serif;
  --bg-primary: #0f172a;
  
  @apply relative w-full h-screen flex items-center justify-center overflow-hidden;
  background-color: var(--bg-primary);
  font-family: var(--font-secondary);
}

.bg-layer {
  @apply absolute inset-0 z-0 bg-cover bg-center;
  background-image: url('../assets/login-bg.png');
  filter: brightness(0.6) saturate(1.2);
  transform: scale(1.1);
  transition: transform 20s ease;
}

.login-wrapper:hover .bg-layer {
  transform: scale(1);
}

.login-container {
  @apply relative z-10 w-full max-w-md px-4;
}

/* Glassmorphism Classes moved from global style.css */
.glass-effect {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
}

.auth-card {
  @apply glass-effect rounded-3xl p-8 md:p-12;
}

.auth-header {
  @apply text-center mb-10;
}

.app-logo {
  @apply inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-indigo-600 mb-4 shadow-lg shadow-indigo-500/30;
}

.logo-icon {
  @apply text-white text-3xl;
}

h1 {
  @apply text-3xl font-bold text-white mb-2;
  font-family: var(--font-primary);
  letter-spacing: -0.02em;
}

.subtitle {
  @apply text-slate-400 text-sm;
}

.auth-content {
  @apply mb-10;
}

.google-login-btn {
  @apply w-full h-14 bg-white hover:bg-slate-50 text-slate-800 font-semibold rounded-xl shadow-xl shadow-black/20 flex items-center justify-center;
}

.google-btn-content {
  @apply flex items-center gap-3;
}

.premium-btn {
  @apply relative overflow-hidden transition-all duration-300 active:scale-95;
}

.error-notification {
  @apply flex items-center gap-2 p-4 mb-6 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm;
}

.auth-footer {
  @apply text-center text-slate-500 text-xs mt-8;
}

/* Animations */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in-up {
  animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

.animate-shake {
  animation: shake 0.4s ease-in-out;
}
</style>