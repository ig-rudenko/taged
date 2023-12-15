import axios, {AxiosInstance} from "axios"

const tokenItem = <HTMLInputElement>document.querySelector("input[name=csrfmiddlewaretoken]")

const token = tokenItem?tokenItem.value:""

const api_request: AxiosInstance = axios.create({
    headers: {
        // Добавляем токен в заголовок "X-CSRFToken"
        'X-CSRFToken': token
    }
});

export default api_request