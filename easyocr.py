from pathlib import Path
from PIL import Image, ImageEnhance
import easyocr


def enhance_image_steps(img_path: Path) -> Image.Image:
    """
    Открывает изображение, переводит в градации серого и повышает контраст.
    Не сохраняет промежуточные версии, возвращает улучшенное Image.
    """
    image = Image.open(img_path).convert("L")
    image = ImageEnhance.Contrast(image).enhance(2.0)
    return image


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
            image = enhance_image_steps(img_path)
        except Exception as e:
            print(f"⚠️ Не удалось обработать {img_path.name}: {e}")
            continue
        
        try:
            # Распознаём текст прямо с Pillow-объекта
            results = reader.readtext(image)
        except Exception as e:
            print(f"⚠️ Ошибка OCR для {img_path.name}: {e}")
            continue

        text_lines = [res[1] for res in results]
        full_text = "\n".join(text_lines)

        txt_path = img_path.with_suffix(".txt")
        txt_path.write_text(full_text, encoding="utf-8")

        print(f"✅ Текст сохранён в: {txt_path.name}")

    print("\n🎉 Распознавание завершено.")


if __name__ == "__main__":
    recognize_text_in_folder(Path("images"))
