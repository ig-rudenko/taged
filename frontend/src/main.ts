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
import setupInterceptors from '@/services/api/setupInterceptors';
import router from "@/router";
import keycloakConnector from "@/keycloak.ts";
import {setTokens} from "@/services/auth/token.service.ts";
import authTypeService, {AuthType} from "@/services/auth/type.ts";

setupInterceptors();
export const app = createApp(App);
app.use(PrimeVue, {ripple: true});
app.use(ToastService);
app.directive('badge', BadgeDirective);
app.directive('tooltip', Tooltip);

app.use(store);
app.use(router);
app.config.globalProperties.$router = router as Router;

if (authTypeService.type != AuthType.jwt) {
    keycloakConnector.initKeycloak().then(() => {
        if (!keycloakConnector.enabled) return;  // Если OIDC вышлючен на backend.

        if (window.location.hash) {
            history.replaceState(null, "", window.location.pathname + window.location.search);
        }

        // Если вошли через OIDC.
        if (keycloakConnector.keycloakLoginState.isLogin) {
            keycloakConnector.autoRefreshToken(setTokens);  // Автоматическое обновление токена.
            store.dispatch('auth/keycloakLogin')
        }

        // Если необходимо авторизоваться.
        if (keycloakConnector.keycloakLoginState.autoLogin) {
            store.dispatch('auth/keycloakLogin').then(
                () => setTimeout(() => location.href = "/", 100)
            )
            keycloakConnector.keycloakLoginState.deleteAutoLogin()
        }
    });
}

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
