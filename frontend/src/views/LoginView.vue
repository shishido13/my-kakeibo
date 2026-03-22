<template>
  <div class="fin-page min-h-screen px-4 py-6 sm:px-6 lg:px-8">
    <div class="fin-frame flex min-h-[calc(100vh-3rem)] items-center justify-center">
      <div class="grid w-full max-w-[1080px] overflow-hidden rounded-[20px] border border-line bg-panel shadow-hairline lg:grid-cols-[1.1fr_420px]">
        <main class="bg-panel px-5 py-6 sm:px-8 sm:py-8 lg:px-10 lg:py-10">
          <div class="mx-auto flex h-full max-w-[340px] flex-col justify-between">
            <div>
              <div class="inline-flex h-12 w-12 items-center justify-center rounded-[12px] border border-line bg-surface text-accent-strong">
                <i class="pi pi-wallet text-[18px]"></i>
              </div>
              <div class="mt-6">
                <div class="fin-label">Sign In</div>
                <h2 class="fin-title mt-2 text-[30px] font-semibold leading-[1.08]">シシド家計簿</h2>
                <p class="mt-3 text-[13px] leading-6 text-ink-soft">
                  Google アカウントで認証し、ダッシュボードと集計画面へアクセスします。
                </p>
              </div>

              <div v-if="error" class="mt-6 rounded-[12px] border border-[#e3d2d3] bg-[#f6efef] px-4 py-3 text-[#7b4f53]">
                <div class="fin-label text-[#7b4f53]">Authentication Error</div>
                <div class="mt-1 text-[12px] font-medium leading-6">{{ errorMessage }}</div>
              </div>

              <button type="button" @click="handleGoogleLogin" class="mt-8 flex w-full items-center justify-center gap-3 rounded-[12px] border border-accent bg-[linear-gradient(180deg,_#2a4b65_0%,_#1d3447_100%)] px-4 py-3 text-[13px] font-semibold text-white transition hover:border-accent-strong hover:bg-[linear-gradient(180deg,_#315674_0%,_#173042_100%)]">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="20" height="20" aria-hidden="true">
                  <path fill="#fbc02d" d="M43.611,20.083H42V20H24v8h11.303c-1.649,4.657-6.08,8-11.303,8c-6.627,0-12-5.373-12-12s5.373-12,12-12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C12.955,4,4,12.955,4,24s8.955,20,20,20s20-8.955,20-20C44,22.659,43.862,21.35,43.611,20.083z"/>
                  <path fill="#e53935" d="M6.306,14.691l6.571,4.819C14.655,15.108,18.961,12,24,12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C16.318,4,9.656,8.337,6.306,14.691z"/>
                  <path fill="#4caf50" d="M24,44c5.166,0,9.86-1.977,13.409-5.192l-6.19-5.238C29.211,35.091,26.715,36,24,36c-5.202,0-9.619-3.317-11.283-7.946l-6.522,5.025C9.505,39.556,16.227,44,24,44z"/>
                  <path fill="#1565c0" d="M43.611,20.083L43.595,20L42,20H24v8h11.303c-0.792,2.237-2.231,4.166-4.087,5.571c0.001-0.001,0.002-0.001,0.003-0.002l6.19,5.238C36.971,39.205,44,34,44,24C44,22.659,43.862,21.35,43.611,20.083z"/>
                </svg>
                <span>Google でログイン</span>
              </button>
            </div>

            <footer class="mt-8 border-t border-line pt-4 text-[11px] text-muted">
              <div class="flex items-center justify-between gap-3">
                <span>Shishido Kakeibo</span>
                <span class="fin-value">2026</span>
              </div>
            </footer>
          </div>
        </main>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { auth } from '../auth';

const route = useRoute();
const error = computed(() => route.query.error);

const errorMessage = computed(() => {
  if (error.value === 'auth_failed') return '認証に失敗しました。時間をおいて再度お試しください。';
  if (error.value === 'access_denied') return 'アクセスが許可されていません。許可済みメールでログインしてください。';
  return 'ログインエラーが発生しました。';
});

const handleGoogleLogin = () => {
  auth();
};
</script>
