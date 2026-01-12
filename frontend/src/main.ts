import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './assets/main.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

// Apply saved theme before mounting to avoid flash
const savedTheme = localStorage.getItem('theme') || 'mediaflow'
document.documentElement.setAttribute('data-theme', savedTheme)

app.mount('#app')
