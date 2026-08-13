<template>
  <main class="settings-page">
    <div class="settings-container">
      <!-- Page Title -->
      <header class="page-header">
        <h1>Configurações</h1>
        <p>Gerencie suas informações pessoais e preferências</p>
      </header>

      <!-- User Settings Section -->
      <section class="settings-card">
        <div class="card-header" @click="toggleUserSection">
          <div class="header-content">
            <User :size="24" class="icon" />
            <div>
              <h2>Meu Perfil</h2>
              <span class="subtitle">Informações da sua conta</span>
            </div>
          </div>
          <ChevronDown
            :size="24"
            :class="{ 'rotated': isUserExpanded }"
            class="chevron"
          />
        </div>

        <transition name="slide">
          <div v-show="isUserExpanded" class="card-content">
            <div class="profile-identity">
              <div class="avatar-wrap">
                <div class="avatar-display">
                  <img
                    v-if="displayAvatarUrl"
                    :src="displayAvatarUrl"
                    alt="Seu avatar"
                    class="avatar-image"
                  />
                  <div v-else class="avatar-placeholder">
                    <User :size="32" />
                  </div>
                </div>

                <button
                  type="button"
                  class="avatar-edit-btn"
                  :disabled="isUploading"
                  @click="fileInput?.click()"
                  aria-label="Alterar foto de perfil"
                  title="Alterar foto de perfil"
                >
                  <Loader2 v-if="isUploading" :size="14" class="icon-spin" />
                  <Camera v-else :size="14" />
                </button>

                <input
                  ref="fileInput"
                  type="file"
                  accept="image/*"
                  @change="handleAvatarSelect"
                  class="file-input"
                  hidden
                />
              </div>

              <div class="identity-text">
                <template v-if="isLoadingUser">
                  <span class="skeleton-line skeleton-line--name" />
                  <span class="skeleton-line skeleton-line--email" />
                </template>
                <template v-else>
                  <h3 class="user-name">{{ userInfo.name || 'Seu nome' }}</h3>
                  <p class="user-email">{{ userInfo.email || 'seuemail@exemplo.com' }}</p>
                </template>
              </div>
            </div>

            <p v-if="loadError" class="feedback-msg error-msg">{{ loadError }}</p>
            <p v-if="uploadError" class="feedback-msg error-msg">{{ uploadError }}</p>
            <p v-if="uploadSuccess" class="feedback-msg success-msg">{{ uploadSuccess }}</p>

            <div class="profile-footer">
              <button type="button" class="btn-signout" @click="handleLogout">
                <LogOut :size="16" />
                <span>Sair da conta</span>
              </button>
            </div>
          </div>
        </transition>
      </section>

      <!-- Appearance Settings Section -->
      <section class="settings-card">
        <div class="card-header">
          <div class="header-content">
            <component :is="isDark ? Moon : Sun" :size="24" class="icon" />
            <div>
              <h2>Aparência</h2>
              <span class="subtitle">Escolha entre o tema claro e o escuro</span>
            </div>
          </div>
          <button
            type="button"
            class="theme-switch"
            role="switch"
            :aria-checked="isDark"
            aria-label="Alternar modo escuro"
            @click="themeStore.toggleTheme()"
          >
            <span class="theme-switch-thumb" />
          </button>
        </div>
      </section>

      <!-- Additional Settings Sections (for future use) -->
      <section class="settings-card disabled">
        <div class="card-header">
          <div class="header-content">
            <Lock :size="24" class="icon" />
            <div>
              <h2>Segurança</h2>
              <span class="subtitle">Gerencie sua senha e autenticação</span>
            </div>
          </div>
        </div>
      </section>

      <section class="settings-card disabled">
        <div class="card-header">
          <div class="header-content">
            <Bell :size="24" class="icon" />
            <div>
              <h2>Notificações</h2>
              <span class="subtitle">Controle suas preferências de notificação</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  </main>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { User, ChevronDown, Lock, Bell, Sun, Moon, Camera, Loader2, LogOut } from 'lucide-vue-next'
import UserService from '@/services/userService'
import { useUserStore } from '@/stores/userStore'
import { useThemeStore } from '@/stores/themeStore'

interface UserInfo {
  id: string
  name: string
  email: string
  avatar?: string
}

const isUserExpanded = ref(true)
const isUploading = ref(false)
const isLoadingUser = ref(true)
const loadError = ref('')
const uploadError = ref('')
const uploadSuccess = ref('')
const fileInput = ref<HTMLInputElement>()

const userStore = useUserStore()
const themeStore = useThemeStore()
const router = useRouter()

const isDark = computed(() => themeStore.theme === 'dark')

const userInfo = reactive<UserInfo>({
  id: '',
  name: '',
  email: '',
  avatar: '',
})

const userService = new UserService()

// Avatar URL da store (prioridade)
const displayAvatarUrl = computed(() => userStore.avatar || userInfo.avatar)

const toggleUserSection = () => {
  isUserExpanded.value = !isUserExpanded.value
}

const handleLogout = () => {
  userService.logout()
  router.push('/entrar')
}

const loadUserInfo = async () => {
  isLoadingUser.value = true
  loadError.value = ''
  try {
    const response = await userService.getUserInfo()
    userInfo.id = response.id || ''
    userInfo.name = response.name || ''
    userInfo.email = response.email || ''
    userInfo.avatar = response.avatar || ''

    if (response.avatar) {
      userStore.setavatar(response.avatar)
    }
  } catch (error) {
    console.error('Erro ao carregar informações do usuário:', error)
    loadError.value = 'Não foi possível carregar seus dados. Verifique se você está logado.'
  } finally {
    isLoadingUser.value = false
  }
}

const handleAvatarSelect = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]

  if (!file) return

  // Validações
  if (!file.type.startsWith('image/')) {
    uploadError.value = '❌ Por favor, selecione um arquivo de imagem'
    setTimeout(() => { uploadError.value = '' }, 4000)
    return
  }

  const maxSize = 5 * 1024 * 1024 // 5MB
  if (file.size > maxSize) {
    uploadError.value = '❌ Arquivo muito grande. Máximo 5MB'
    setTimeout(() => { uploadError.value = '' }, 4000)
    return
  }

  // Preview local
  const reader = new FileReader()
  reader.onload = (e) => {
    userInfo.avatar = e.target?.result as string
  }
  reader.readAsDataURL(file)

  // Upload para servidor
  try {
    isUploading.value = true
    uploadError.value = ''
    uploadSuccess.value = ''

    await userService.uploadAvatar(file)

    uploadSuccess.value = '✅ Foto de perfil atualizada com sucesso!'
    setTimeout(() => {
      uploadSuccess.value = ''
    }, 4000)

  } catch (error) {
    uploadError.value = '❌ Erro ao fazer upload. Tente novamente.'
    // Recarregar dados originais em caso de erro
    await loadUserInfo()
    console.error('Erro ao fazer upload:', error)
  } finally {
    isUploading.value = false
  }

  // Limpar input
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

onMounted(() => {
  loadUserInfo()
})
</script>

<style scoped>
.settings-page {
  min-height: calc(100vh - 65px);
  padding: 32px 20px;
  background-color: var(--color-surface-soft);
}

.settings-container {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}

/* Page Header */
.page-header {
  margin-bottom: 32px;
  text-align: center;
}

.page-header h1 {
  font-size: 2rem;
  color: var(--color-text);
  margin: 0 0 8px 0;
  font-weight: 700;
}

.page-header p {
  font-size: 1rem;
  color: var(--color-placeholder);
  margin: 0;
}

/* Settings Card */
.settings-card {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  margin-bottom: 16px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.settings-card:not(.disabled):hover {
  border-color: var(--color-primary);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.settings-card.disabled {
  opacity: 0.5;
  pointer-events: none;
}

/* Card Header */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  cursor: pointer;
  user-select: none;
  border-bottom: 1px solid var(--color-border);
  transition: background-color 0.2s ease;
}

.card-header:hover {
  background-color: var(--color-bg);
}

.header-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-content .icon {
  color: var(--color-primary);
  flex-shrink: 0;
}

.header-content h2 {
  font-size: 1.15rem;
  margin: 0 0 4px 0;
  color: var(--color-text);
  font-weight: 600;
}

.subtitle {
  display: block;
  font-size: 0.85rem;
  color: var(--color-placeholder);
  margin: 0;
}

.chevron {
  color: var(--color-placeholder);
  transition: transform 0.3s ease;
  flex-shrink: 0;
}

.chevron.rotated {
  transform: rotate(180deg);
}

/* Theme Switch */
.theme-switch {
  flex-shrink: 0;
  width: 48px;
  height: 28px;
  padding: 3px;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  background-color: var(--color-bg);
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: background-color 0.25s ease, border-color 0.25s ease;
}

.theme-switch[aria-checked='true'] {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
}

.theme-switch-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background-color: var(--color-surface);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.25);
  transition: transform 0.25s ease;
}

.theme-switch[aria-checked='true'] .theme-switch-thumb {
  transform: translateX(20px);
}

/* Card Content */
.card-content {
  padding: 24px;
}

/* Profile identity */
.profile-identity {
  display: flex;
  align-items: center;
  gap: 20px;
}

.avatar-wrap {
  position: relative;
  flex-shrink: 0;
}

.avatar-display {
  width: 76px;
  height: 76px;
  border-radius: 50%;
  overflow: hidden;
  border: 1px solid var(--color-border);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-surface-alt);
  color: var(--color-placeholder);
}

.avatar-edit-btn {
  position: absolute;
  right: -2px;
  bottom: -2px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 3px solid var(--color-surface);
  background-color: var(--color-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.2s ease, transform 0.2s ease;
}

.avatar-edit-btn:hover:not(:disabled) {
  background-color: var(--color-primary-hover);
  transform: scale(1.06);
}

.avatar-edit-btn:disabled {
  cursor: not-allowed;
  opacity: 0.85;
}

.icon-spin {
  animation: icon-spin 0.8s linear infinite;
}

@keyframes icon-spin {
  to {
    transform: rotate(360deg);
  }
}

.identity-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.user-name {
  font-family: var(--font-display);
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--color-text);
  line-height: 1.25;
}

.user-email {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  overflow-wrap: anywhere;
}

.skeleton-line {
  display: block;
  height: 14px;
  border-radius: 6px;
  background-color: var(--color-border);
  animation: skeleton-pulse 1.4s ease-in-out infinite;
}

.skeleton-line + .skeleton-line {
  margin-top: 8px;
}

.skeleton-line--name {
  width: 140px;
  height: 16px;
}

.skeleton-line--email {
  width: 190px;
}

@keyframes skeleton-pulse {
  0%,
  100% {
    opacity: 0.6;
  }
  50% {
    opacity: 1;
  }
}

.feedback-msg {
  margin: 14px 0 0;
  font-size: 0.85rem;
}

.error-msg {
  color: var(--color-danger);
}

.success-msg {
  color: var(--color-success);
}

/* Profile footer / sign out */
.profile-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 10px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--color-border);
}

.btn-signout {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border: 1px solid transparent;
  border-radius: var(--radius-input);
  background-color: transparent;
  color: var(--color-danger);
  font-size: 0.9rem;
  font-weight: 600;
  font-family: var(--font-body);
  cursor: pointer;
  transition: background-color 0.2s ease, color 0.2s ease, box-shadow 0.2s ease;
}

.btn-signout:hover {
  background-color: var(--color-danger-soft);
}

/* Animations */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  max-height: 0;
}

/* Responsive */
@media (max-width: 600px) {
  .settings-page {
    padding: 20px 16px;
  }

  .page-header h1 {
    font-size: 1.5rem;
  }

  .profile-identity {
    flex-direction: column;
    text-align: center;
  }

  .profile-footer {
    justify-content: center;
  }

  .card-header {
    padding: 16px;
  }

  .card-content {
    padding: 16px;
  }
}
</style>
