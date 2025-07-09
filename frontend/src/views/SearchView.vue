<!-- src/views/SearchView.vue -->
<template>
  <div class="container-fluid mt-4 px-0">
    <h1 class="mb-4 text-center">PyFinder – Advanced Search</h1>

    <!-- ▸ SEARCH CRITERIA --------------------------------------------------- -->
    <div class="row justify-content-center gx-0">
      <div class="col-12 col-lg-10 col-xxl-8 px-0">
        <SearchBar
          :search-criteria="searchCriteria"
          @update:searchCriteria="updateSearchCriteria"
          @performSearchNow="performSearchNow"
          @performCnpjSearch="performCnpjSearch"
          @validationError="handleValidationError"
        />
      </div>
    </div>

    <!-- ▸ LOADING ----------------------------------------------------------- -->
    <div v-if="loading" class="text-center mt-4">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading…</span>
      </div>
    </div>

    <!-- ▸ SEARCH RESULTS ---------------------------------------------------- -->
    <SearchResult
      :results="results"
      :selected-cpf-result="selectedCpfResult"
      :cpf-page="cpfPage"
      :per-page="perPage"
      :total-cpf-pages="totalCpfPages"
      :paged-cpf-results="pagedCpfResults"
      @get-associated-companies="getAssociatedCompanies"
      @update:cpfPage="cpfPage = $event"
      @go-to-cpf-page="goToCpfPage"
    />

    <InfoModal
      :is-visible="showInfoModal"
      :message="modalMessage"
      @close="showInfoModal = false"
    />
   </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import api from '@/services/api'
import {useRouter} from "vue-router";
import InfoModal from '@/components/InfoModal.vue';
import SearchBar from '@/components/SearchBar.vue';
import SearchResult from '@/components/SearchResult.vue';

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
const showInfoModal = ref(false);
const modalMessage = ref('');

const updateSearchCriteria = (newCriteria) => {
  searchCriteria.value = newCriteria;
};

const handleValidationError = (message) => {
  modalMessage.value = message;
  showInfoModal.value = true;
};

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

import unidecode from 'unidecode';

/* --- API ----------------------------------------------------------------- */
let debounceTimer = null
let latestRequest = null;

const performSearch = async (searchType = 'cpf') => {
  const currentRequest = Symbol();
  latestRequest = currentRequest;

  // Basic validation for CPF and CNPJ
  const cleanCpf = searchCriteria.value.cpf.replace(/[^0-9]/g, '');
  const cleanCnpj = searchCriteria.value.cnpj.replace(/[^0-9]/g, '');
  const normalizedName = unidecode(searchCriteria.value.name.toUpperCase());

  if (searchType === 'cpf' && cleanCpf && cleanCpf.length !== 11) {
    results.value = null;
    return;
  }
  if (searchType === 'cnpj' && cleanCnpj && !/^\d{14}$/.test(cleanCnpj)) {
    results.value = null;
    return;
  }

  // Always perform search if there's a token, even if criteria are empty
  // This ensures the 401 interceptor is triggered if the token is invalid
  const hasSearchCriteria = Object.values(searchCriteria.value).some(criteria => criteria.length > 0);

  if (!hasSearchCriteria && !localStorage.getItem('token')) {
    results.value = null; // Clear previous results
    return;
  }

  loading.value = true
  selectedCpfResult.value = null // Clear selected CPF result on new search
  selectedCompanyData.value = null // Clear selected company data on new search
  try {
    let responseData;
    if (searchType === 'cpf') {
      const { data } = await api.search({ cpf: cleanCpf, name: normalizedName });
      responseData = data;
    } else if (searchType === 'cnpj') {
      const { data } = await api.search({ cnpj: cleanCnpj });
      responseData = data;
    }

    if (latestRequest === currentRequest) {
      results.value = responseData // Store the entire data object
      cpfPage.value = 1 // reset on new search
    }
  } catch {
    if (latestRequest === currentRequest) {
      results.value = null
    }
  } finally {
    if (latestRequest === currentRequest) {
      loading.value = false
    }
  }
}

const getAssociatedCompanies = async (personName, personCpf) => {
  const currentRequest = Symbol();
  latestRequest = currentRequest;

  if (selectedCpfResult.value && selectedCpfResult.value.name === personName) {
    selectedCpfResult.value = null;
    return;
  }

  if (!personName) return;
  loading.value = true;
  try {
    const { data } = await api.getCompaniesByName(personName, personCpf);
    if (latestRequest === currentRequest) {
      const resultToUpdate = results.value.user_data.find(user => user.name === personName);
      if (resultToUpdate) {
        if (data.associated_companies && data.associated_companies.length > 0) {
          resultToUpdate.associated_companies = data.associated_companies;
          selectedCpfResult.value = resultToUpdate;
        } else {
          modalMessage.value = "There is no company linked to this CPF";
          showInfoModal.value = true;
          selectedCpfResult.value = null; // Ensure no table is shown
        }
      }
    }
  } catch (err) {
    console.error("Error fetching associated companies:", err);
  } finally {
    if (latestRequest === currentRequest) {
      loading.value = false;
    }
  }
};

const performSearchNow = async () => {
  clearTimeout(debounceTimer);
  await performSearch('cpf'); // Default to CPF search
  searchCriteria.value.name = '';
  searchCriteria.value.cpf = '';
};

const performCnpjSearch = async () => {
  const currentRequest = Symbol();
  latestRequest = currentRequest;

  clearTimeout(debounceTimer);
  loading.value = true;
  selectedCpfResult.value = null;
  selectedCompanyData.value = null;

  try {
    const { data } = await api.cnpjSearch({ cnpj: searchCriteria.value.cnpj });
    if (latestRequest === currentRequest) {
      results.value = data;
    }
  } catch (err) {
    console.error("CNPJ search error:", err);
    if (latestRequest === currentRequest) {
      results.value = null;
      modalMessage.value = "Error searching CNPJ. Please try again.";
      showInfoModal.value = true;
    }
  } finally {
    if (latestRequest === currentRequest) {
      loading.value = false;
      searchCriteria.value.cnpj = '';
    }
  }
};

onMounted(() => {
  // Make an initial API call to a protected endpoint to validate the session
  // This will trigger the 401 interceptor if the token is invalid
  api.search({}).catch(() => {}); // Catch the error to prevent console warnings
  performSearch('cpf'); // Initial search on mount, default to CPF
})

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

</style>
