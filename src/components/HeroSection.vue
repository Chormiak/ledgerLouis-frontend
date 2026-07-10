<template>
  <section class="hero">
    <div class="hero-background">
      <div class="gradient-orb gradient-orb--1"></div>
      <div class="gradient-orb gradient-orb--2"></div>
      <div class="gradient-orb gradient-orb--3"></div>
    </div>

    <div class="hero-container">
      <div class="hero-content">

        <h1 class="hero-title">
          Transforme suas
          <span class="gradient-text">finanças</span>
          <br />
          em resultados
        </h1>

        <p class="hero-description">
          Controle total de entradas e saídas, relatórios inteligentes e uma 
          experiência que simplifica a gestão financeira da sua empresa.
        </p>

        <div class="hero-actions">
          <button class="btn-primary" @click="$emit('signup')">
            <span>Começar Gratuitamente</span>
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M4.16666 10H15.8333M15.8333 10L10 4.16666M15.8333 10L10 15.8333" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
          <button class="btn-secondary" @click="scrollToFeatures">
            <span>Saiba Mais</span>
          </button>
        </div>

        <div class="hero-stats">
          <div class="stat-item">
            <div class="stat-value">100%</div>
            <div class="stat-label">Gratuito</div>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <div class="stat-value">24/7</div>
            <div class="stat-label">Disponível</div>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <div class="stat-value">5min</div>
            <div class="stat-label">Setup rápido</div>
          </div>
        </div>
      </div>

      <div class="hero-visual">
        <div class="dashboard-mockup">
          <div class="mockup-header">
            <div class="mockup-dots">
              <span class="dot"></span>
              <span class="dot"></span>
              <span class="dot"></span>
            </div>
          </div>
          <div class="mockup-content">
            <div class="mockup-card">
              <div class="mockup-line short"></div>
              <div class="mockup-line"></div>
            </div>
            <div class="mockup-card">
              <div class="mockup-line medium"></div>
              <div class="mockup-line short"></div>
            </div>
            <div class="mockup-chart">
              <div class="chart-bar" style="height: 60%"></div>
              <div class="chart-bar" style="height: 80%"></div>
              <div class="chart-bar" style="height: 45%"></div>
              <div class="chart-bar" style="height: 90%"></div>
              <div class="chart-bar" style="height: 70%"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const scrollToFeatures = () => {
  const featuresSection = document.querySelector('.features-section');
  featuresSection?.scrollIntoView({ behavior: 'smooth' });
};
</script>

<style scoped>
.hero {
  position: relative;
  min-height: 90vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  padding: 80px 20px 60px;
}

.hero-background {
  position: absolute;
  inset: 0;
  overflow: hidden;
  z-index: 0;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.6;
  animation: float 20s ease-in-out infinite;
}

.gradient-orb--1 {
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, #27B969 0%, #1DCD6C 100%);
  top: -100px;
  right: -100px;
  animation-delay: 0s;
}

.gradient-orb--2 {
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  bottom: -50px;
  left: -50px;
  animation-delay: 5s;
}

.gradient-orb--3 {
  width: 250px;
  height: 250px;
  background: linear-gradient(135deg, #34d399 0%, #10b981 100%);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation-delay: 10s;
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(30px, -30px) scale(1.05);
  }
  66% {
    transform: translate(-20px, 20px) scale(0.95);
  }
}

.hero-container {
  position: relative;
  z-index: 1;
  max-width: 1200px;
  width: 100%;
  display: grid;
  grid-template-columns: 1fr;
  gap: 60px;
  align-items: center;
}

@media (min-width: 1024px) {
  .hero-container {
    grid-template-columns: 1fr 1fr;
  }
}

.hero-content {
  color: white;
}


.badge-icon {
  font-size: 18px;
}

.badge-text {
  font-size: 14px;
  font-weight: 600;
  color: #27B969;
}

.hero-title {
  font-size: clamp(2rem, 5vw, 3.5rem);
  font-weight: 800;
  line-height: 1.1;
  margin-bottom: 24px;
  color: white;
}

.gradient-text {
  background: linear-gradient(135deg, #27B969 0%, #1DCD6C 50%, #34d399 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-description {
  font-size: clamp(1rem, 2vw, 1.125rem);
  line-height: 1.7;
  color: #cbd5e1;
  margin-bottom: 32px;
  max-width: 540px;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 48px;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 16px 32px;
  background: linear-gradient(135deg, #27B969 0%, #1DCD6C 100%);
  color: white;
  border: none;
  border-radius: 999px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(39, 185, 105, 0.4);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 30px rgba(39, 185, 105, 0.5);
}

.btn-primary:active {
  transform: translateY(0);
}

.btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 16px 32px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 999px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
}

.hero-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  align-items: center;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: 800;
  color: #27B969;
}

.stat-label {
  font-size: 14px;
  color: #94a3b8;
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: rgba(255, 255, 255, 0.2);
}

.hero-visual {
  display: none;
}

@media (min-width: 1024px) {
  .hero-visual {
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.dashboard-mockup {
  width: 100%;
  max-width: 500px;
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  overflow: hidden;
  backdrop-filter: blur(20px);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: float 6s ease-in-out infinite;
}

.mockup-header {
  padding: 12px 16px;
  background: rgba(15, 23, 42, 0.6);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.mockup-dots {
  display: flex;
  gap: 6px;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
}

.dot:first-child {
  background: #ef4444;
}

.dot:nth-child(2) {
  background: #f59e0b;
}

.dot:last-child {
  background: #10b981;
}

.mockup-content {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.mockup-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 16px;
}

.mockup-line {
  height: 12px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  margin-bottom: 8px;
}

.mockup-line:last-child {
  margin-bottom: 0;
}

.mockup-line.short {
  width: 60%;
}

.mockup-line.medium {
  width: 80%;
}

.mockup-chart {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  height: 120px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
}

.chart-bar {
  flex: 1;
  background: linear-gradient(180deg, #27B969 0%, #1DCD6C 100%);
  border-radius: 8px 8px 0 0;
  transition: all 0.3s ease;
}

.chart-bar:hover {
  background: linear-gradient(180deg, #34d399 0%, #27B969 100%);
  transform: scaleY(1.05);
  transform-origin: bottom;
}
</style>