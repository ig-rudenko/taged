import api from "@/services/api.ts";
import {v4 as uuidv4} from "uuid";


export class EditService {
    private readonly id: string;

    constructor() {
        this.id = uuidv4();
    }

    setBeingEdited(noteID: string) {
        const data = {
            note: noteID,
            editor: this.id
        }
        return api.post('/notes/editors', data);
    }

    async isBeingEdited(noteID: string): Promise<boolean> {
        const resp = await api.get<string[]>('/notes/editors/' + noteID);
        return resp.data.indexOf(this.id) !== -1 && resp.data.length > 1;
    }
}
