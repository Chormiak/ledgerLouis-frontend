<template>
  <footer class="site-footer">
    <div class="footer-content">
      <div class="footer-brand">
        <span class="logo-text">LEDGER</span>
        <p class="tagline">Controle financeiro simples para empresas que querem crescer.</p>
      </div>

      <nav class="footer-links" aria-label="Links rápidos">
        <RouterLink to="/">Início</RouterLink>
        <RouterLink to="/company">Empresas</RouterLink>
        <RouterLink to="/entrar">Entrar</RouterLink>
        <RouterLink to="/cadastro">Criar conta</RouterLink>
      </nav>
    </div>

    <div class="footer-bottom">
      <p>© {{ year }} Ledger Louis. Feito pela equipe GitCoffee.</p>
    </div>
  </footer>
</template>

<script setup lang="ts">
const year = new Date().getFullYear();
</script>

<style scoped>
.site-footer {
  background-color: var(--color-surface);
  border-top: 1px solid var(--color-border);
  padding: 40px 25px 124px;
  margin-bottom: -100px;
}

.footer-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 1100px;
  margin: 0 auto;
}

.footer-brand .logo-text {
  font-family: var(--font-display);
  font-weight: 800;
  font-size: 18px;
  letter-spacing: 1px;
  color: var(--color-text);
}

.tagline {
  margin-top: 8px;
  font-size: 13px;
  color: var(--color-text-secondary);
  max-width: 320px;
  line-height: 1.6;
}

.footer-links {
  display: flex;
  flex-wrap: wrap;
  gap: 16px 24px;
}

.footer-links a {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-decoration: none;
  transition: color 0.2s ease;
}

.footer-links a:hover {
  color: var(--color-success-dark);
}

.footer-bottom {
  max-width: 1100px;
  margin: 28px auto 0;
  padding-top: 20px;
  border-top: 1px solid var(--color-border);
}

.footer-bottom p {
  font-size: 12px;
  color: var(--color-text-tertiary);
}

@media (min-width: 700px) {
  .footer-content {
    flex-direction: row;
    justify-content: space-between;
    align-items: flex-start;
  }
}

@media (min-width: 1100px) {
  .site-footer {
    padding: 40px 40px 124px;
  }

  .footer-content,
  .footer-bottom {
    max-width: 1000px;
  }
}
</style>
