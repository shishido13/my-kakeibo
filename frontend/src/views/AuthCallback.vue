<template>
  <div>ログイン処理中...</div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getGoogleRedirectUri } from '../auth'
import { authApi } from '../services/api'

const router = useRouter()
const route = useRoute()

onMounted(async () => {
  const code = route.query.code // Googleから渡されたコード
  if (typeof code !== 'string') {
    router.replace('/login?error=auth_failed')
    return
  }

  try {
    const response = await authApi.post('/google', {
      code,
      redirect_uri: getGoogleRedirectUri(),
    })

    localStorage.setItem('isLoggedIn', 'true')
    localStorage.setItem('userEmail', response.data.email)

    router.push('/')
  } catch (error: any) {
    console.error('ログイン失敗:', error)
    const errorType = error.response?.status === 403 ? 'access_denied' : 'auth_failed'
    router.push(`/login?error=${errorType}`)
  }
})
</script>