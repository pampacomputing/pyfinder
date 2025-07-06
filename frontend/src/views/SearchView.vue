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

                
                <div class="col-12">
                  <button type="submit" class="btn btn-primary me-2">Search CPF</button>
                  <button type="button" class="btn btn-info" @click="performCnpjSearch">Search CNPJ</button>
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
                      @click="selectCpfResult(result)"
                      :class="{ 'table-active': selectedCpfResult === result }"
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
            <div v-else-if="results.empresa && Object.keys(results.empresa).length > 0" class="mt-4">
              <h5 class="card-title p-3">Company Data (CNPJ)</h5>
              <div class="table-container table-responsive">
                <table class="table table-dark table-striped table-hover m-0">
                  <thead>
                    <tr>
                      <th>CNPJ</th>
                      <th>Razão Social</th>
                      <th>Nome Fantasia</th>
                      <th>Natureza Jurídica</th>
                      <th>Porte</th>
                      <th>Capital Social</th>
                      <th>Situação Cadastral</th>
                      <th>Data Situação Cadastral</th>
                      <th>Motivo Situação Cadastral</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      @click="selectCompany(results.empresa)"
                      :class="{ 'table-active': selectedCompanyData === results.empresa }"
                    >
                      <td>{{ results.cnpj }}</td>
                      <td>{{ results.empresa.razao_social }}</td>
                      <td>{{ results.empresa.nome_fantasia }}</td>
                      <td>{{ results.empresa.natureza_juridica.descricao }}</td>
                      <td>{{ results.empresa.porte }}</td>
                      <td>{{ results.empresa.capital_social }}</td>
                      <td>{{ results.empresa.situacao_cadastral.descricao }}</td>
                      <td>{{ results.empresa.situacao_cadastral.data }}</td>
                      <td>{{ results.empresa.situacao_cadastral.motivo.descricao }}</td>
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
                      <th>Nome</th>
                      <th>Sexo</th>
                      <th>Data de Nascimento</th>
                      <th>Qualificação Sócio</th>
                      <th>Data Entrada Sociedade</th>
                      <th>País</th>
                      <th>Representante Legal</th>
                      <th>Nome Representante</th>
                      <th>Qualificação Representante Legal</th>
                      <th>Faixa Etária</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(partner, partnerIdx) in results.socios" :key="partnerIdx">
                      <td>{{ partner.cpf }}</td>
                      <td>{{ partner.nome }}</td>
                      <td>{{ partner.sexo }}</td>
                      <td>{{ partner.data_nascimento }}</td>
                      <td>{{ partner.qualificacao_socio.descricao }}</td>
                      <td>{{ partner.data_entrada_sociedade }}</td>
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

            <!-- Associated Companies and Partners for Selected CPF -->
            <div v-if="selectedCpfResult && selectedCpfResult.associated_companies && selectedCpfResult.associated_companies.length > 0" class="mt-4">
              <h5 class="card-title p-3">Associated Companies for {{ selectedCpfResult.name }}</h5>
              <div v-for="(companyData, companyIdx) in selectedCpfResult.associated_companies" :key="companyIdx" class="mb-4">
                <h6>Company {{ companyIdx + 1 }}:</h6>
                <div class="table-container table-responsive mb-3">
                  <table class="table table-dark table-striped table-hover m-0">
                    <thead>
                      <tr>
                        <th>CNPJ Básico</th>
                        <th>Razão Social</th>
                        <th>Natureza Jurídica</th>
                        <th>Qualificação Responsável</th>
                        <th>Porte Empresa</th>
                        <th>Ente Federativo Responsável</th>
                        <th>Capital Social</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td>{{ companyData.company_details.cnpj_basico }}</td>
                        <td>{{ companyData.company_details.razao_social }}</td>
                        <td>{{ companyData.company_details.natureza_juridica }}</td>
                        <td>{{ companyData.company_details.company_details.qualificacao_responsavel }}</td>
                        <td>{{ companyData.company_details.porte_empresa }}</td>
                        <td>{{ companyData.company_details.ente_federativo_responsavel }}</td>
                        <td>{{ companyData.company_details.capital_social }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <h6>Partners for this Company:</h6>
                <div class="table-container table-responsive">
                  <table class="table table-dark table-striped table-hover m-0">
                    <thead>
                      <tr>
                        <th>CPF/CNPJ Sócio</th>
                        <th>Nome Sócio</th>
                        <th>Data de Nascimento</th>
                        <th>Gênero</th>
                        <th>Qualificação Sócio</th>
                        <th>Data Entrada Sociedade</th>
                        <th>País</th>
                        <th>Representante Legal</th>
                        <th>Nome Representante</th>
                        <th>Qualificação Representante Legal</th>
                        <th>Faixa Etária</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(partner, partnerIdx) in companyData.partners" :key="partnerIdx">
                        <td>{{ partner.cpf }}</td>
                        <td>{{ partner.nome }}</td>
                        <td>{{ partner.data_nascimento }}</td>
                        <td>{{ partner.genero }}</td>
                        <td>{{ partner.qualificacao_socio }}</td>
                        <td>{{ partner.data_entrada_sociedade }}</td>
                        <td>{{ partner.pais }}</td>
                        <td>{{ partner.representante_legal }}</td>
                        <td>{{ partner.nome_representante }}</td>
                        <td>{{ partner.qualificacao_representante_legal }}</td>
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
  cnpj: '', // Re-added CNPJ field
  name: '',
});
const results = ref(null)
const loading = ref(false)
const selectedCpfResult = ref(null) // New state for selected CPF result
const selectedCompanyData = ref(null) // New state for selected company data

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

const performSearch = async (searchType = 'cpf') => {
  
  // Basic validation for CPF and CNPJ
  const cleanCpf = searchCriteria.value.cpf.replace(/[^0-9]/g, '');
  const cleanCnpj = searchCriteria.value.cnpj.replace(/[^0-9]/g, '');

  if (searchType === 'cpf' && cleanCpf && cleanCpf.length !== 11) {
    results.value = null;
    return;
  }
  if (searchType === 'cnpj' && cleanCnpj && !/^\d{14}$/.test(cleanCnpj)) {
    results.value = null;
    return;
  }

  // Only perform search if at least one criterion is not empty
  const hasSearchCriteria = Object.values(searchCriteria.value).some(criteria => criteria.length > 0);

  if (!hasSearchCriteria) {
    results.value = null; // Clear previous results
    return;
  }

  loading.value = true
  selectedCpfResult.value = null // Clear selected CPF result on new search
  selectedCompanyData.value = null // Clear selected company data on new search
  selectedCompanyData.value = null // Clear selected company data on new search
  try {
    let responseData;
    if (searchType === 'cpf') {
      const { data } = await api.search({ cpf: cleanCpf, name: searchCriteria.value.name.toUpperCase() });
      responseData = data;
    } else if (searchType === 'cnpj') {
      const { data } = await api.search({ cnpj: cleanCnpj });
      responseData = data;
    }
    
    results.value = responseData // Store the entire data object
    cpfPage.value = 1 // reset on new search
  } catch (err) {
    results.value = null
  } finally {
    loading.value = false
  }
}

const performSearchNow = () => {
  clearTimeout(debounceTimer)
  performSearch('cpf') // Default to CPF search
}

const performCnpjSearch = async () => {
  clearTimeout(debounceTimer)
  const cleanCnpj = searchCriteria.value.cnpj.replace(/[^0-9]/g, '');

  if (!cleanCnpj || cleanCnpj.length !== 14) {
    alert("CNPJ must have 14 digits.");
    results.value = null;
    return;
  }

  if (!validateCnpjCheckDigits(cleanCnpj)) {
    alert("Invalid CNPJ check digits.");
    results.value = null;
    return;
  }

  loading.value = true;
  selectedCpfResult.value = null;
  selectedCompanyData.value = null;

  try {
    const { data } = await api.cnpjSearch({ cnpj: cleanCnpj });
    results.value = data;
  } catch (err) {
    console.error("CNPJ search error:", err);
    results.value = null;
    alert("Error searching CNPJ. Please try again.");
  } finally {
    loading.value = false;
  }
};

const validateCnpjCheckDigits = (cnpj) => {
  function calculateDv(cnpjPart, weights) {
    let total = 0;
    for (let i = 0; i < cnpjPart.length; i++) {
      total += parseInt(cnpjPart[i]) * weights[i];
    }
    let remainder = total % 11;
    return remainder < 2 ? 0 : 11 - remainder;
  }

  const cnpj12Digits = cnpj.substring(0, 12);
  const weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
  const dv1Calculated = calculateDv(cnpj12Digits, weights1);

  if (parseInt(cnpj[12]) !== dv1Calculated) {
    return false;
  }

  const cnpj13Digits = cnpj.substring(0, 13);
  const weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
  const dv2Calculated = calculateDv(cnpj13Digits, weights2);

  if (parseInt(cnpj[13]) !== dv2Calculated) {
    return false;
  }

  return true;
};

watch(
  searchCriteria,
  () => {
    clearTimeout(debounceTimer)
    // Only debounce if both CPF and CNPJ are empty, otherwise search immediately
    if (!searchCriteria.value.cpf && !searchCriteria.value.cnpj && !searchCriteria.value.name) {
      debounceTimer = setTimeout(() => performSearch('cpf'), 500);
    }
  },
  { deep: true }
)

onMounted(() => performSearch('cpf')) // Initial search on mount, default to CPF

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