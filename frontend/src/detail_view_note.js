import { createApp } from 'vue';
import PrimeVue from 'primevue/config/config.esm.js';
import App from './DetailViewNote.vue';
import ToastService from 'primevue/toastservice/toastservice.esm.js';
import "primevue/resources/themes/viva-light/theme.css";


const app = createApp(App);
app.use(PrimeVue, { ripple: true });
app.use(ToastService);
app.mount('#app');
