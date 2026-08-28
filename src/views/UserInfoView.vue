<script lang="ts" setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import UserInfo from "../components/user/UserInfo.vue"
import { useUserStore } from '@/stores/userStore'

const router = useRouter()
const userStore = useUserStore()

onMounted(() => {
  if (!userStore.accessToken) {
    router.replace({ name: 'entrar' })
  }
})
</script>
<template>
    <div class="main-container">
        <div class="auth-wrapper">
            <UserInfo />
        </div>
    </div>
  </template>
  
  <style scoped>
  .main-container {
      width: 100%;
      min-height: calc(100vh - 175px);
      display: flex;
      flex-direction: column;
      align-items: center; 
      justify-content: center;
      background-color: var(--color-bg);
      padding: 20px;
  }
  
  .auth-wrapper {
      width: 100%;
      max-width: 500px;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      border-radius: 0;
      overflow: hidden; 
      background-color: transparent; 
      box-shadow: none;
  }
  </style>