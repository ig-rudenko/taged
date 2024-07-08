class LoginUser {
    username: string = ""
    password: string = ""
}

class UserTokens {
    constructor(
        public accessToken: string | null = null,
        public refreshToken: string | null = null
    ) {}
}

class User {
    constructor(
        public id: string,
        public username: string,
        public isSuperuser: boolean,
        public isStaff: boolean,
        public firstName?: string,
        public lastName?: string,
        public email?: string,
    ) {}
}

function createNewUser(data: any): User {
    return new User(
        data.id,
        data.username,
        data.is_superuser || data.isSuperuser,
        data.is_staff || data.isStaff,
        data.first_name || data.firstName,
        data.last_name || data.lastName,
        data.email
    )
}

export {LoginUser, UserTokens, User, createNewUser}