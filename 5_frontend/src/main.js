import Vue from 'vue'
import App from './App.vue'
import Home from './pages/Home.vue'
import Resume from './pages/Resume.vue'
import Stats from './pages/Stats.vue'
import VueRouter from 'vue-router'

Vue.use(VueRouter)
Vue.config.productionTip = false

const routes = [
  { path: '/', component: Home },
  { path: '/resume', component: Resume },
  { path: '/stats', component: Stats },
  { path: '*', redirect: '/' }
]

const router = new VueRouter({
  routes
})

new Vue({
  render: h => h(App),
  router
}).$mount('#app')
