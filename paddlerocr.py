from pathlib import Path
from PIL import Image, ImageEnhance
from paddleocr import PaddleOCR

exit(0)

def enhance_image_steps(img_path: Path) -> Path:
    """Усиливает контраст и переводит в ч/б для лучшего OCR"""
    image = Image.open(img_path).convert("L")
    image = ImageEnhance.Contrast(image).enhance(2.0)
    tmp_path = img_path.with_name(f"tmp_{img_path.name}")
    image.save(tmp_path)
    return tmp_path


def recognize_text_in_folder(folder: Path, lang: str = "en"):
    jpg_files = list(folder.glob("*.jpg"))

    if not jpg_files:
        print("🛑 Нет JPG-файлов в папке:", folder)
        return

    print(f"🔍 Найдено {len(jpg_files)} .jpg-файлов в {folder}")

    # Лёгкая модель: *_mobile
    ocr = PaddleOCR(
        use_angle_cls=False,   # ускоряет, если не нужен поворот текста
        lang=lang,
        # rec_model_dir=None,    # авто-скачивание мобильной модели
        # det_model_dir=None,
        # use_gpu=False,         # на Mac без GPU это быстрее и стабильнее
        # rec_algorithm="CRNN",  # стандарт для мобильных
        # det_algorithm="DB"     # детектор для мобильных
    )

    for i, img_path in enumerate(jpg_files, 1):
        print(f"\n[{i}/{len(jpg_files)}] 🖼️ Обрабатывается: {img_path.name}")

        try:
            processed_path = enhance_image_steps(img_path)
        except Exception as e:
            print(f"⚠️ Не удалось обработать {img_path.name}: {e}")
            continue

        try:
            result = ocr.predict(str(processed_path))
            # result = ocr.ocr(str(processed_path))
            # result = ocr.ocr(str(processed_path), cls=False)

            extracted_text = "\n".join(
                line[1][0] for block in result if block for line in block
            )
        except Exception as e:
            print(f"⚠️ Ошибка OCR для {img_path.name}: {e}")
            continue
        finally:
            processed_path.unlink(missing_ok=True)  # удаляем временный файл

        txt_path = img_path.with_suffix(".txt")
        txt_path.write_text(extracted_text.strip(), encoding="utf-8")
        print(f"✅ Текст сохранён в: {txt_path.name}")

    print("\n🎉 Распознавание завершено.")


if __name__ == "__main__":
    recognize_text_in_folder(Path("images"), lang="en")
