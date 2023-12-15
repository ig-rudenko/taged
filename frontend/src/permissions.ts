class UserPermissions {

    constructor(private perms: Array<string>) {}

    public get hasPermissionToCreateNote(): boolean {
        return this.perms.includes("create_notes")
    }
    public get hasPermissionToUpdateNote(): boolean {
        return this.perms.includes("update_notes")
    }
    public get hasPermissionToDeleteNote(): boolean {
      return this.perms.includes("delete_notes")
    }
}

export {UserPermissions}