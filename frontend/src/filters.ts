class NoteSearchFilter {
    constructor(
        public search: string = "",
        public tags: string[] = [],
        public use_vectorizer: boolean = false,
        public vectorizer_only: boolean = false,
    ) {
    }

    toggleVectorSearch(): void {
        if (this.use_vectorizer) {
            this.use_vectorizer = false;
            this.vectorizer_only = false;
        } else {
            this.use_vectorizer = true;
            this.vectorizer_only = false;
        }
    }

    getParams(): URLSearchParams {
        const params = new URLSearchParams();
        if (this.search.length > 0) params.append("search", this.search);
        for (const tag of this.tags) {
            params.append("tags-in", tag);
        }
        if (this.use_vectorizer) { params.append("use-vectorizer", "true"); }
        if (this.vectorizer_only) { params.append("vectorizer-only", "true"); }
        return params
        // let query_param = params.toString()
        // if (query_param.length > 0) query_param = "?" + query_param;
        // return query_param;
    }

    getParamsString(): string {
        let query_param = this.getParams().toString();
        if (query_param.length > 0) query_param = "?" + query_param;
        return query_param;
    }

}


function createNoteFilter(params: any): NoteSearchFilter {
    let tags: string[]
    let use_vectorizer: boolean = false
    let vectorizer_only: boolean = false

    if (typeof params['tags-in'] === "string") {
        tags = [params['tags-in']]
    } else {
        tags = params['tags-in']
    }
    if (params['use-vectorizer'] === "true") {
        use_vectorizer = true
    }
    if (params['vectorizer-only'] === "true") {
        vectorizer_only = true
    }

    return new NoteSearchFilter(params.search, tags, use_vectorizer, vectorizer_only)
}


export {createNoteFilter, NoteSearchFilter}
