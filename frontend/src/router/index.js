import { createRouter, createWebHistory } from 'vue-router'
import TheWelcome from '../components/TheWelcome.vue'
import SearchView from '../views/SearchView.vue'
import UserLoginView from '../views/UserLogin.vue'
import UserRegisterView from '../views/UserRegister.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: TheWelcome,
    },
    {
      path: '/login',
      name: 'login',
      component: UserLoginView
    },
    {
      path: '/register',
      name: 'register',
      component: UserRegisterView
    },
  {
      path: '/search',
      name: 'search',
      component: SearchView,
      meta: { requiresAuth: true }
    }
  ]
})

router.beforeEach((to, from, next) => {
  const loggedIn = localStorage.getItem('token');

  if (to.path === '/login' && loggedIn) {
    next('/search');
  } else if (to.matched.some(record => record.meta.requiresAuth) && !loggedIn) {
    next('/login');
  } else {
    next();
  }
});

export default router
