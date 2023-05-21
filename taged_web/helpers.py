import re


def icon_path(file: str):
    """
    Если расширение файла есть в списке расширений, вернуть значок для этого расширения

    :param file: Имя файла, который вы хотите отобразить
    :return: Путь к значку для типа файла
    """

    if re.match(r".+\.(docx?|rtf)$", file):
        icon = "docx.png"
    elif re.match(r".+\.xls[xm]?$", file):
        icon = "xlsx.png"
    elif re.match(r".+\.pdf$", file):
        icon = "pdf.png"
    elif re.match(r".+\.(txt|log)$", file):
        icon = "txt.png"
    elif re.match(r".+\.(drawio)$", file):
        icon = "drawio.png"
    elif re.match(r".+\.xml$", file):
        icon = "xml.png"
    elif re.match(r".+\.vsdx?$", file):
        icon = "visio.png"
    elif re.match(r".+\.(rar|7z|zip|tar[.gz]|iso)$", file):
        icon = "archive.png"
    elif re.match(r".+\.(png|jpe?g|gif|bpm|svg|ico|tiff)$", file):
        icon = "img.png"
    else:
        icon = "file.png"

    # Возврат пути к иконке
    return "images/icons/" + icon
