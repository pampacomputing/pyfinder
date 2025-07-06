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

    <h2 class="mt-4">Register</h2>
    <form @submit.prevent="onRegister">
      <div class="mb-3">
        <label for="reg-username" class="form-label">Username</label>
        <input type="text" class="form-control" id="reg-username" v-model="registration.username">
      </div>
      <div class="mb-3">
        <label for="reg-email" class="form-label">Email</label>
        <input type="email" class="form-control" id="reg-email" v-model="registration.email">
      </div>
      <div class="mb-3">
        <label for="reg-password" class="form-label">Password</label>
        <input type="password" class="form-control" id="reg-password" v-model="registration.password">
      </div>
      <div class="mb-3">
        <label for="reg-password-confirm" class="form-label">Confirm Password</label>
        <input type="password" class="form-control" id="reg-password-confirm" v-model="registration.password_confirm">
      </div>
      <button type="submit" class="btn btn-success">Register</button>
    </form>

   </div>
</template>

<script setup>
import { ref, inject } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';
 
const authStore = useAuthStore();
const router = useRouter();

const credentials = ref({
  username: '',
  password: ''
});

const registration = ref({
  username: '',
  email: '',
  password: '',
  password_confirm: ''
});


const showErrorModal = inject('showErrorModal');
 
const onLogin = async () => {
  try {
    await authStore.login(credentials.value);
    if (authStore.isAuthenticated) {
      router.push({ name: 'search' });
    }
  } catch (err) {
    showErrorModal(authStore.error);
  }
};

const onRegister = async () => {
   if (registration.value.password !== registration.value.password_confirm) {
     showErrorModal(['Passwords do not match.']);
     return;
   }
   try {
     await authStore.register({
       username: registration.value.username,
       email: registration.value.email,
       password: registration.value.password,
     });
     // Optionally, clear form or show success message
     alert('Registration successful! You can now log in.'); // This alert is still in Portuguese
     registration.value = { username: '', email: '', password: '', password_confirm: '' };
   } catch (err) {
     showErrorModal(authStore.error);
  }
};
</script>

<style scoped>
.login-view {
  max-width: 400px;
  margin: 0 auto;
}
</style>
