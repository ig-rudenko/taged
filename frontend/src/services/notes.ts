import {v4 as uuidv4} from 'uuid';

import api from "@/services/api";
import {NoteSearchFilter} from "@/filters";
import {getVerboseAxiosError} from "@/errorFmt";
import {errorToast, successToast} from "@/services/myToast";
import {DetailNote, getFiles, newDetailNote, Note, NoteDraft} from "@/note";


interface Paginator {
    currentPage: number
    maxPages: number
    perPage: number
}

interface OriginRecord {
    filesCount: number
    id: string
    preview_image: string
    published_at: string
    score: number
    tags: string[]
    title: string
}

interface OriginNotesPaginateResult {
    paginator: Paginator
    totalRecords: number
    records: OriginRecord[]
}

interface NotesPaginateResult {
    paginator: Paginator
    totalRecords: number
    notes: DetailNote[]
}


class NotesService {

    async getPermissions() {
        try {
            let resp = await api.get("/notes/permissions")
            return resp.data
        } catch (error: any) {
            let text = "Не удалось загрузить ваши полномочия\n" + getVerboseAxiosError(error);
            errorToast(`Error: ${error.response.status}`, text);
            throw error;
        }
    }

    async getAvailableTags() {
        // Получаем доступные пользователем теги
        try {
            let resp = await api.get<string[]>("/notes/tags");
            return resp.data;
        } catch (error: any) {
            let text = "Не удалось загрузить ТЕГИ\n" + getVerboseAxiosError(error);
            errorToast(`Error: ${error.response.status}`, text);
            throw error;
        }
    }

    async autocomplete(query: string) {
        let value = await api.get<string[]>("/notes/autocomplete?term=" + query);
        return value.data;
    }

    async findNotes(filter: NoteSearchFilter, currentPage: number): Promise<NotesPaginateResult> {
        const params = filter.getParams()
        const filterParamsString = filter.getParamsString()

        params.append("page", String(currentPage))

        history.pushState({path: "/" + filterParamsString}, '', "/" + filterParamsString);

        const URL = "/notes/?" + params.toString()

        const getDetailNotes = (data: any[]): Array<DetailNote> => {
            let res: Array<DetailNote> = []
            for (const note of data) {
                res.push(newDetailNote(note))
            }
            return res
        }

        try {
            const resp = await api.get<OriginNotesPaginateResult>(URL)
            return {
                notes: getDetailNotes(resp.data.records),
                totalRecords: resp.data.totalRecords,
                paginator: resp.data.paginator
            }

        } catch (error: any) {
            let text = "Не удалось загрузить записи\n" + getVerboseAxiosError(error);
            errorToast(`Error: ${error.response.status}`, text);
            throw error;
        }
    }

    async getNoteFiles(noteID: string) {
        try {
            const resp = await api.get("/notes/" + noteID + "/files")
            return getFiles(resp.data)
        } catch (error: any) {
            let text = "Не удалось загрузить Файлы записи\n" + getVerboseAxiosError(error);
            errorToast(`Error: ${error.response.status}`, text);
            throw error;
        }
    }

    async getNote(id: string): Promise<DetailNote> {
        try {
            let resp = await api.get<any>("/notes/" + id);
            const note = newDetailNote(resp.data);
            note.id = id;
            return note
        } catch (error: any) {
            let text = "Не удалось загрузить запись";
            errorToast(`Error: ${error.response.status}`, text);
            throw error;
        }
    }

    async updateNote(note: Note, filesForm: FormData) {
        try {
            const resp = await api.put("/notes/" + note.id, note)

            if (resp.status === 200 || resp.status === 201) {
                this.deleteUnusedFiles(note)
                await this.uploadNewFiles(note.id, filesForm)
                successToast("Обновлено!", `Запись "${note.title}" была обновлена!`)
            } else {
                errorToast(`Error: ${resp.status}`, resp.data);
            }
        } catch (error: any) {
            errorToast('Error', getVerboseAxiosError(error));
            throw error;
        }
    }

    async createNote(note: Note, filesForm: FormData) {
        try {
            // Иначе создаем новую заметку
            const resp = await api.post("/notes/", note)

            if (resp.status === 200 || resp.status === 201) {
                await this.uploadNewFiles(resp.data.id, filesForm)
                successToast("Создано!", `Запись "${resp.data.title}" была создана!`)
            } else {
                errorToast(`Error: ${resp.status}`, resp.data);
            }
        } catch (error: any) {
            errorToast('Error', getVerboseAxiosError(error));
            throw error;
        }
    }

    async deleteNote(noteID: string) {
        try {
            return api.delete("/notes/" + noteID)
        } catch (error: any) {
            errorToast('Error', getVerboseAxiosError(error));
            throw error;
        }
    }

    async getTempLink(noteID: string, duration: number) {
        try {
            const resp = await api.post<{ link: string }>(
                '/notes/temp/' + noteID,
                {minutes: duration}
            )
            return document.location.origin + resp.data.link
        } catch (error: any) {
            let text = "Не удалось создать временную ссылку\n";
            errorToast('Error', text + getVerboseAxiosError(error));
            throw error;
        }
    }


    private deleteUnusedFiles(note: Note) {
        // Если заметка редактировалась, то проверяем файлы, которые уже существовали
        for (const file of note.files) {
            if (!file.disable) continue;

            // Удаляем файлы, которые были отключены
            api.delete("/notes/" + note.id + '/files/' + file.name).catch(
                reason => {
                    errorToast(`Error: ${reason.response.status}`, reason.response.data)
                }
            )
        }
    }

    /**
     * Обновляем файлы заметки
     * @param {String} noteId
     * @param {FormData} filesForm
     */
    private async uploadNewFiles(noteId: string, filesForm: FormData) {

        // Загружаем новые добавленные файлы
        const resp = await api.post("/notes/" + noteId + '/files', filesForm, {
            headers: {
                "Content-Type": "multipart/form-data",
            }
        })
        const data = await resp.data

        if (resp.status !== 201) errorToast(`Error: ${resp.status}`, data);
    }

    async getDraftsList(): Promise<NoteDraft[]> {
        try {
            const resp = await api.get<NoteDraft[]>("/drafts/")
            return resp.data
        } catch (error: any) {
            console.log("getDraftsList", error)
            return []
        }
    }

    async getDraft(id: string): Promise<NoteDraft | undefined> {
        try {
            const resp = await api.get<NoteDraft>(`/drafts/${id}/`)
            return resp.data
        } catch (error: any) {
        }
    }

    async createDraft(note: Note): Promise<NoteDraft> {
        const id = uuidv4();
        return await this.saveDraft(id, note)
    }

    async saveDraft(id: string, note: Note): Promise<NoteDraft> {
        const data = {
            id: id,
            title: note.title,
            content: note.content,
            tags: note.tags,
        }
        const resp = await api.post<NoteDraft>("/drafts/", data)
        return resp.data
    }

    async deleteDraft(id: string) {
        await api.delete(`/drafts/${id}/`)
    }

}

const notesService = new NotesService();
export default notesService;
