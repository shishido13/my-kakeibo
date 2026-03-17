<template>
  <div>ログイン処理中...</div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const route = useRoute()

onMounted(async () => {
  const code = route.query.code // Googleから渡されたコード
  if (code) {
    try {
      // 1. バックエンドにコードを送って、ユーザー情報を取得・認証する
      const response = await axios.post(`${import.meta.env.VITE_API_URL}/auth/google`, { code })
      
      // 2. ログイン成功フラグを保存（本来はJWTトークンなどを入れる）
      localStorage.setItem('isLoggedIn', 'true')
      localStorage.setItem('userEmail', response.data.email)

      // 3. ダッシュボードへ移動
      router.push('/')
    } catch (error: any) {
      console.error('ログイン失敗:', error)
      const errorType = error.response?.status === 403 ? 'access_denied' : 'auth_failed'
      router.push(`/login?error=${errorType}`)
    }
  }
})
</script>