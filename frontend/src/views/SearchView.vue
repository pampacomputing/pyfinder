<!-- src/views/SearchView.vue -->
<template>
  <div class="container-fluid mt-4 px-0">
    <h1 class="mb-4 text-center">PyFinder – Advanced Search</h1>

    <!-- ▸ SEARCH CRITERIA --------------------------------------------------- -->
    <div class="row justify-content-center gx-0">
      <div class="col-12 col-lg-10 col-xxl-8 px-0">
        <div class="card bg-dark text-white border-secondary w-100">
          <div class="card-header">
            <h4>Search Criteria</h4>
          </div>
          <div class="card-body">
            <form @submit.prevent="performSearchNow">
              <div class="row g-3">
                <div class="col-sm-6">
                  <label for="cpf" class="form-label">CPF</label>
                  <input
                    id="cpf"
                    type="text"
                    class="form-control"
                    v-model="searchCriteria.cpf"
                    placeholder="Search by CPF…"
                  />
                </div>

                <div class="col-sm-6">
                  <label for="cnpj" class="form-label">CNPJ</label>
                  <input
                    id="cnpj"
                    type="text"
                    class="form-control"
                    v-model="searchCriteria.cnpj"
                    placeholder="Search by CNPJ…"
                  />
                </div>

                <div class="col-sm-6">
                  <label for="name" class="form-label">Name</label>
                  <input
                    id="name"
                    type="text"
                    class="form-control"
                    v-model="searchCriteria.name"
                    placeholder="Search by Name…"
                  />
                </div>

                <div class="col-sm-6 col-md-4">
                  <label for="birthdate" class="form-label">Birthdate</label>
                  <input
                    id="birthdate"
                    type="date"
                    class="form-control"
                    v-model="searchCriteria.birthdate"
                  />
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- ▸ LOADING ----------------------------------------------------------- -->
    <div v-if="loading" class="text-center mt-4">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading…</span>
      </div>
    </div>

    <!-- ▸ SEARCH RESULTS ---------------------------------------------------- -->
    <div v-if="results" class="row justify-content-center gx-0 mt-4">
      <div class="col-12 col-lg-10 col-xxl-8 px-0">
        <div class="card bg-dark text-white border-secondary w-100">
          <div class="card-header">
            <h4>Search Results</h4>
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
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="(result, idx) in pagedCpfResults"
                      :key="result.cpf"
                    >
                      <td>{{ (cpfPage - 1) * perPage + idx + 1 }}</td>
                      <td>{{ result.cpf }}</td>
                      <td>{{ result.name }}</td>
                      <td>{{ result.date }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- ▸ PAGINATION ------------------------------------------------ -->
              <nav v-if="totalCpfPages > 1" class="mt-3">
                <ul class="pagination justify-content-center mb-0">
                  <li class="page-item" :class="{ disabled: cpfPage === 1 }">
                    <button class="page-link" @click="cpfPage--">«</button>
                  </li>

                  <li
                    class="page-item"
                    v-for="n in totalCpfPages"
                    :key="n"
                    :class="{ active: n === cpfPage }"
                  >
                    <button class="page-link" @click="goToCpfPage(n)">{{ n }}</button>
                  </li>

                  <li class="page-item" :class="{ disabled: cpfPage === totalCpfPages }">
                    <button class="page-link" @click="cpfPage++">»</button>
                  </li>
                </ul>
              </nav>
            </div>

            <!-- CNPJ Company Data -->
            <div v-if="results.company_data && results.company_data.length > 0" class="mt-4">
              <h5 class="card-title p-3">Company Data (CNPJ)</h5>
              <div class="table-container table-responsive">
                <table class="table table-dark table-striped table-hover m-0">
                  <thead>
                    <tr>
                      <th>CNPJ</th>
                      <th>Razão Social</th>
                      <th>Nome Fantasia</th>
                      <th>Situação Cadastral</th>
                      <th>Endereço</th>
                      <th>Telefone</th>
                      <th>Email</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="company in results.company_data" :key="company.cnpj">
                      <td>{{ company.cnpj }}</td>
                      <td>{{ company.razao_social }}</td>
                      <td>{{ company.nome_fantasia }}</td>
                      <td>{{ company.situacao_cadastral }}</td>
                      <td>{{ company.logradouro }}, {{ company.numero }} - {{ company.bairro }}, {{ company.municipio }} - {{ company.uf }}</td>
                      <td>{{ company.ddd_1 }} {{ company.telefone_1 }}</td>
                      <td>{{ company.ddd_2 }} {{ company.telefone_2 }}</td>
                      <td>{{ company.email }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- CNPJ Partner Data -->
            <div v-if="results.partner_data && results.partner_data.length > 0" class="mt-4">
              <h5 class="card-title p-3">Partner Data (CNPJ)</h5>
              <div class="table-container table-responsive">
                <table class="table table-dark table-striped table-hover m-0">
                  <thead>
                    <tr>
                      <th>Nome Sócio</th>
                      <th>CPF/CNPJ Sócio</th>
                      <th>Data Entrada Sociedade</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="partner in results.partner_data" :key="partner.cpf_cnpj_socio">
                      <td>{{ partner.nome_socio }}</td>
                      <td>{{ partner.cpf_cnpj_socio }}</td>
                      <td>{{ partner.data_entrada_sociedade }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Correlated Data -->
            <div v-if="results.correlated_data && results.correlated_data.length > 0" class="mt-4">
              <h5 class="card-title p-3">Correlated Data (CPF & CNPJ)</h5>
              <div class="table-container table-responsive">
                <table class="table table-dark table-striped table-hover m-0">
                  <thead>
                    <tr>
                      <th>CPF</th>
                      <th>Nome CPF</th>
                      <th>CNPJ Sócio</th>
                      <th>Nome Sócio</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="correlated in results.correlated_data" :key="correlated.cpf_info.cpf + correlated.partner_info.cpf_cnpj_socio">
                      <td>{{ correlated.cpf_info.cpf }}</td>
                      <td>{{ correlated.cpf_info.name }}</td>
                      <td>{{ correlated.partner_info.cnpj_basico }}</td>
                      <td>{{ correlated.partner_info.nome_socio }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ▸ ERROR ------------------------------------------------------------- -->
    <div v-if="error" class="alert alert-danger mt-4">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import api from '@/services/api'
import {useRouter} from "vue-router";

/* --- state --------------------------------------------------------------- */
const searchCriteria = ref({
  cpf: '',
  cnpj: '', // New CNPJ field
  name: '',
  birthdate: ''
})
const results = ref(null)
const loading = ref(false)
const error = ref(null)

/* --- pagination for CPF results ------------------------------------------ */
const cpfPage = ref(1) // Renamed from 'page'
const perPage = 100                                // ◄◄◄ agora 100 por página
const totalCpfPages = computed(() => // Renamed from 'totalPages'
  results.value && results.value.user_data
    ? Math.ceil(results.value.user_data.length / perPage)
    : 1
)
const pagedCpfResults = computed(() => // Renamed from 'pagedResults'
  results.value && results.value.user_data
    ? results.value.user_data.slice((cpfPage.value - 1) * perPage, cpfPage.value * perPage)
    : []
)
const goToCpfPage = n => { // Renamed from 'goToPage'
  if (n >= 1 && n <= totalCpfPages.value) cpfPage.value = n
}

/* --- API ----------------------------------------------------------------- */
let debounceTimer = null

const performSearch = async () => {
  // Basic validation for CPF and CNPJ
  const cleanCpf = searchCriteria.value.cpf.replace(/[^0-9]/g, '');
  const cleanCnpj = searchCriteria.value.cnpj.replace(/[^0-9]/g, '');

  if (cleanCpf && cleanCpf.length !== 11) {
    error.value = 'CPF must have 11 digits.';
    results.value = null;
    return;
  }
  if (cleanCnpj && cleanCnpj.length !== 14) {
    error.value = 'CNPJ must have 14 digits.';
    results.value = null;
    return;
  }

  // Only perform search if at least one criterion is not empty
  const hasSearchCriteria = Object.values(searchCriteria.value).some(criteria => criteria.length > 0);

  if (!hasSearchCriteria) {
    results.value = null; // Clear previous results
    error.value = 'Please enter at least one search criterion (CPF, CNPJ, Name, or Birthdate).';
    return;
  }

  loading.value = true
  error.value = null
  try {
    const { data } = await api.search(searchCriteria.value)
    results.value = data // Store the entire data object
    cpfPage.value = 1 // reset on new search
  } catch (err) {
    error.value = err.response ? err.response.data.error : err.message
    results.value = null
  } finally {
    loading.value = false
  }
}

const performSearchNow = () => {
  clearTimeout(debounceTimer)
  performSearch()
}

watch(
  searchCriteria,
  () => {
    clearTimeout(debounceTimer)
    debounceTimer = setTimeout(performSearch, 500)
  },
  { deep: true }
)

onMounted(performSearch)

/* ---------- estado de autenticação ------------------------------------ */
const isAuth = ref(false)
const router = useRouter()

function syncAuth() {
  isAuth.value = !!localStorage.getItem('token')
}

onMounted(() => {
  syncAuth()
  window.addEventListener('storage', syncAuth)
})
router.afterEach(syncAuth)

</script>

<style>
/* Remove padding que o Offcanvas às vezes injeta no body */
body {
  padding-right: 0 !important;
}

/* Altura máx. da tabela + header colado */
.table-container {
  max-height: 60vh;
  overflow: auto;
}
.table thead th {
  position: sticky;
  top: 0;
  z-index: 2;
}
</style>
