from pathlib import Path

from PIL import Image

thumbnail_sizes = {
    "small": (300, 300),
    "large": (1920, 1920),
}


def get_thumbnail_path(origin_image_path: Path, size_name: str) -> Path:
    """Возвращает thumbnail для переданного изображения и размера thumbnail."""
    thumb_name = origin_image_path.stem + "_thumb_" + size_name + origin_image_path.suffix
    return origin_image_path.parent / thumb_name


def need_to_create_large_thumbnail(origin_image_size: tuple[int, int]) -> bool:
    """
    Если изображение слишком большое, то необходимо создать thumbnail.
    """
    return (
        origin_image_size[0] > thumbnail_sizes["large"][0] * 1.5
        or origin_image_size[1] > thumbnail_sizes["large"][1] * 1.5
    )


def create_thumbnails(original_image_path: Path) -> dict[str, Path]:
    """
    Создаёт thumbnail для переданного изображения и размера thumbnail.

    :param original_image_path: Путь к изображению в хранилище.
    """
    thumbnails: dict[str, Path] = {}

    for size_name, size in thumbnail_sizes.items():
        img = Image.open(original_image_path)
        if size_name == "large" and not need_to_create_large_thumbnail(img.size):
            # Пропускаем создание `large thumbnail`, если изображение недостаточно большое.
            continue

        img.thumbnail(size)
        thumb_image_path = get_thumbnail_path(original_image_path, size_name)
        thumbnails[size_name] = thumb_image_path
        img.save(thumb_image_path)
    return thumbnails
