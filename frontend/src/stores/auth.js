import { defineStore } from 'pinia';
import api from '@/services/api';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    error: [], // Changed to an array for multiple error messages
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
  },
  actions: {
    async login(credentials) {
      this.error = []; // Clear previous errors
      try {
        const response = await api.login(credentials);
        this.token = response.data.key;
        localStorage.setItem('token', this.token);
      } catch (err) {
        if (err.response && err.response.data) {
          // Handle API validation errors (e.g., 400 Bad Request)
          for (const key in err.response.data) {
            if (Array.isArray(err.response.data[key])) {
              err.response.data[key].forEach(msg => this.error.push(`${key}: ${msg}`));
            } else if (typeof err.response.data[key] === 'string') {
              this.error.push(`${key}: ${err.response.data[key]}`);
            }
          }
        } else {
          // Handle network errors or other unexpected errors
          this.error.push(err.message || 'An unknown error occurred during login.');
        }
        throw err; // Re-throw to allow component to handle further if needed
      }
    },
    async register(userData) {
      this.error = []; // Clear previous errors
      try {
        const response = await api.register(userData);
        // Assuming successful registration might return a token or just a success message
        // If it returns a token, you might want to log the user in automatically
        // For now, just handle success/error
        console.log('Registration successful:', response.data);
      } catch (err) {
        // Extract specific error message from registration response
        if (err.response && err.response.data) {
          // Handle API validation errors (e.g., 400 Bad Request)
          for (const key in err.response.data) {
            if (Array.isArray(err.response.data[key])) {
              err.response.data[key].forEach(msg => this.error.push(`${key}: ${msg}`));
            } else if (typeof err.response.data[key] === 'string') {
              this.error.push(`${key}: ${err.response.data[key]}`);
            }
          }
        } else {
          // Handle network errors or other unexpected errors
          this.error.push(err.message || 'An unknown error occurred during registration.');
        }
        throw err; // Re-throw to allow component to handle further if needed
      }
    },
    logout() {
      this.token = null;
      localStorage.removeItem('token');
      this.error = []; // Clear error on logout
    },
    clearError() {
      this.error = [];
    },
  },
});
