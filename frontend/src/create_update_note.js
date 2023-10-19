import { createApp } from 'vue'
import PrimeVue from 'primevue/config/config.esm.js';
import BadgeDirective from 'primevue/badgedirective/badgedirective.esm.js';
import ToastService from 'primevue/toastservice/toastservice.esm.js';
import App from './CreateUpdateNote.vue'
import "primevue/resources/themes/viva-light/theme.css"


const app = createApp(App)
app.use(PrimeVue, { ripple: true })
app.use(ToastService);
app.directive('badge', BadgeDirective);
app.mount('#app')
