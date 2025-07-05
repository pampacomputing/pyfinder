<template>
  

  <!-- Conteúdo principal -->
  <main class="container-fluid mt-4">
    <RouterView />
  </main>
</template>

<script setup>
import { RouterView } from 'vue-router'
</script>

<style>
.offcanvas-body .navbar-nav {
  height: 100%;
  display: flex;
  flex-direction: column;
}

#app {
  max-width: none !important;
  padding: 0 !important;
  margin: 0 !important;
  display: block !important;
}
@media (min-width: 1024px) {
  body {
    display: block !important;
    place-items: unset !important;
  }
}
</style>

<style>
.offcanvas-body .navbar-nav {
  height: 100%;
  display: flex;
  flex-direction: column;
}

#app {
  max-width: none !important;
  padding: 0 !important;
  margin: 0 !important;
  display: block !important;
}
@media (min-width: 1024px) {
  body {
    display: block !important;
    place-items: unset !important;
  }
}
</style>
