<template>
  <!-- Conteúdo principal -->
  <main class="container-fluid mt-4">
    <RouterView />
  </main>

  <!-- Componente do Modal de Erro -->
  <ErrorModal
    :isVisible="isErrorModalVisible"
    :message="errorMessages"
    @close="closeErrorModal"
  />
</template>

<script setup>
import { ref, provide } from 'vue';
import { RouterView } from 'vue-router';
import ErrorModal from './components/ErrorModal.vue';

const errorMessages = ref([]);
const isErrorModalVisible = ref(false);

const showErrorModal = (messages) => {
  errorMessages.value = Array.isArray(messages) ? messages : [messages];
  isErrorModalVisible.value = true;
};

const closeErrorModal = () => {
  isErrorModalVisible.value = false;
  errorMessages.value = [];
};

provide('showErrorModal', showErrorModal);
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
  display: block !importan;
}
@media (min-width: 1024px) {
  body {
    display: block !important;
    place-items: unset !important;
  }
}
</style>
