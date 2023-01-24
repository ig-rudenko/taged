function file_format(file_name) {
    if (file_name.match(/.+\.(doc[x]?|rtf)$/i)){
        return 'docx'
    }
    if (file_name.match(/.+\.xls[xm]?$/i)){
        return 'xlsx'
    }
    if (file_name.match(/.+\.pdf$/i)){
        return 'pdf'
    }
    if (file_name.match(/.+\.xml$/i)){
        return 'xml'
    }
    if (file_name.match(/.+\.drawio$/i)){
        return 'drawio'
    }
    if (file_name.match(/.+\.txt$/i)){
        return 'txt'
    }
    if (file_name.match(/.+\.vsd[x]?$/i)){
        return 'visio'
    }
    if (file_name.match(/.+\.(png|jp[e]?g|gif|bpm|svg|ico|tiff)$/i)){
        return 'img'
    }
    if (file_name.match(/.+\.(rar|7z|zip|tar[.gz]|iso)$/i)){
        return 'archive'
    }
    return 'file'
}