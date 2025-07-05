<template>
  <div class="login-view">
    <h2>Login</h2>
    <form @submit.prevent="onLogin">
      <div class="mb-3">
        <label for="username" class="form-label">Username</label>
        <input type="text" class="form-control" id="username" v-model="credentials.username">
      </div>
      <div class="mb-3">
        <label for="password" class="form-label">Password</label>
        <input type="password" class="form-control" id="password" v-model="credentials.password">
      </div>
      <button type="submit" class="btn btn-primary">Login</button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

const credentials = ref({
  username: '',
  password: ''
});

const onLogin = async () => {
  await authStore.login(credentials.value);
  if (authStore.isAuthenticated) {
    router.push({ name: 'search' });
  }
};
</script>

<style scoped>
.login-view {
  max-width: 400px;
  margin: 0 auto;
}
</style>
