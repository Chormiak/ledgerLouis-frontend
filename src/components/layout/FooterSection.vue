<template>
  <footer class="site-footer">
    <div class="glow glow--1" aria-hidden="true"></div>
    <div class="glow glow--2" aria-hidden="true"></div>

    <div class="footer-content">
      <div class="footer-brand">
        <span class="logo-text">LEDGER</span>
        <p class="tagline">Controle financeiro simples para empresas que querem crescer.</p>
      </div>

      <nav class="footer-links" aria-label="Navegação">
        <p class="links-title">Navegação</p>
        <RouterLink to="/">Início</RouterLink>
        <RouterLink to="/company">Empresas</RouterLink>
      </nav>

      <nav class="footer-links" aria-label="Conta">
        <p class="links-title">Conta</p>
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
  position: relative;
  overflow: hidden;
  background: linear-gradient(180deg, #0f172a 0%, #0b111f 100%);
  padding: 28px 25px 124px;
  margin-bottom: -100px;
}

.glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(70px);
  opacity: 0.1;
  pointer-events: none;
}

.glow--1 {
  width: 220px;
  height: 220px;
  background: linear-gradient(135deg, #27b969 0%, #1dcd6c 100%);
  top: -100px;
  left: -70px;
}

.glow--2 {
  width: 180px;
  height: 180px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  bottom: -50px;
  right: -50px;
}

.footer-content {
  position: relative;
  z-index: 1;
  display: grid;
  gap: 20px;
  max-width: 1100px;
  margin: 0 auto;
}

.footer-brand .logo-text {
  font-family: var(--font-display);
  font-weight: 800;
  font-size: 16px;
  letter-spacing: 1px;
  background: linear-gradient(135deg, #27b969 0%, #1dcd6c 50%, #34d399 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.tagline {
  margin-top: 6px;
  font-size: 12.5px;
  color: #94a3b8;
  max-width: 300px;
  line-height: 1.6;
}

.links-title {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #6ee7b7;
  margin-bottom: 10px;
}

.footer-links {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.footer-links a {
  font-size: 13px;
  font-weight: 600;
  color: #cbd5e1;
  text-decoration: none;
  transition: color 0.2s ease;
  width: fit-content;
}

.footer-links a:hover {
  color: #34d399;
}

.footer-bottom {
  position: relative;
  z-index: 1;
  max-width: 1100px;
  margin: 22px auto 0;
  padding-top: 14px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.footer-bottom p {
  font-size: 11.5px;
  color: #64748b;
}

@media (min-width: 700px) {
  .footer-content {
    grid-template-columns: 1.4fr 1fr 1fr;
  }
}

@media (min-width: 1100px) {
  .site-footer {
    padding: 36px 40px 124px;
  }

  .footer-content,
  .footer-bottom {
    max-width: 1000px;
  }
}
</style>
