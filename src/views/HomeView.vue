<template>
  <main class="home-container">
    <HeroSection @signup="handleSignup" />

    <section class="features-section">
      <h2 class="section-title">
        Conheça Nosso <br />
        <span class="highlight">Gerenciador Financeiro</span>
      </h2>

      <div class="features-list">
        <FeatureItem 
          number="1" 
          title="Todos os gastos na Palma Na mão" 
          description="Acompanhe cada centavo de onde quer que você esteja com nossa interface mobile-first." 
        />
        <FeatureItem 
          number="2" 
          title="Prático e simples" 
          description="Sem menus complicados. Adicione suas entradas e saídas em segundos." 
        />
        <FeatureItem 
          number="3" 
          title="Análises complexas" 
          description="Transformamos seus dados em gráficos fáceis de entender para sua tomada de decisão." 
        />
        <FeatureItem 
          number="4" 
          title="Relatórios mensais" 
          description="Receba fechamentos detalhados e entenda para onde seu dinheiro está indo." 
        />
      </div>
    </section>

    <HowItWorks />

    <CompanyTestimonials />

    <CalltoAction @signup="handleSignup" />

    <FooterSection />
  </main>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import HeroSection from '@/components/sections/HeroSection.vue';
import FeatureItem from '@/components/sections/FeatureItem.vue';
import HowItWorks from '@/components/sections/HowItWorks.vue';
import CompanyTestimonials from '@/components/sections/CompanyTestimonials.vue';
import CalltoAction from '@/components/sections/CalltoAction.vue';
import FooterSection from '@/components/layout/FooterSection.vue';

const router = useRouter();

const handleSignup = () => {
  router.push({ name: 'cadastro' });
};
</script>

<style scoped>
.home-container {
  background-color: var(--color-surface-soft);
  min-height: 100vh;
}

.home-container :deep(.hero) {
  margin-top: -10px;
}

.features-section {
  padding: 70px 25px 20px 25px;
  max-width: 1100px;
  margin: 0 auto;
}

.section-title {
  text-align: center;
  font-family: var(--font-display);
  font-size: clamp(22px, 2vw, 27px);
  color: var(--color-success-dark);
  margin-bottom: 32px;
  font-weight: 600;
  line-height: 1.3;
}

.highlight {
  font-weight: 800;
}

.features-list {
  display: grid;
  gap: 16px;
}

@media (min-width: 700px) {
  .features-list {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1100px) {
  .features-section {
    padding: 64px 25px 24px;
  }
}
</style>