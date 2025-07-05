<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card bg-dark text-white border-secondary">
          <div class="card-header text-center">
            <h3>Register</h3>
          </div>
          <div class="card-body">
            <form @submit.prevent="register">
              <div class="mb-3">
                <label for="email" class="form-label">Email</label>
                <input type="email" class="form-control" id="email" v-model="email" required>
              </div>
              <div class="mb-3">
                <label for="name" class="form-label">Name</label>
                <input type="text" class="form-control" id="name" v-model="name" required>
              </div>
              <div class="mb-3">
                <label for="password" class="form-label">Password</label>
                <input type="password" class="form-control" id="password" v-model="password" required>
              </div>
              <div class="mb-3">
                <label for="confirmPassword" class="form-label">Confirm Password</label>
                <input type="password" class="form-control" id="confirmPassword" v-model="confirmPassword" required>
              </div>
              <div class="d-grid">
                <button type="submit" class="btn btn-primary">Register</button>
              </div>
            </form>
            <p v-if="error" class="text-danger mt-3 text-center">{{ error }}</p>
            <p v-if="successMessage" class="text-success mt-3 text-center">{{ successMessage }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'

export default {
  data() {
    return {
      email: '',
      name: '',
      password: '',
      confirmPassword: '',
      error: '',
      successMessage: ''
    }
  },
  methods: {
    async register() {
      if (this.password !== this.confirmPassword) {
        this.error = 'Passwords do not match.';
        this.successMessage = '';
        return;
      }

      try {
        await api.register({
          username: this.name,
          email: this.email,
          password1: this.password,
          password2: this.confirmPassword
        })
        // Attempt to log in the user after successful registration
        try {
          const loginResponse = await api.login({
            username: this.name,
            password: this.password
          });
          localStorage.setItem('token', loginResponse.data.key); // Assuming the token is in response.data.key
          this.successMessage = 'Registration successful! You are now logged in.';
          this.error = '';
          this.$router.push('/search');
        } catch (loginError) {
          this.error = 'Registration successful, but automatic login failed. Please try logging in manually.';
          this.successMessage = '';
          this.$router.push('/login');
        }
      } catch (e) {
        this.error = e.response ? this.getErrorMessage(e.response.data) : 'Registration failed.'
        this.successMessage = ''
      }
    },
    getErrorMessage(errorData) {
      if (!errorData) {
        return 'An unknown error occurred.';
      }
      if (errorData.detail) {
        return errorData.detail;
      }
      const fieldErrors = ['email', 'name', 'password', 'username'];
      for (const field of fieldErrors) {
        if (errorData[field] && Array.isArray(errorData[field]) && errorData[field].length > 0) {
          return `${field}: ${errorData[field][0]}`;
        }
      }
      return JSON.stringify(errorData);
    }
  }
}
</script>
