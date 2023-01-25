import re
import base64
import hashlib
import pathlib
from bs4 import BeautifulSoup

from django.conf import settings


class ImagePathIsNotFileError(Exception):
    pass


class PathNotSetError(Exception):
    pass


class InvalidImageBase64Error(Exception):
    pass


class ImageBase64Decoder:

    prefix_pattern: str = r"^data:image/\S+;base64,"

    def __init__(self, image_src: str):
        if re.match(self.prefix_pattern, image_src[:40]):
            image_base64: str = re.sub(self.prefix_pattern, "", image_src)

            # Декодируем base 64 в bytes
            self.image_binary: bytes = base64.decodebytes(
                bytes(image_base64, encoding="utf8") + b"="
            )
        else:
            raise InvalidImageBase64Error(
                f'Неверный формат изображения base64 "{image_src[:40]}",'
                f' должен быть "data:image/<type>;base64,..."'
            )

    def save(self, file_path: pathlib.Path):
        """Сохраняем байты в файл как изображение"""

        if file_path.exists() and file_path.is_dir():
            raise ImagePathIsNotFileError(
                f"Путь для сохранения изображения не является файлом: {file_path.absolute()}"
            )

        with file_path.open("wb") as file:
            file.write(self.image_binary)


class ReplaceImagesInHtml:

    media_root: pathlib.Path = settings.MEDIA_ROOT
    media_url: str = settings.MEDIA_URL

    def __init__(self, html_string: str):
        self._soup = BeautifulSoup(html_string, features="html.parser")
        self.images = self._soup.find_all("img")
        self._format_media_url()

    @property
    def has_base64_encoded_images(self) -> bool:
        for image in self.images:
            if not image.get("src"):
                continue
            if re.match(ImageBase64Decoder.prefix_pattern, image["src"][:30]):
                return True

        return False

    def _format_media_url(self):
        """Убираем начальный и завершающий слэши."""

        if self.media_url.endswith("/"):
            self.media_url = self.media_url[:-1]
        if self.media_url.startswith("/"):
            self.media_url = self.media_url[1:]

    @property
    def html(self) -> str:
        return str(self._soup)

    def save_images_and_update_src(self, image_prefix: str, folder: str):
        path = self.media_root / folder

        if path is None:
            raise PathNotSetError(
                "Не указан путь по умолчанию для сохранения изображений"
            )

        if not isinstance(path, pathlib.Path):
            path = pathlib.Path(path)

        # Создаем папки
        path.mkdir(parents=True, exist_ok=True)

        for number, image in enumerate(self.images):
            if not image.get("src"):
                continue

            try:
                # Декодируем атрибут изображения src из base64 в байты.
                decoded_image = ImageBase64Decoder(image["src"])
            except InvalidImageBase64Error:
                # Изображение не закодировано в base64.
                continue
            else:
                # Вычисляем хеш изображения
                hash_ = hashlib.md5(decoded_image.image_binary).hexdigest()[:10]

                # Имя изображения "префикс-номер-хеш.png"
                image_name = (
                    f"{image_prefix + image.get('alt', '')}-{number}-{hash_}.png"
                )
                # Сохраняем изображение.
                decoded_image.save(path / image_name)

                # Заменяем base64 на URL изображения.
                image["src"] = f"/{self.media_url}/{folder}/{image_name}"
