import {AxiosError} from "axios";

export function getVerboseAxiosError(error: AxiosError<any>): string {
    if (error.response?.data) {
        const detail = error.response.data

        let validationErrors = ""
        for (const key of Object.keys(detail)) {
            validationErrors += key.toString() + ": " + detail[key].toString()
        }
        return validationErrors

    }
    return error.message
}
