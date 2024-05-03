import {AxiosError} from "axios";

export function getVerboseAxiosError(error: AxiosError<any>): string {
    console.log(error)
    if (error.response?.data) {
        const detail = error.response.data
        console.log(detail)

        let validationErrors = ""
        for (const key of Object.keys(detail)) {
            validationErrors += key.toString() + ": " + detail[key].toString() + "<br>"
        }
        return validationErrors

    }
    return error.message
}
