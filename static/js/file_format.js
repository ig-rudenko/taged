function file_format(file_name) {
    if (file_name.endsWith('.docx') || file_name.endsWith('.doc') || file_name.endsWith('.rtf')){
        return 'docx'
    }
    if (file_name.endsWith('.xls') || file_name.endsWith('.xlsx') || file_name.endsWith('.xlsm')){
        return 'xlsx'
    }
    if (file_name.endsWith('.pdf')){
        return 'pdf'
    }
    if (file_name.endsWith('.xml')){
        return 'xml'
    }
    if (file_name.endsWith('.drawio')){
        return 'drawio'
    }
    if (file_name.endsWith('.txt')){
        return 'txt'
    }
    if (file_name.endsWith('.vsd') || file_name.endsWith('.vsdx')){
        return 'visio'
    }
    if (file_name.endsWith('.png') || file_name.endsWith('.jpeg') || file_name.endsWith('.jpg') || file_name.endsWith('.gif') || file_name.endsWith('.bpm')){
        return 'img'
    }
    if (file_name.endsWith('.rar') || file_name.endsWith('.7z') || file_name.endsWith('.zip') || file_name.endsWith('.tar') || file_name.endsWith('.iso')){
        return 'archive'
    }
    return 'file'
}