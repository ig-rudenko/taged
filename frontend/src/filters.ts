class NoteSearchFilter {
    constructor(
        public search: string = "",
        public tags: string[] = [],
    ) {
    }

    getParams(): URLSearchParams {
        const params = new URLSearchParams();
        if (this.search.length > 0) params.append("search", this.search);
        for (const tag of this.tags) {
            params.append("tags-in", tag);
        }
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
    if (typeof params['tags-in'] === "string") {
        tags = [params['tags-in']]
    } else {
        tags = params['tags-in']
    }
    return new NoteSearchFilter(params.search, tags)
}


export {createNoteFilter, NoteSearchFilter}
