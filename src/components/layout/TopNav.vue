<template>
  <header class="top-navbar">
    <router-link to="/" class="logo-section">
      <span class="logo-text">LEDGER</span>
    </router-link>
  </header>
</template>

<style scoped>
.top-navbar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 52px;
  background-color: var(--color-surface);
  display: flex;
  align-items: center;
  padding: 0 18px;
  box-sizing: border-box;
  z-index: 1001;

  border-bottom: 1px solid var(--color-border);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02);
}

.logo-section {
  display: inline-flex;
  align-items: center;
  text-decoration: none;
}

.logo-text {
  font-family: var(--font-display);
  font-weight: 800;
  font-size: 15px;
  letter-spacing: 1px;
  color: var(--color-text);
}
</style>