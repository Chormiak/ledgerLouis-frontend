<template>
  <section class="decision-cta">
    <div class="cta-card">
      <div class="glow glow--1" aria-hidden="true"></div>
      <div class="glow glow--2" aria-hidden="true"></div>

      <div class="cta-content">
        <h2 class="cta-title">E agora, já se <span class="highlight">decidiu?</span></h2>
        <p class="cta-subtitle">
          Entre no <span class="brand-text">Ledger Louis</span> agora mesmo. É gratuito, simples e focado no que
          importa: seu lucro.
        </p>

        <PrimaryButton @click="$emit('signup')">
          Começar agora
          <svg width="18" height="18" viewBox="0 0 20 20" fill="none" aria-hidden="true">
            <path
              d="M4.16666 10H15.8333M15.8333 10L10 4.16666M15.8333 10L10 15.8333"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </PrimaryButton>

        <p class="free-badge">Sempre grátis para começar</p>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import PrimaryButton from '@/components/ui/PrimaryButton.vue';

// Emitindo o mesmo evento do seu Hero para manter o padrão
defineEmits(['signup']);
</script>

<style scoped>
.decision-cta {
  padding: 0 20px 48px;
}

.cta-card {
  position: relative;
  overflow: hidden;
  max-width: 720px;
  margin: 0 auto;
  padding: 48px 32px;
  border-radius: 28px;
  text-align: center;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.18);
}

.glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.2;
  pointer-events: none;
}

.glow--1 {
  width: 220px;
  height: 220px;
  background: linear-gradient(135deg, #27b969 0%, #1dcd6c 100%);
  top: -90px;
  right: -60px;
}

.glow--2 {
  width: 160px;
  height: 160px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  bottom: -70px;
  left: -50px;
}

.cta-content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

h2.cta-title {
  font-family: var(--font-display);
  font-size: 28px;
  font-weight: 800;
  color: white;
  margin-bottom: 12px;
  line-height: 1.2;
}

.highlight {
  background: linear-gradient(135deg, #27b969 0%, #1dcd6c 50%, #34d399 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.cta-subtitle {
  font-size: 15px;
  color: #cbd5e1;
  line-height: 1.6;
  max-width: 420px;
  margin-bottom: 28px;
}

.brand-text {
  color: #6ee7b7;
  font-weight: 700;
}

.cta-content :deep(.primary-btn) {
  gap: 8px;
}

.free-badge {
  margin-top: 16px;
  font-size: 12px;
  color: #94a3b8;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

@media (min-width: 1100px) {
  .cta-card {
    padding: 56px 48px;
  }

  h2.cta-title {
    font-size: 32px;
  }
}
</style>
