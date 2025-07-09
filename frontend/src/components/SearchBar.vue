<!-- src/components/SearchBar.vue -->
<template>
  <div class="card bg-dark text-white border-secondary w-100">
    <div class="card-header">
      <h4>Search</h4>
    </div>
    <div class="card-body">
      <form @submit.prevent="handleCpfSearch">
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
              @input="updateNameCriteria($event.target.value)"
              placeholder="Search by Name…"
            />
          </div>

          <div class="col-12">
            <button type="submit" class="btn btn-primary me-2">Search CPF</button>
            <button type="button" class="btn btn-info" @click="handleCnpjSearch">Search CNPJ</button>
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

const emit = defineEmits(['update:searchCriteria', 'performSearchNow', 'performCnpjSearch', 'validationError']);

const updateCriteria = (field, value) => {
  const newCriteria = { ...props.searchCriteria, [field]: value };
  emit('update:searchCriteria', newCriteria);
};

const updateNameCriteria = (value) => {
  const sanitizedValue = value.replace(/[^a-zA-Z\sãõáéíóúçàèìòùâêîôûÃÕÁÉÍÓÚÇÀÈÌÒÙÂÊÎÔÛ]/g, '');
  updateCriteria('name', sanitizedValue);
};

const validateCpf = (cpf) => {
  cpf = cpf.replace(/[^\d]+/g,'');
  if(cpf === '' || cpf.length !== 11 || /^(\d)\1{10}$/.test(cpf)) return false;
  let add = 0;
  for (let i=0; i < 9; i++) add += parseInt(cpf.charAt(i)) * (10 - i);
  let rev = 11 - (add % 11);
  if (rev === 10 || rev === 11) rev = 0;
  if (rev !== parseInt(cpf.charAt(9))) return false;
  add = 0;
  for (let i = 0; i < 10; i++) add += parseInt(cpf.charAt(i)) * (11 - i);
  rev = 11 - (add % 11);
  if (rev === 10 || rev === 11) rev = 0;
  if (rev !== parseInt(cpf.charAt(10))) return false;
  return true;
};

const validateCnpj = (cnpj) => {
    cnpj = cnpj.replace(/[^\d]+/g, '');
    if (cnpj === '' || cnpj.length !== 14 || /^(\d)\1{13}$/.test(cnpj)) return false;
    let length = cnpj.length - 2;
    let numbers = cnpj.substring(0, length);
    const digits = cnpj.substring(length);
    let sum = 0;
    let pos = length - 7;
    for (let i = length; i >= 1; i--) {
      sum += numbers.charAt(length - i) * pos--;
      if (pos < 2) pos = 9;
    }
    let result = sum % 11 < 2 ? 0 : 11 - (sum % 11);
    if (result != digits.charAt(0)) return false;
    length = length + 1;
    numbers = cnpj.substring(0, length);
    sum = 0;
    pos = length - 7;
    for (let i = length; i >= 1; i--) {
      sum += numbers.charAt(length - i) * pos--;
      if (pos < 2) pos = 9;
    }
    result = sum % 11 < 2 ? 0 : 11 - (sum % 11);
    if (result != digits.charAt(1)) return false;
    return true;
}

const handleCpfSearch = () => {
  if (props.searchCriteria.cpf && !validateCpf(props.searchCriteria.cpf)) {
    emit('validationError', 'Invalid CPF');
  } else {
    emit('performSearchNow');
  }
};

const handleCnpjSearch = () => {
  if (props.searchCriteria.cnpj && !validateCnpj(props.searchCriteria.cnpj)) {
    emit('validationError', 'Invalid CNPJ');
  } else {
    emit('performCnpjSearch');
  }
};
</script>
