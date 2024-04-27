import { createApp } from 'vue';
import PrimeVue from 'primevue/config';
import Tooltip from "primevue/tooltip";
import ToastService from 'primevue/toastservice';
import BadgeDirective from 'primevue/badgedirective';
import "primevue/resources/themes/viva-light/theme.css";
import "@/assets/styles.min.css"
import "@/assets/main.css"

import {Router} from "vue-router";
import Button from "primevue/button";
import InlineMessage from "primevue/inlinemessage/InlineMessage.vue";
import InputText from "primevue/inputtext";

import App from './App.vue';
import store from "@/store";
import setupInterceptors from '@/services/setupInterceptors';
import router from "@/router";

setupInterceptors(store);
const app = createApp(App);
app.use(PrimeVue, { ripple: true });
app.use(ToastService);
app.directive('tooltip', Tooltip);
app.use(store);
app.use(router);
app.config.globalProperties.$router = router as Router;

app.directive('badge', BadgeDirective);


app.component('Button', Button);
app.component('InlineMessage', InlineMessage);
app.component('InputText', InputText);

app.mount('#app');
