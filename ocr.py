from pathlib import Path
from PIL import Image, ImageEnhance
import easyocr

from logger import logger

def enhance_image_steps(img_path: Path) -> Image.Image:
    """
    Открывает изображение, переводит в градации серого и повышает контраст.
    Не сохраняет промежуточные версии, возвращает улучшенное Image.
    """
    image = Image.open(img_path).convert("L")
    image = ImageEnhance.Contrast(image).enhance(2.0)
    return image

def crop_image(image: Image.Image, top: int = 0, bottom: int = 0, left: int = 0, right: int = 0, save_test: bool = True, original_path: Path = None) -> Image.Image:
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
        cropped_image.save('images/cropped.jpg')
        logger.debug(f"🔍 Тестовое обрезанное изображение сохранено")
    
    return cropped_image


def recognize_text_in_folder(folder: Path, lang: str = "en"):
    """
    Распознаёт текст со всех .jpg файлов в указанной папке
    и сохраняет результат в .txt рядом с изображениями.
    """
    reader = easyocr.Reader([lang], gpu=False)
    jpg_files = list(folder.glob("*.jpg"))

    if not jpg_files:
        logger.info("🛑 Нет JPG-файлов в папке:", folder)
        return

    logger.debug(f"🔍 Найдено {len(jpg_files)} .jpg-файлов в {folder}")

    for i, img_path in enumerate(jpg_files, 1):
        logger.debug(f"\n[{i}/{len(jpg_files)}] 🖼️ Обрабатывается: {img_path.name}")

        try:
            image = enhance_image_steps(img_path)
        except Exception as e:
            logger.error(f"⚠️ Не удалось обработать {img_path.name}: {e}")
            continue
        
        try:
            image = crop_image(image, save_test=True, original_path='images')
        except Exception as e:
            logger.error(f"Error while cropping image {e}")
            continue
        exit(0)
        
        try:
            # Распознаём текст прямо с Pillow-объекта
            results = reader.readtext(image)
        except Exception as e:
            logger.error(f"⚠️ Ошибка OCR для {img_path.name}: {e}")
            continue

        text_lines = [res[1] for res in results]
        full_text = "\n".join(text_lines)

        txt_path = img_path.with_suffix(".txt")
        txt_path.write_text(full_text, encoding="utf-8")

        logger.debug(f"✅ Текст сохранён в: {txt_path.name}")

    logger.info("\n🎉 Распознавание завершено.")


if __name__ == "__main__":
    recognize_text_in_folder(Path("images"))
