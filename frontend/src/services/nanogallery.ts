import {getSmallThumbnail, hasSmallThumbnail} from "@/services/thumbnails.ts";


export function nanoGalleryReload() {
    $.getScript("/js/nanogallery2.min.js")
        .fail((jqxhr, settings, exception) => {
            console.log("Произошла ошибка при перезагрузке библиотеки `nano gallery`", jqxhr, settings, exception);
        });
}


export function makeRandomID(length: number): string {
    let result = '';
    const characters: string = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    const charactersLength = characters.length;
    let counter = 0;
    while (counter < length) {
        result += characters.charAt(Math.floor(Math.random() * charactersLength));
        counter += 1;
    }
    return result;
}

export function createGallery(galleryID: any, items: any[], retry: boolean = true) {
    try {
        // @ts-ignore
        $(`#${galleryID}`).nanogallery2( {
            // ### gallery settings ###
            thumbnailHeight: 100,
            thumbnailWidth: 100,
            thumbnailL1GutterWidth: 20,
            thumbnailL1GutterHeight: 20,
            blurredImageQuality: 3,
            thumbnailAlignment: "left",
            thumbnailOpenImage: true,
            thumbnailDisplayTransitionDuration: 1,
            thumbnailDisplayInterval: 1,
            thumbnailBorderVertical: 1,
            thumbnailBorderHorizontal: 1,

            colorScheme: {
                thumbnail: {
                    borderColor: "rgba(114,114,114,0.69)",
                    borderRadius: "4px",
                }
            },
            thumbnailToolbarImage :  { topLeft: 'display', bottomRight : 'download' },
            allowHTMLinData: true,
            thumbnailLabel: {
                position: "onBottom",
                titleMultiLine: true
            },
            // ### gallery content ###
            items: items
        });
    } catch {
        if (retry) createGallery(galleryID, items, false)
    }
}


interface NGItem {
    src: string
    srct?: string
    title?: string
}


export async function findThumbs(images: string[], withDescriptions: string[]): Promise<NGItem[]> {
    // Параллельно выполняем запросы для всех URL
    const promises = images.map(async (url, index) => {
        let data: NGItem = {
            src: url
        };
        // Асинхронно проверяем наличие миниатюры
        if (await hasSmallThumbnail(url)) {
            data.srct = getSmallThumbnail(url);
        }

        if (withDescriptions) {
            data.title = withDescriptions[index];
        }

        return data;
    });

    // Ожидаем завершения всех запросов
    return await Promise.all(promises);
}