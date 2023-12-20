class NoteValidator {
    constructor(
        public title: boolean = true,
        public content: boolean = true,
        public tags: boolean = true,
    ) { }

    public get isValid() {
        return this.tags && this.title && this.content
    }
}


class NoteFile {
    constructor(
        public name: string,
        public size: number,
        public type: string,
        public disable: boolean = false,
    ) {}
}

class Note {
    private _valid: NoteValidator = new NoteValidator()
    constructor(
        public id: string = "",
        public title: string = "",
        public content: string = "",
        public tags: Array<string> = [],
        public files: Array<NoteFile> = [],
    ) { }

    public get valid() {
        this.isValid()
        return this._valid
    }

    public isValid() {
      this._valid.title = this.title.length !== 0
      this._valid.tags = this.tags.length !== 0
      this._valid.content = this.content.length !== 0
      return this._valid.isValid
    }


}


class DetailNote extends Note {
    constructor(
        public id: string,
        public title: string,
        public content: string,
        public tags: Array<string>,
        public files: Array<NoteFile>,
        public filesCount: number,
        public published_at: string = "",
        public previewImage: string = "",
        public score: number = 0,
    ) {
        super();
    }

    public get scorePercents(): number {
        return Math.round(this.score * 100)
    }
}

function getFiles(data: Array<any>): Array<NoteFile> {
    let files: Array<NoteFile> = []
    for (const file of data) {
        files.push(new NoteFile(file.name, file.size, file.type, false))
    }
    return files
}

function createNewNote(data: any): Note {
    return new Note(
        data.id, data.title, data.content, data.tags, getFiles(data.files)
    )
}

function newDetailNote(data: any): DetailNote {
    return new DetailNote(
        data.id, data.title, data.content, data.tags, getFiles(data.files || []), data.filesCount,
        data.published_at, data.previewImage, data.score
    )
}



export {NoteFile, Note, DetailNote, createNewNote, newDetailNote, getFiles}