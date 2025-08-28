from pathlib import Path
from PIL import Image, ImageEnhance
import easyocr
import numpy as np
from typing import List, Tuple, Any

from logger import logger

def enhance_image_steps(img_path: Path) -> Image.Image:
    """
    Открывает изображение, переводит в градации серого и повышает контраст.
    Не сохраняет промежуточные версии, возвращает улучшенное Image.
    """
    image = Image.open(img_path).convert("L")
    image = ImageEnhance.Contrast(image).enhance(2.0)
    return image

def crop_image(image: Image.Image, top: int = 0, bottom: int = 0, left: int = 0, right: int = 0, save_test: bool = True, original_path: Path | None = Path('images/cropped-test.jpg')) -> Image.Image:
    """
    Обрезает изображение сверху, снизу и по краям на заданные значения.
    
    Args:
        image: PIL Image объект для обрезки
        top: количество пикселей для обрезки сверху
        bottom: количество пикселей для обрезки снизу  
        left: количество пикселей для обрезки слева
        right: количество пикселей для обрезки справа
        save_test: сохранить ли тестовое изображение для контроля
        original_path: путь к исходному файлу (для сохранения тестового)
    
    Returns:
        Image.Image: обрезанное изображение
    """
    width, height = image.size
    
    # Проверяем границы обрезки
    if left + right >= width or top + bottom >= height:
        logger.warning("⚠️ Параметры обрезки слишком большие для изображения")
        return image
    
    # Вычисляем координаты для обрезки
    crop_box = (
        left,                    # левая граница
        top,                     # верхняя граница
        width - right,           # правая граница
        height - bottom          # нижняя граница
    )
    
    cropped_image = image.crop(crop_box)
    
    # Сохраняем тестовое изображение для контроля
    # if save_test and original_path:
    if save_test:
        # test_path = original_path.parent / f"cropped_{original_path.stem}.jpg"
        cropped_image.save(str(original_path))
        logger.debug(f"🔍 Тестовое обрезанное изображение сохранено {str(original_path)}")
    
    return cropped_image


def ocr_file(file_path: Path, lang: str = "en") -> str | None:
    """
    Распознаёт текст из указанного файла изображения.
    
    Args:
        file_path: Путь к файлу изображения
        lang: Язык для распознавания (по умолчанию "en")
        
    Returns:
        str | None: Распознанный текст или None в случае ошибки
    """
    if not file_path.exists():
        logger.error(f"🛑 Файл не найден: {file_path}")
        return None
        
    if not file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
        logger.error(f"🛑 Неподдерживаемый формат файла: {file_path.suffix}")
        return None

    logger.debug(f"🖼️ Обрабатывается файл: {file_path.name}")
    
    reader = easyocr.Reader([lang], gpu=False)

    try:
        image = enhance_image_steps(file_path)
    except Exception as e:
        logger.error(f"⚠️ Не удалось обработать {file_path.name}: {e}")
        return None
    
    try:
        # image = crop_image(image, top=320, bottom=220, save_test=True, original_path=None)
        image = crop_image(image, top=320, bottom=220)
    except Exception as e:
        logger.error(f"⚠️ Ошибка при обрезке изображения {file_path.name}: {e}")
        return None
    
    try:
        # Конвертируем PIL Image → numpy array
        image_np = np.array(image)
        # Передаём в easyocr - возвращает список кортежей (bbox, text, confidence)
        results = reader.readtext(image_np)
    except Exception as e:
        logger.error(f"⚠️ Ошибка OCR для {file_path.name}: {e}")
        return None

    text_lines = [result[1] for result in results]  # type: ignore[misc]
    full_text = "\n".join(text_lines)

    logger.debug(f'✅ Распознан текст: {full_text[:50]}...')
    
    return full_text if full_text.strip() else None


if __name__ == "__main__":
    # Обрабатываем все изображения в каталоге images
    images_dir = Path("images")
    
    if not images_dir.exists():
        print(f"Каталог {images_dir} не найден")
        exit(1)
    
    # Поддерживаемые форматы изображений
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    
    # Находим все файлы изображений
    image_files = []
    for ext in image_extensions:
        image_files.extend(images_dir.glob(f"*{ext}"))
        image_files.extend(images_dir.glob(f"*{ext.upper()}"))
    
    if not image_files:
        print(f"Нет файлов изображений в каталоге {images_dir}")
        exit(1)
    
    print(f"Найдено {len(image_files)} файлов изображений")
    
    # Обрабатываем каждый файл
    processed_count = 0
    for image_file in image_files:
        print(f"\nОбрабатывается: {image_file.name}")
        result = recognize_text_in_folder(image_file)
        
        if result:
            print(f"Распознанный текст: {result}")
            processed_count += 1
    
    print(f"\n🎉 Обработка завершена. Успешно обработано: {processed_count}/{len(image_files)} файлов")
