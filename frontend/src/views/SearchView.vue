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
                    v-for="(result, idx) in pagedResults"
                    :key="result.cpf"
                  >
                    <td>{{ (page - 1) * perPage + idx + 1 }}</td>
                    <td>{{ result.cpf }}</td>
                    <td>{{ result.name }}</td>
                    <td>{{ result.date }}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- ▸ PAGINATION ------------------------------------------------ -->
            <nav v-if="totalPages > 1" class="mt-3">
              <ul class="pagination justify-content-center mb-0">
                <li class="page-item" :class="{ disabled: page === 1 }">
                  <button class="page-link" @click="page--">«</button>
                </li>

                <li
                  class="page-item"
                  v-for="n in totalPages"
                  :key="n"
                  :class="{ active: n === page }"
                >
                  <button class="page-link" @click="goToPage(n)">{{ n }}</button>
                </li>

                <li class="page-item" :class="{ disabled: page === totalPages }">
                  <button class="page-link" @click="page++">»</button>
                </li>
              </ul>
            </nav>
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
  name: '',
  birthdate: ''
})
const results = ref(null)
const loading = ref(false)
const error = ref(null)

/* --- pagination ---------------------------------------------------------- */
const page = ref(1)
const perPage = 100                                // ◄◄◄ agora 100 por página
const totalPages = computed(() =>
  results.value ? Math.ceil(results.value.length / perPage) : 1
)
const pagedResults = computed(() =>
  results.value
    ? results.value.slice((page.value - 1) * perPage, page.value * perPage)
    : []
)
const goToPage = n => {
  if (n >= 1 && n <= totalPages.value) page.value = n
}

/* --- API ----------------------------------------------------------------- */
let debounceTimer = null

const performSearch = async () => {
  // Only perform search if at least one criterion is not empty and has minimum length (if applicable)
  const hasSearchCriteria = Object.values(searchCriteria.value).some(criteria => criteria.length >= 3 || criteria.length === 0);

  if (!hasSearchCriteria && (searchCriteria.value.cpf || searchCriteria.value.name || searchCriteria.value.birthdate)) {
    // If criteria exist but don't meet min length, don't search
    results.value = []; // Clear previous results
    return;
  }

  loading.value = true
  error.value = null
  try {
    const { data } = await api.search(searchCriteria.value)
    results.value = data.user_data
    page.value = 1 // reset on new search
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
