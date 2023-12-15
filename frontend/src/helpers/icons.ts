/**
 * Возвращает имя иконки для формата файла.
 */
export default function getFileFormatIconName(fileName: string): string {
    if (fileName.match(/.+\.(docx?|rtf)$/i)){
        return 'docx'
    }
    if (fileName.match(/.+\.xls[xm]?$/i)){
        return 'xlsx'
    }
    if (fileName.match(/.+\.pdf$/i)){
        return 'pdf'
    }
    if (fileName.match(/.+\.xml$/i)){
        return 'xml'
    }
    if (fileName.match(/.+\.drawio$/i)){
        return 'drawio'
    }
    if (fileName.match(/.+\.txt$/i)){
        return 'txt'
    }
    if (fileName.match(/.+\.vsdx?$/i)){
        return 'visio'
    }
    if (fileName.match(/.+\.(png|jpe?g|gif|bpm|svg|ico|tiff)$/i)){
        return 'img'
    }
    if (fileName.match(/.+\.(rar|7z|zip|tar[.gz]|iso)$/i)){
        return 'archive'
    }

    return 'file'
}