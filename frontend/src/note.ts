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
    public valid: NoteValidator = new NoteValidator()
    constructor(
        public id: string = "",
        public title: string = "",
        public content: string = "",
        public tags: Array<string> = [],
        public files: Array<NoteFile> = [],
    ) {}

    public isValid() {
      this.valid.title = this.title.length !== 0
      this.valid.tags = this.tags.length !== 0
      this.valid.content = this.content.length !== 0
      return this.valid.isValid
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

function newDetailNote(data: any): DetailNote {
    return new DetailNote(
        data.id, data.title, data.content, data.tags, getFiles(data.files || []), data.filesCount,
        data.published_at, data.preview_image, data.score
    )
}



export {NoteFile, Note, DetailNote, newDetailNote, getFiles}