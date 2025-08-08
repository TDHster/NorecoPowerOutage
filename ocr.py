# recognize_text_from_images.py

from pathlib import Path
from PIL import Image, ImageEnhance
import easyocr

def enhance_image_steps(img_path: Path, out_dir: Path = Path("processed")) -> Image:
    out_dir.mkdir(exist_ok=True, parents=True)

    stem = img_path.stem  # имя файла без расширения

    # 1. Открытие и перевод в оттенки серого
    image = Image.open(img_path).convert("L")
    gray_path = out_dir / f"{stem}_1_gray.png"
    image.save(gray_path)
    print(f"🖤 Сохранено (градации серого): {gray_path.name}")

    # 2. Повышение контраста
    image = ImageEnhance.Contrast(image).enhance(2.0)
    contrast_path = out_dir / f"{stem}_2_contrast.png"
    image.save(contrast_path)
    print(f"⚫ Сохранено (контраст): {contrast_path.name}")

    # # 3. Бинаризация
    # threshold = 160
    # image = image.point(lambda x: 255 if x > threshold else 0)
    # binary_path = out_dir / f"{stem}_3_binary.png"
    # image.save(binary_path)
    # print(f"⬛ Сохранено (бинаризация): {binary_path.name}")

    return image  # уже готовое для OCR


def recognize_text_in_folder(folder: Path, lang: str = "en"):
    """
    Распознаёт текст со всех .jpg файлов в указанной папке
    и сохраняет результат в .txt рядом с изображениями.
    """
    reader = easyocr.Reader([lang], gpu=False)
    jpg_files = list(folder.glob("*.jpg"))

    if not jpg_files:
        print("🛑 Нет JPG-файлов в папке:", folder)
        return

    print(f"🔍 Найдено {len(jpg_files)} .jpg-файлов в {folder}")

    for i, img_path in enumerate(jpg_files, 1):
        print(f"\n[{i}/{len(jpg_files)}] 🖼️ Обрабатывается: {img_path.name}")

        try:   
            image = Image.open(img_path).convert("L")  # Перевод в градации серого

            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)

        except Exception as e:
            print(f"⚠️ Не удалось обработать {img_path.name}: {e}")
            continue
        
        # Распознаём текст
        results = reader.readtext(str(img_path))

        # Извлекаем только текст
        text_lines = [res[1] for res in results]
        full_text = "\n".join(text_lines)

        # Сохраняем в .txt
        txt_path = img_path.with_suffix(".txt")
        txt_path.write_text(full_text, encoding="utf-8")

        print(f"✅ Текст сохранён в: {txt_path.name}")

    print("\n🎉 Распознавание завершено.")

# Пример использования
if __name__ == "__main__":
    recognize_text_in_folder(Path("images"))  # путь к папке с картинками
