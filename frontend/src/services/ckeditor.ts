import tokenService from "@/services/token.service";

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
        if (window.CKEDITOR) {
            // @ts-ignore
            window.CKEDITOR.on('instanceReady', (evt: any) => {
                const editor = evt.editor;
                this.setSizes(editor);
            });
        } else {
            setTimeout(() => this.enableImagesAutoSize(), 50)
        }
    }

}

export const ckeditorConfig = {
    language: "ru",
    height: '75vh',
    uiColor: "#ffffff",
    filebrowserUploadUrl: "/api/ckeditor/upload/",
    fileTools_requestHeaders: {
        'Authorization': 'Bearer ' + tokenService.getLocalAccessToken()
    },
    iframe_attributes: {
        sandbox: 'allow-scripts allow-same-origin',
        allow: 'autoplay'
    },
    contentsCss: ["/themes/viva-light/theme.css", "/css/styles.min.css", "/css/main.css"],
    bodyClass: "m-4",
    format_pre: {
        element: 'pre',
        attributes: {class: "bg-black-alpha-70 border-round p-3 px-5 shadow-2 text-white w-fit"}
    },
    font_names: 'Cascadia Code, monospace;' +
        'Comic Sans MS/Comic Sans MS, cursive;' +
        'Courier New/Courier New, Courier, monospace;' +
        'Lucida Sans Unicode/Lucida Sans Unicode, Lucida Grande, sans-serif;' +
        'Tahoma/Tahoma, Geneva, sans-serif;' +
        'Times New Roman/Times New Roman, Times, serif;',
    toolbar: [
        {'name': 'document', 'items': ['Source', '-', 'Save', 'NewPage', 'Preview', 'Print', '-', 'Templates']},
        {'name': 'clipboard', 'items': ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo']},
        {'name': 'editing', 'items': ['Find', 'Replace', '-', 'SelectAll']},
        // {
        //   'name': 'forms',
        //   'items': ['Form', 'Checkbox', 'Radio', 'TextField', 'Textarea', 'Select', 'Button', 'ImageButton',
        //     'HiddenField']
        // },
        '/',
        {'name': 'styles', 'items': ['Styles', 'Format', 'Font', 'FontSize']},
        {'name': 'colors', 'items': ['TextColor', 'BGColor']},
        {
            'name': 'basicstyles',
            'items': ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat']
        },
        {
            'name': 'paragraph',
            'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-',
                'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock']
        },
        {'name': 'links', 'items': ['Link', 'Unlink', 'Anchor']},
        {
            'name': 'insert',
            'items': ['Image', 'Flash', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', 'PageBreak', 'Iframe']
        },
        {'name': 'about', 'items': ['About']},
        '/',
        {
            'name': 'yourcustomtools', 'items': [
                'Maximize',
                'ShowBlocks',
                "RemoveFormat"
            ]
        },
    ]
}
