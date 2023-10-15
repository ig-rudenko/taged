import { createApp } from 'vue'
import PrimeVue from 'primevue/config';
import BadgeDirective from 'primevue/badgedirective';
import App from './Notes.vue'
import "primevue/resources/themes/viva-light/theme.css"


const app = createApp(App)
app.use(PrimeVue, { ripple: true })
app.directive('badge', BadgeDirective);
app.mount('#app')
