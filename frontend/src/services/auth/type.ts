export enum AuthType {
    none = 0,
    jwt = 1,
    keycloak = 2,
}

export class AuthTypeService {
    private _type: AuthType = AuthType.none;

    constructor() {
        this.load();
    }

    private load() {
        const data = localStorage.getItem("authType");
        if (data) {
            const parsed = Number(data);
            this._type = isNaN(parsed) ? AuthType.none : parsed;
        }
    }

    private save() {
        localStorage.setItem("authType", this._type.toString());
    }

    setJWTAuth() {
        this._type = AuthType.jwt
        this.save()
    }

    setKeycloakAuth() {
        this._type = AuthType.keycloak
        this.save()
    }

    setNoneAuth() {
        this._type = AuthType.none
        this.save()
    }

    get type() {
        return this._type
    }

}

const authTypeService = new AuthTypeService();

export default authTypeService;
