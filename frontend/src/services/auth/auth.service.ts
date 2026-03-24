import axios from "axios";

import {LoginUser} from "@/user";
import UserService from "@/services/auth/user.service";
import {tokenService} from "@/services/auth/token.service";
import keycloakConnector from "@/keycloak";
import authTypeService from "@/services/auth/type.ts";

class AuthService {
    async login(user: LoginUser) {
        let response = await axios.post("/api/auth/token/", {
            username: user.username,
            password: user.password
        });
        tokenService.setTokens(response.data.access, response.data.refresh);
        authTypeService.setJWTAuth()
        return response
    }

    async keycloakLogin() {
        const {access, refresh} = keycloakConnector.getTokens()
        console.log(access, refresh)
        if (access && refresh) {
            keycloakConnector.keycloakLoginState.setLogin()  // OIDC используется для входа.
            tokenService.setTokens(access, refresh)
            authTypeService.setKeycloakAuth()
            return Promise.resolve()
        }
        return Promise.reject()
    }

    async logout() {
        keycloakConnector.keycloakLoginState.deleteAutoLogin()
        keycloakConnector.keycloakLoginState.setLogout()  // Выход из OIDC
        tokenService.removeTokens();
        UserService.removeUser();
        authTypeService.setNoneAuth();

        // Очищаем всё хранилище.
        localStorage.clear();
    }

}

export default new AuthService();