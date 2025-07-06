import axios from 'axios';

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use(
  (config) => {
    // Only add Authorization header if the request is not for registration
    if (config.url !== '/auth/registration/') {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Token ${token}`;
      }
    }
    // Add CSRF token for POST requests
    if (config.method === 'post') {
      const csrfToken = getCookie('csrftoken');
      if (csrfToken) {
        config.headers['X-CSRFToken'] = csrfToken;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response) {
      // Erro de resposta da API (status code fora do 2xx)
      const { data, status } = error.response;
      let errorMessages = [];
      if (data && typeof data === 'object') {
        for (const key in data) {
          errorMessages.push(`${key}: ${data[key]}`);
        }
      }
      else if (data) {
        errorMessages.push(data);
      }
      else {
        errorMessages.push(`Error ${status}: ${error.message}`);
      }
      // Aqui você precisará injetar o showErrorModal do App.vue
      // Por enquanto, vamos apenas rejeitar a promessa
      return Promise.reject(errorMessages);
    }
    else if (error.request) {
      // The request was made but no response was received
      return Promise.reject(['No response from server. Check your connection.']);
    }
    else {
      // Something happened in setting up the request that triggered an Error
      return Promise.reject([`Request error: ${error.message}`]);
    }
  }
);

export default {
  search(criteria) {
    // Use GET for search with query parameters
    // Ensure only relevant criteria are sent for CPF/CNPJ search
    const params = {};
    if (criteria.cpf) params.cpf = criteria.cpf;
    if (criteria.cnpj) params.cnpj = criteria.cnpj; // Add CNPJ parameter
    if (criteria.name) params.name = criteria.name;

    return apiClient.get('/search/', { params: params });
  },
  login(credentials) {
    return apiClient.post('/auth/login/', credentials);
  },
  register(userData) {
    return apiClient.post('/auth/registration/', userData);
  },
  cnpjSearch(data) {
    return apiClient.post('/cnpj/search/', data);
  },
};