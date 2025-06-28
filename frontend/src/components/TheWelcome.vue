<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const handleScroll = () => {
  if (window.scrollY > 50) { // Adjust this value as needed
    document.body.classList.add('fade-out')
    setTimeout(() => {
      router.push('/login')
    }, 500); // Match this with the CSS transition duration
  }
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  document.body.classList.remove('fade-out') // Clean up class on unmount
})
</script>

<template>
  <div class="welcome-wrapper">
    <h1 class="main-title">Pyfinder</h1>
    <div class="scroll-message">
      <p>Scroll to login</p>
      <span class="arrow-down">&#x25BC;</span> <!-- Downward-pointing triangle character -->
    </div>
    
  </div>
  <div style="height: 100vh;"></div> <!-- Spacer to enable scrolling -->
</template>

<style scoped>
/* ---- layout principal ---- */
.welcome-wrapper {
  max-width: 960px;
  margin: 0 auto;
  padding: 2rem 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center; /* Center content vertically */
  min-height: calc(100vh - 60px); /* Adjust for potential header/footer */
}

.main-title {
  font-size: 6em; /* Increased font size */
  font-weight: 700;
  text-align: center;
  margin-bottom: 30px; /* Adjusted margin */
  color: var(--vt-c-text-1); /* Use a theme variable for text color */
}

.scroll-message {
  font-size: 1.8em; /* Increased font size */
  margin-top: 30px; /* Adjusted margin */
  display: flex;
  flex-direction: column;
  align-items: center;
  color: var(--vt-c-text-2); /* Use a theme variable for text color */
}

.arrow-down {
  font-size: 4em; /* Increased font size */
  animation: bounce 1s infinite;
  color: var(--vt-c-indigo); /* Use a theme variable for arrow color */
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-15px);
  }
  60% {
    transform: translateY(-7px);
  }
}


</style>

<style>
/* Global styles for transition */
body {
  transition: opacity 0.5s ease-in-out;
}

body.fade-out {
  opacity: 0;
}
</style>
