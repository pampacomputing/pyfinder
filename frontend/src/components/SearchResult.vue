<!-- src/components/SearchResult.vue -->
<template>
  <div v-if="results" class="row justify-content-center gx-0 mt-4">
    <div class="col-12 col-lg-10 col-xxl-8 px-0">
      <div class="card bg-dark text-white border-secondary w-100">
        <div class="card-header">
          <h4>Results</h4>
        </div>

        <div class="card-body p-0">
          <!-- CPF Results -->
          <div v-if="results.user_data && results.user_data.length > 0">
            <h5 class="card-title p-3">CPF Results</h5>
            <div class="table-container table-responsive">
              <table class="table table-dark table-striped table-hover m-0">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>CPF</th>
                    <th>Name</th>
                    <th>Birthdate</th>
                    <th>Gender</th>
                  </tr>
                </thead>
                <tbody>
                  <template v-for="(result, idx) in pagedCpfResults" :key="result.cpf">
                    <tr
                      @click="emit('getAssociatedCompanies', result.name, result.cpf)"
                      :class="{ 'table-active': selectedCpfResult && selectedCpfResult.name === result.name }"
                    >
                      <td>{{ (cpfPage - 1) * perPage + idx + 1 }}</td>
                      <td>{{ formatCpf(result.cpf) }}</td>
                      <td>{{ result.name }}</td>
                      <td>{{ formatDate(result.date) }}</td>
                      <td>{{ result.gender }}</td>
                    </tr>
                    <tr v-if="selectedCpfResult && selectedCpfResult.name === result.name && selectedCpfResult.associated_companies && selectedCpfResult.associated_companies.length > 0">
                      <td colspan="5">
                        <div class="p-3">
                          <h6 class="text-white">Associated Companies for {{ selectedCpfResult.name }}</h6>
                          <table class="table table-dark table-sm">
                            <thead>
                              <tr>
                                <th>CNPJ</th>
                                <th>Company Name</th>
                                <th>Trade Name</th>
                              </tr>
                            </thead>
                            <tbody>
                              <template v-for="(company, companyIdx) in selectedCpfResult.associated_companies" :key="companyIdx">
                                <tr @click="toggleCompanyDetails(company)" class="company-row">
                                <td>{{ formatCnpj(company.cnpj) }}</td>
                                <td>{{ company.razao_social }}</td>
                                <td>{{ company.nome_fantasia }}</td>
                              </tr>
                              <tr v-if="selectedCompany && selectedCompany.cnpj === company.cnpj">
                                <td colspan="3">
                                  <div class="p-3">
                                    <h6 class="text-white">Company Details</h6>
                                    <table class="table table-dark table-sm">
                                      <tbody>
                                        <tr><th>Legal Nature</th><td>{{ company.natureza_juridica }}</td></tr>
                                        <tr><th>Size</th><td>{{ company.porte }}</td></tr>
                                        <tr><th>Capital Stock</th><td>{{ company.capital_social }}</td></tr>
                                        <tr><th>Registration Status</th><td>{{ company.situacao_cadastral }}</td></tr>
                                        <tr><th>Registration Date</th><td>{{ formatDate(company.data_situacao_cadastral) }}</td></tr>
                                        <tr><th>Registration Reason</th><td>{{ company.motivo_situacao_cadastral }}</td></tr>
                                        <tr><th>Street</th><td>{{ company.endereco.logradouro }}</td></tr>
                                        <tr><th>Number</th><td>{{ company.endereco.numero }}</td></tr>
                                        <tr><th>Complement</th><td>{{ company.endereco.complemento }}</td></tr>
                                        <tr><th>Neighborhood</th><td>{{ company.endereco.bairro }}</td></tr>
                                        <tr><th>City</th><td>{{ company.endereco.municipio }}</td></tr>
                                        <tr><th>State</th><td>{{ company.endereco.uf }}</td></tr>
                                        <tr><th>ZIP Code</th><td>{{ company.endereco.cep }}</td></tr>
                                      </tbody>
                                    </table>
                                  </div>
                                </td>
                              </tr>
                              </template>
                            </tbody>
                          </table>
                        </div>
                      </td>
                    </tr>
                  </template>
                </tbody>
              </table>
            </div>

            <!-- ▸ PAGINATION ------------------------------------------------ -->
            <nav v-if="totalCpfPages > 1" class="mt-3">
              <ul class="pagination justify-content-center mb-0">
                <li class="page-item" :class="{ disabled: cpfPage === 1 }">
                  <button class="page-link" @click="emit('update:cpfPage', cpfPage - 1)">«</button>
                </li>

                <li
                  class="page-item"
                  v-for="n in totalCpfPages"
                  :key="n"
                  :class="{ active: n === cpfPage }"
                >
                  <button class="page-link" @click="emit('goToCpfPage', n)">{{ n }}</button>
                </li>

                <li class="page-item" :class="{ disabled: cpfPage === totalCpfPages }">
                  <button class="page-link" @click="emit('update:cpfPage', cpfPage + 1)">»</button>
                </li>
              </ul>
            </nav>
          </div>

          <!-- CNPJ Company Data -->
          <div v-else-if="results.empresa && Object.keys(results.empresa).length > 0" class="mt-4">
            <h5 class="card-title p-3">Company Data (CNPJ)</h5>
            <div class="table-container table-responsive">
              <table class="table table-dark table-striped table-hover m-0">
                <thead>
                  <tr>
                    <th>CNPJ</th>
                    <th>Company Name</th>
                    <th>Trade Name</th>
                    <th>Legal Nature</th>
                    <th>Size</th>
                    <th>Capital Stock</th>
                    <th>Registration Status</th>
                    <th>Registration Date</th>
                    <th>Registration Status Reason</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>{{ formatCnpj(results.cnpj) }}</td>
                    <td>{{ results.empresa.razao_social }}</td>
                    <td>{{ results.empresa.nome_fantasia }}</td>
                    <td>{{ results.empresa.natureza_juridica.descricao }}</td>
                    <td>{{ results.empresa.porte }}</td>
                    <td>{{ results.empresa.capital_social }}</td>
                    <td>{{ results.empresa.situacao_cadastral.descricao }}</td>
                    <td>{{ formatDate(results.empresa.situacao_cadastral.data) }}</td>
                    <td>{{ results.empresa.situacao_cadastral.motivo.descricao }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- CNPJ Address Data -->
          <div v-if="results.empresa && results.empresa.endereco" class="mt-4">
            <h5 class="card-title p-3">Address</h5>
            <div class="table-container table-responsive">
              <table class="table table-dark table-striped table-hover m-0">
                <thead>
                  <tr>
                    <th>Street</th>
                    <th>Number</th>
                    <th>Complement</th>
                    <th>Neighborhood</th>
                    <th>City</th>
                    <th>State</th>
                    <th>ZIP Code</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>{{ results.empresa.endereco.logradouro }}</td>
                    <td>{{ results.empresa.endereco.numero }}</td>
                    <td>{{ results.empresa.endereco.complemento }}</td>
                    <td>{{ results.empresa.endereco.bairro }}</td>
                    <td>{{ results.empresa.endereco.municipio.descricao }}</td>
                    <td>{{ results.empresa.endereco.uf }}</td>
                    <td>{{ results.empresa.endereco.cep }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- CNPJ Partner Data (Subtable) -->
          <div v-if="results.socios && results.socios.length > 0" class="mt-4">
            <h5 class="card-title p-3">Partner Data for {{ results.empresa.razao_social }}</h5>
            <div class="table-container table-responsive">
              <table class="table table-dark table-striped table-hover m-0">
                <thead>
                  <tr>
                    <th>CPF</th>
                    <th>Name</th>
                    <th>Gender</th>
                    <th>Birthdate</th>
                    <th>Partner Qualification</th>
                    <th>Entry Date</th>
                    <th>Country</th>
                    <th>Legal Representative</th>
                    <th>Representative Name</th>
                    <th>Legal Representative Qualification</th>
                    <th>Age Range</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(partner, partnerIdx) in results.socios" :key="partnerIdx">
                    <td>{{ formatCpf(partner.cpf) }}</td>
                    <td>{{ partner.nome }}</td>
                    <td>{{ formatGender(partner.sexo) }}</td>
                    <td>{{ formatDate(partner.data_nascimento) }}</td>
                    <td>{{ partner.qualificacao_socio.descricao }}</td>
                    <td>{{ formatDate(partner.data_entrada_sociedade) }}</td>
                    <td>{{ partner.pais.descricao }}</td>
                    <td>{{ partner.representante_legal }}</td>
                    <td>{{ partner.nome_representante }}</td>
                    <td>{{ partner.qualificacao_representante_legal.descricao }}</td>
                    <td>{{ partner.faixa_etaria }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>

import {ref} from "vue";

const selectedCompany = ref(null);

const toggleCompanyDetails = (company) => {
  if (selectedCompany.value && selectedCompany.value.cnpj === company.cnpj) {
    selectedCompany.value = null;
  } else {
    selectedCompany.value = company;
  }
};

defineProps({
  results: {
    type: Object,
    default: () => null,
  },
  selectedCpfResult: {
    type: Object,
    default: () => null,
  },
  cpfPage: {
    type: Number,
    required: true,
  },
  perPage: {
    type: Number,
    required: true,
  },
  totalCpfPages: {
    type: Number,
    required: true,
  },
  pagedCpfResults: {
    type: Array,
    required: true,
  },
});

const emit = defineEmits(['getAssociatedCompanies', 'update:cpfPage', 'goToCpfPage']);

const formatCpf = (cpf) => {
  if (!cpf) return '';
  const cleanCpf = cpf.replace(/\D/g, '');
  if (cleanCpf.length !== 11) return cpf;
  return cleanCpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
};

const formatCnpj = (cnpj) => {
  if (!cnpj) return '';
  const cleanCnpj = cnpj.replace(/\D/g, '');
  if (cleanCnpj.length !== 14) return cnpj;
  return cleanCnpj.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  if (dateString.length === 8 && /^[0-9]+$/.test(dateString)) {
    const year = dateString.substring(0, 4);
    const month = dateString.substring(4, 6);
    const day = dateString.substring(6, 8);
    return `${day}/${month}/${year}`;
  }
  if (dateString.includes('-')) {
    const [year, month, day] = dateString.split('-');
    return `${day}/${month}/${year}`;
  }
  return dateString;
};

const formatGender = (genderCode) => {
  if (genderCode === 'M') return 'Male';
  if (genderCode === 'F') return 'Female';
  return genderCode;
};
</script>

<style scoped>
.table-container {
  max-height: 60vh;
  overflow: auto;
}
.table thead th {
  position: sticky;
  top: 0;
  z-index: 2;
}
.company-row {
  cursor: pointer;
}
</style>
