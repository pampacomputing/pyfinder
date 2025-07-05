<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card bg-dark text-white border-secondary">
          <div class="card-header text-center">
            <h3>Login</h3>
          </div>
          <div class="card-body">
            <form @submit.prevent="login">
              <div class="mb-3">
                <label for="username" class="form-label">Username</label>
                <input type="text" class="form-control" id="username" v-model="username">
              </div>
              <div class="mb-3">
                <label for="password" class="form-label">Password</label>
                <input type="password" class="form-control" id="password" v-model="password">
              </div>
              <div class="d-grid">
                <button type="submit" class="btn btn-primary">Login</button>
              </div>
              <div class="d-grid mt-2">
                <button type="button" class="btn btn-secondary" @click="goToRegister">Sign In</button>
              </div>
            </form>
            <p v-if="error" class="text-danger mt-3 text-center">{{ error }}</p>
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
      username: '',
      password: '',
      error: ''
    }
  },
  methods: {
    async login() {
      try {
        const { data } = await api.login({
          username: this.username,
          password: this.password
        })
        localStorage.setItem('token', data.key)

        /* —— Navega para /search — App.vue detectará o token via afterEach —— */
        this.$router.push('/search')
      } catch (e) {
        this.error = 'Invalid credentials'
      }
    },
    goToRegister() {
      this.$router.push('/register')
    }
  }
}
</script>
