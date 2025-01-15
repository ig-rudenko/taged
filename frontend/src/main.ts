import {createApp} from 'vue';
import PrimeVue from 'primevue/config';
import {Router} from "vue-router";

import BadgeDirective from 'primevue/badgedirective';
import AutoComplete from "primevue/autocomplete";
import Badge from "primevue/badge";
import Button from "primevue/button";
import ContextMenu from "primevue/contextmenu";
import Dialog from "primevue/dialog";
import Image from "primevue/image";
import InputNumber from "primevue/inputnumber";
import InputSwitch from "primevue/inputswitch";
import InputText from "primevue/inputtext";
import InlineMessage from "primevue/inlinemessage";
import MultiSelect from "primevue/multiselect";
import OverlayPanel from "primevue/overlaypanel";
import ScrollPanel from "primevue/scrollpanel";
import ScrollTop from "primevue/scrolltop";
import Tag from "primevue/tag";
import ToastService from 'primevue/toastservice';
import Tooltip from "primevue/tooltip";

// import "primevue/resources/themes/viva-light/theme.css";
import App from './App.vue';
import store from "@/store";
import setupInterceptors from '@/services/setupInterceptors';
import router from "@/router";

setupInterceptors(store);
export const app = createApp(App);
app.use(PrimeVue, {ripple: true});
app.use(ToastService);
app.directive('badge', BadgeDirective);
app.directive('tooltip', Tooltip);

app.use(store);
app.use(router);
app.config.globalProperties.$router = router as Router;

app.component('AutoComplete', AutoComplete);
app.component('Badge', Badge);
app.component('Button', Button);
app.component('ContextMenu', ContextMenu);
app.component('Dialog', Dialog);
app.component('Image', Image);
app.component('InlineMessage', InlineMessage);
app.component('InputNumber', InputNumber);
app.component('InputSwitch', InputSwitch);
app.component('InputText', InputText);
app.component('MultiSelect', MultiSelect);
app.component('OverlayPanel', OverlayPanel);
app.component('ScrollPanel', ScrollPanel);
app.component('ScrollTop', ScrollTop);
app.component('Tag', Tag);

app.mount('#app');
