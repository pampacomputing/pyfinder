<!-- src/components/SearchBar.vue -->
<template>
  <div class="card bg-dark text-white border-secondary w-100">
    <div class="card-header">
      <h4>Search</h4>
    </div>
    <div class="card-body">
      <form @submit.prevent="emit('performSearchNow')">
        <div class="row g-3">
          <div class="col-sm-6">
            <label for="cpf" class="form-label">CPF</label>
            <input
              id="cpf"
              type="text"
              class="form-control"
              :value="searchCriteria.cpf"
              @input="updateCriteria('cpf', $event.target.value)"
              placeholder="Search by CPF…"
            />
          </div>

          <div class="col-sm-6">
            <label for="cnpj" class="form-label">CNPJ</label>
            <input
              id="cnpj"
              type="text"
              class="form-control"
              :value="searchCriteria.cnpj"
              @input="updateCriteria('cnpj', $event.target.value)"
              placeholder="Search by CNPJ…"
            />
          </div>

          <div class="col-sm-6">
            <label for="name" class="form-label">Name</label>
            <input
              id="name"
              type="text"
              class="form-control"
              :value="searchCriteria.name"
              @input="updateCriteria('name', $event.target.value)"
              placeholder="Search by Name…"
            />
          </div>

          <div class="col-12">
            <button type="submit" class="btn btn-primary me-2">Search CPF</button>
            <button type="button" class="btn btn-info" @click="emit('performCnpjSearch')">Search CNPJ</button>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  searchCriteria: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(['update:searchCriteria', 'performSearchNow', 'performCnpjSearch']);

const updateCriteria = (field, value) => {
  const newCriteria = { ...props.searchCriteria, [field]: value };
  emit('update:searchCriteria', newCriteria);
};
</script>
