<template>
  <div class="card">
    <div class="card-header">
      <h4>Search Criteria</h4>
    </div>
    <div class="card-body">
      <form @submit.prevent="performSearch">
        <div class="row g-3">
          <div class="col-md-4">
            <label for="cpf" class="form-label">CPF</label>
            <input type="text" class="form-control" id="cpf" v-model="searchCriteria.cpf">
          </div>
          <div class="col-md-4">
            <label for="name" class="form-label">Name</label>
            <input type="text" class="form-control" id="name" v-model="searchCriteria.name">
          </div>
          <div class="col-md-4">
            <label for="birthdate" class="form-label">Birthdate</label>
            <input type="date" class="form-control" id="birthdate" v-model="searchCriteria.birthdate">
          </div>
        </div>
        <button type="submit" class="btn btn-primary mt-3">Search</button>
      </form>
    </div>
  </div>

  <div v-if="results" class="mt-4">
    <div class="card">
      <div class="card-header">
        <h4>Search Results</h4>
      </div>
      <div class="card-body">
        <table class="table table-striped">
          <thead>
            <tr>
              <th>CPF</th>
              <th>Name</th>
              <th>Birthdate</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="result in results" :key="result.cpf">
              <td>{{ result.cpf }}</td>
              <td>{{ result.name }}</td>
              <td>{{ result.birthdate }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <div v-if="error" class="alert alert-danger mt-4">
    {{ error }}
  </div>
</template>

<script setup>
import { ref } from 'vue';
import api from '@/services/api';

const searchCriteria = ref({
  cpf: '',
  name: '',
  birthdate: ''
});

const results = ref(null);
const error = ref(null);

const performSearch = async () => {
  try {
    const response = await api.search(searchCriteria.value);
    results.value = response.data;
    error.value = null;
  } catch (err) {
    error.value = err.response ? err.response.data : err.message;
    results.value = null;
  }
};
</script>
