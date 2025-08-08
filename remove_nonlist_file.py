from pathlib import Path
from logger import logger
from config import config

def delete_unlisted(allowed_filenames: list[str], directory: str = config.IMAGES_DIR, extension="*.jpg") -> None:
    """
    Удаляет .jpg файлы в каталоге, имена которых (с расширением) нет в списке allowed_filenames.
    :param directory: путь к каталогу
    :param allowed_filenames: список имён файлов с расширением (.jpg)
    """
    dir_path = Path(directory)

    if not dir_path.is_dir():
        raise NotADirectoryError(f"{directory} — not the directory")

    files_in_dir = list(dir_path.glob(extension))
    logger.debug(f"Found files: {[p.name for p in files_in_dir]}")

    for file_path in files_in_dir:
        logger.debug(f"Checking file: {file_path.name!r}")
        if file_path.name not in allowed_filenames:
            logger.info(f"Removing {file_path.name}, cause not on URL list")
            file_path.unlink()
            
            
if __name__ == "__main__":
    # keep_list = ["image1.jpg", "photo2.jpg", "logo.jpg"]
    # delete_unlisted_jpgs("/path/to/folder", keep_list)
    pass
