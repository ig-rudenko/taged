class Paginator {
    constructor(
        public currentPage: number = 1,
        public maxPages: number = 1,
        public perPage: number = 24,
    ) {}
}

export {Paginator}