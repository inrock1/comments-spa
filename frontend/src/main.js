import { createApp } from 'vue'
import axios from 'axios'
import App from './App.vue'

const app = createApp(App)

app.config.globalProperties.$axios = axios

app.mount('#app')
