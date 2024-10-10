/**
 * @license Copyright (c) 2003-2023, CKSource Holding sp. z o.o. All rights reserved.
 * For licensing, see https://ckeditor.com/legal/ckeditor-oss-license
 */

CKEDITOR.editorConfig = function( config ) {
	// Define changes to default configuration here. For example:
	// config.language = 'fr';
	// config.uiColor = '#AADC6E';
};

const IMAGES = [];

function setSizes(editor) {
    const images = editor.document.find('img').$
    // console.log(images)
    images.forEach(img => {
        // console.log("CHECK IMAGES")
        if (IMAGES.indexOf(img) === -1) {
            // console.log("SET STYLE")
            img.setAttribute('style', 'max-width: 100%');
            IMAGES.push(img)
        }
    });
    setTimeout(() => setSizes(editor), 500)
}

CKEDITOR.on('instanceReady', evt => {
    const editor = evt.editor;
    setSizes(editor)
});
