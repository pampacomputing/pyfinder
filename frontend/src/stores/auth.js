import { defineStore } from 'pinia';
import api from '@/services/api';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
  },
  actions: {
    async login(credentials) {
      const response = await api.post('/auth/login/', credentials);
      this.token = response.data.key;
      localStorage.setItem('token', this.token);
    },
    logout() {
      this.token = null;
      localStorage.removeItem('token');
    },
  },
});
