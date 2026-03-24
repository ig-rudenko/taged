import Keycloak from "keycloak-js";
import axios from "axios";


class KeycloakLoginState {
    setAutoLogin() {
        localStorage.setItem("keycloak-auto-login", "true")
    }

    deleteAutoLogin() {
        localStorage.removeItem("keycloak-auto-login")
    }

    get autoLogin(): boolean {
        return localStorage.getItem("keycloak-auto-login") === "true"
    }

    setLogin() {
        localStorage.setItem("keycloak-login", "true")
    }

    setLogout() {
        localStorage.removeItem("keycloak-login")
    }

    get isLogin(): boolean {
        return localStorage.getItem("keycloak-login") === "true"
    }
}

class KeycloakConfigState {
    setConfig(config: OIDCConfig) {
        localStorage.setItem("keycloak-config-state", JSON.stringify(config))
    }

    getConfig(): OIDCConfig | null {
        return JSON.parse(localStorage.getItem("keycloak-config-state") || "null") as OIDCConfig | null
    }
}


export interface OIDCConfig {
    enabled: boolean;
    url: string;
    clientId: string;
    realm: string;
}


class KeycloakConnector {
    public _keycloak: Keycloak | null = null
    public keycloakLoginState: KeycloakLoginState = new KeycloakLoginState()
    private configState: KeycloakConfigState = new KeycloakConfigState()
    public isKeycloakInitialized: boolean = false;
    public refreshTokenTimeout: number = 30000;  // Таймаут для обновления токена в мс.
    public enabled: boolean = false;

    get keycloak(): Keycloak {
        if (this._keycloak) return this._keycloak;
        throw new Error("Keycloak not initialized")
    }

    async getOIDConfig(): Promise<OIDCConfig> {
        const config = this.configState.getConfig()
        if (config) return config;
        const resp = await axios.get<OIDCConfig>('/api/oidc/config')
        this.configState.setConfig(resp.data);
        return resp.data;
    }

    async initKeycloak() {
        // Если уже инициализирован, не делаем повторную инициализацию
        if (this.isKeycloakInitialized) {
            return
        }
        try {
            const config = await this.getOIDConfig()
            this.enabled = config.enabled
            if (!this.enabled) return;

            this._keycloak = new Keycloak({
                url: config.url,
                realm: config.realm,
                clientId: config.clientId,
            })
            await this.keycloak.init({
                onLoad: "check-sso",
                pkceMethod: "S256",
                checkLoginIframe: false,
            });
            this.isKeycloakInitialized = true;

        } catch (e) {
            console.error("Keycloak init error:", e);
        }
    }

    autoRefreshToken(callback: null | ((access: string, refresh: string) => void) = null) {
        const update = async () => {
            await this.keycloak.updateToken(this.refreshTokenTimeout + 10)
            if (callback && this.keycloak.token && this.keycloak.refreshToken) {
                callback(this.keycloak.token, this.keycloak.refreshToken)
            }
            setTimeout(update, this.refreshTokenTimeout)
        }
        setTimeout(update, this.refreshTokenTimeout)
    }

    getTokens(): { access: string, refresh: string } {
        if (this.keycloak.token && this.keycloak.refreshToken) {
            return {access: this.keycloak.token, refresh: this.keycloak.refreshToken}
        }
        return {access: "", refresh: ""}
    }

}


const keycloakConnector = new KeycloakConnector()
export default keycloakConnector


// https://auth.net92.ru/realms/sevtelecom/protocol/openid-connect/auth?client_id=knowledge-base-dev&redirect_uri=http%3A%2F%2Flocalhost%3A5173%2F&state=20aa2142-62d5-4903-a616-71878f972c77&response_mode=fragment&response_type=code&scope=openid&nonce=e95624d8-784b-42b4-a464-9c1acf5c1d65&prompt=none&code_challenge=_aPzqAuNSHR1sSg7yn-ZYiyKQ-gsZ2v9C5WN8Q4Q_EY&code_challenge_method=S256

// https://auth.net92.ru/realms/sevtelecom/protocol/openid-connect/auth?client_id=knowledge-base-dev&redirect_uri=http%3A%2F%2Flocalhost%3A5173%2Flogin%23state%3D2b9d7713-d342-4cdb-b16b-49492e8f97c2%26session_state%3Dcef7b446-ad4a-8dad-3b7c-c9c527630c4c%26iss%3Dhttps%253A%252F%252Fauth.net92.ru%252Frealms%252Fsevtelecom%26code%3Dee34959d-2d44-9696-fae9-346880d44b6f.cef7b446-ad4a-8dad-3b7c-c9c527630c4c.32e4ef7b-8aa8-425f-9797-1a5e5abe11ce&state=3a5a1cd1-e6b7-4960-b44c-f69895d01163&response_mode=fragment&response_type=code&scope=openid&nonce=ac7c9716-783c-45e9-b6fc-6d62f1955356&code_challenge=K4TMh41F45iofNyVo5-1bIMoLF9uZfYtkYCubU1bFh0&code_challenge_method=S256

// https://auth.net92.ru/realms/sevtelecom/protocol/openid-connect/auth?client_id=knowledge-base-dev&redirect_uri=http%3A%2F%2Flocalhost%3A5173%2Flogin%23error%3Dlogin_required%26state%3D5c462db4-7c25-4110-8fd8-414131f121eb%26iss%3Dhttps%253A%252F%252Fauth.net92.ru%252Frealms%252Fsevtelecom%26state%3Ddacbff55-9256-429a-b4c6-65b06d1ad73b%26session_state%3D6a1e63b6-d79b-d545-1823-d58c14627dca%26iss%3Dhttps%253A%252F%252Fauth.net92.ru%252Frealms%252Fsevtelecom%26code%3D7605979d-0f42-b955-500c-33831104f600.6a1e63b6-d79b-d545-1823-d58c14627dca.32e4ef7b-8aa8-425f-9797-1a5e5abe11ce&state=b2d218b7-d598-46f8-945d-0283c93c0fa5&response_mode=fragment&response_type=code&scope=openid&nonce=7f6a57ad-668c-4748-8e7a-80af27343d56&code_challenge=M8d6AlZMamx7Nkc5-N1H13o7_OLi58Z9YoAquaa3Tbo&code_challenge_method=S256
