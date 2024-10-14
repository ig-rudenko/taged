export class CkeditorImages {
    private resizeStyles: boolean
    private IMAGES: any[]

    constructor(skipInitial: boolean) {
        // Пропускаем начальные изображения в случае редактирования записи,
        // чтобы не переопределялись размеры существующих картинок.
        this.resizeStyles = !skipInitial;
        this.IMAGES = [];
    }

    setSizes(editor: any) {
        const images = editor.document.find('img').$;
        // console.log(images)
        images.forEach((img: any) => {
            // console.log("CHECK IMAGES")
            if (this.IMAGES.indexOf(img) === -1) {
                // console.log("SET STYLE", this.resizeStyles)
                if (this.resizeStyles) img.setAttribute('style', 'max-width: 100%');
                this.IMAGES.push(img)
            }
        });
        if (images.length > 0) this.resizeStyles = true;
        setTimeout(() => this.setSizes(editor), 500);
    }

    enableImagesAutoSize() {
        // @ts-ignore
        window.CKEDITOR.on('instanceReady', (evt: any) => {
            const editor = evt.editor;
            this.setSizes(editor);
        });
    }

}
