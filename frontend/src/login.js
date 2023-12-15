import { createApp } from 'vue'
import PrimeVue from 'primevue/config/config.esm.js';
import App from './Login.vue'
import "primevue/resources/themes/viva-light/theme.css"

const app = createApp(App)
app.use(PrimeVue, { ripple: true })
app.mount('#app')
