# recognize_text_from_images.py

from pathlib import Path
from PIL import Image
import easyocr

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
            image = Image.open(img_path)
        except Exception as e:
            print(f"⚠️ Не удалось открыть {img_path.name}: {e}")
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
