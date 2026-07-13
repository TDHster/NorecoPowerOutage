# Спецификация OCR-пайплайна (CLI-only)

Воссоздать проект **docuscan** (PaddleOCR + PyMuPDF + OpenCV) в новом проекте.
Только CLI — без FastAPI, без Docker. `python main.py договор.pdf` → JSON.

---

## Целевая структура

```
проект/
├── pyproject.toml
├── .python-version          # "3.12"
├── main.py                  # CLI + process_pdf() + ScanConfig
├── run.sh                   # ./run.sh scan договор.pdf
└── src/
    ├── __init__.py
    ├── pdf_to_images.py     # PDF → список numpy RGB-изображений
    ├── ocr_engine.py        # PaddleOCR (lang="ru"), синглтон
    ├── extract_contacts.py  # ФИО, должность, email из раздела
    └── signature_detector.py # эвристическая детекция подписи
```

---

## 1. `pyproject.toml`

```toml
[project]
name = "pdf-scanner"
version = "0.1.0"
description = "OCR-извлечение данных из PDF (PaddleOCR)"
requires-python = ">=3.12"
dependencies = [
    "paddlepaddle>=3.0.0",
    "paddleocr>=2.9",
    "pymupdf>=1.25",
    "opencv-python-headless>=4.10",
    "numpy>=1.26",
]
```

---

## 2. `.python-version`

```
3.12
```

---

## 3. `src/__init__.py`

Пустой файл.

---

## 4. `src/pdf_to_images.py`

```python
"""Convert PDF pages to numpy arrays (RGB) using PyMuPDF."""

import numpy as np
import fitz  # pymupdf


def pdf_to_images(pdf_path: str, dpi: int = 300) -> list[np.ndarray]:
    """
    Render each page of a PDF as a numpy RGB array.

    Args:
        pdf_path: Path to the PDF file.
        dpi: Rendering resolution (default 300).

    Returns:
        List of (H, W, 3) uint8 numpy arrays, one per page.
    """
    doc = fitz.open(pdf_path)
    images: list[np.ndarray] = []
    zoom = dpi / 72.0  # fitz default is 72 DPI
    mat = fitz.Matrix(zoom, zoom)

    for page in doc:
        pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
        arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
            pix.height, pix.width, 3
        )
        images.append(arr)

    doc.close()
    return images
```

---

## 5. `src/ocr_engine.py`

```python
"""PaddleOCR-based text extraction from images."""

import numpy as np
from paddleocr import PaddleOCR


_ocr: PaddleOCR | None = None


def _get_ocr() -> PaddleOCR:
    global _ocr
    if _ocr is None:
        _ocr = PaddleOCR(lang="ru")
    return _ocr


# (x1, y1, x2, y2, text, confidence)
OcrResult = list[tuple[float, float, float, float, str, float]]


def ocr_image(img: np.ndarray) -> OcrResult:
    ocr = _get_ocr()
    raw = ocr.ocr(img)

    if not raw or not raw[0]:
        return []

    result = raw[0]
    texts: list[str] = result.get("rec_texts", [])
    scores: list[float] = result.get("rec_scores", [])
    boxes: list[np.ndarray] = result.get("rec_boxes", [])

    results: OcrResult = []
    for box, text, conf in zip(boxes, texts, scores):
        if box is None or len(box) < 4:
            continue
        x1, y1, x2, y2 = float(box[0]), float(box[1]), float(box[2]), float(box[3])
        results.append((x1, y1, x2, y2, text, conf))

    return results
```

---

## 6. `src/extract_contacts.py`

```python
"""Extract ФИО, должность and email from Раздел 2.1 OCR results."""

import re
from typing import NamedTuple, Optional

from .ocr_engine import OcrResult


class ContactInfo(NamedTuple):
    full_name: str | None
    position: str | None
    email: str | None


# ── helpers ──────────────────────────────────────────────────────────


def _ocr_lines(ocr: OcrResult) -> list[tuple[float, str]]:
    """Return (y_center, text) sorted top-to-bottom."""
    sorted_ = sorted(ocr, key=lambda r: (r[1], r[0]))  # y first, then x
    return [(r[1], r[4]) for r in sorted_]


# Default markers for searching the contacts section
DEFAULT_SECTION_MARKERS = ["2.1", "раздел 2", "реквизит", "адрес", "банковск"]

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

# Default field prefix patterns (case-insensitive)
DEFAULT_FIELD_FIO = re.compile(r"фио\s*:\s*(.+)", re.IGNORECASE)
DEFAULT_FIELD_POSITION = re.compile(
    r"(?:должность|должност|в\s+лице)\s*:\s*(.+)", re.IGNORECASE
)
DEFAULT_FIELD_EMAIL = re.compile(r"(?:e-?mail|е-?mail|почта|email)\s*:\s*(.+)", re.IGNORECASE)


def _build_field_re(
    prefix: str, key: str, defaults: dict[str, re.Pattern]
) -> re.Pattern:
    """Build a field regex from a user-supplied prefix, or return default."""
    if not prefix:
        return defaults[key]
    escaped = re.escape(prefix)
    return re.compile(escaped + r"\s*(.+)", re.IGNORECASE)


def extract_contacts(
    ocr: OcrResult,
    marker: Optional[str] = None,
    field_prefixes: Optional[dict[str, str]] = None,
    ocr_raw: OcrResult | None = None,
) -> ContactInfo:
    """
    Parse Раздел 2.1 or similar section from OCR data.

    Args:
        ocr: OCR result from the page containing the contacts section.
        marker: Custom section marker to search for (e.g. "3.1").
                If None, uses default markers.
        field_prefixes: Custom field prefix overrides, e.g.
            {"fio": "Имя:", "position": "Должность:", "email": "Почта:"}.
            If a key is missing or None, the default is used.
        ocr_raw: Unused, kept for compatibility.

    Returns:
        ContactInfo(full_name, position, email).
    """
    lines = _ocr_lines(ocr)
    if not lines:
        return ContactInfo(None, None, None)

    # 1. Determine markers to search
    section_markers = [marker] if marker else DEFAULT_SECTION_MARKERS

    # 2. Find section start
    section_start = -1
    for i, (_y, text) in enumerate(lines):
        low = text.lower().strip()
        for m in section_markers:
            if m.lower() in low:
                section_start = i
                break
        if section_start != -1:
            break

    if section_start == -1:
        section_start = len(lines) // 2  # fallback to bottom half

    # 3. Build regexes from user-supplied prefixes (or defaults)
    prefixes = field_prefixes or {}
    field_fio = _build_field_re(prefixes.get("fio", ""), "fio", {
        "fio": DEFAULT_FIELD_FIO,
        "position": DEFAULT_FIELD_POSITION,
        "email": DEFAULT_FIELD_EMAIL,
    })
    field_position = _build_field_re(prefixes.get("position", ""), "position", {
        "fio": DEFAULT_FIELD_FIO,
        "position": DEFAULT_FIELD_POSITION,
        "email": DEFAULT_FIELD_EMAIL,
    })
    field_email = _build_field_re(prefixes.get("email", ""), "email", {
        "fio": DEFAULT_FIELD_FIO,
        "position": DEFAULT_FIELD_POSITION,
        "email": DEFAULT_FIELD_EMAIL,
    })

    # 4. Scan for field matches
    full_name: str | None = None
    position: str | None = None
    email: str | None = None

    for _y, text in lines[section_start:]:
        lower = text.lower().strip()

        # FIO
        m = field_fio.search(lower)
        if m and full_name is None:
            val = m.group(1).strip()
            full_name = _clean_fio(val)

        # Position
        m = field_position.search(lower)
        if m and position is None:
            position = m.group(1).strip()
            position = position[:1].upper() + position[1:] if position else position

        # Email
        m = field_email.search(lower)
        if m and email is None:
            raw_email = m.group(1).strip()
            parsed = EMAIL_RE.search(raw_email)
            if parsed:
                email = parsed.group(0)

        # Fallback: bare email anywhere
        if email is None:
            bare = EMAIL_RE.search(text)
            if bare:
                email = bare.group(0)

    # 5. Fallback for position via keywords
    if position is None:
        POSITION_KEYWORDS = {
            "директор", "руководитель", "начальник",
            "генеральн", "президент", "председател",
            "главн", "управляющий", "менеджер",
        }
        for _y, text in lines[section_start:]:
            low = text.lower()
            for kw in POSITION_KEYWORDS:
                if kw in low:
                    position = text.strip()
                    position = position[:1].upper() + position[1:] if position else position
                    break
            if position:
                break

    # 6. Fallback FIO via regex
    if full_name is None:
        fio_re = re.compile(
            r"[А-ЯЁ][а-яё]+(?:-[А-ЯЁ][а-яё]+)?\s+"
            r"[А-ЯЁ][а-яё]+\s+"
            r"[А-ЯЁ][а-яё]+"
        )
        block = " ".join(t for _, t in lines[section_start:])
        m = fio_re.search(block)
        if m:
            full_name = m.group(0)

    return ContactInfo(full_name, position, email)


def _clean_fio(raw: str) -> str | None:
    """Attempt to title-case a FIO string."""
    parts = raw.strip().split()
    if len(parts) >= 3:
        return " ".join(p.capitalize() for p in parts[:3])
    m = re.search(
        r"[А-ЯЁ][а-яё]+(?:-[А-ЯЁ][а-яё]+)?\s+"
        r"[А-ЯЁ][а-яё]+\s+"
        r"[А-ЯЁ][а-яё]+",
        raw,
    )
    return m.group(0) if m else None
```

---

## 7. `src/signature_detector.py`

```python
"""
Detect handwritten signatures on contract pages.

Algorithm:
1. Define signature zone – bottom region of the page (usually right half).
2. Binarise the image and mask out areas covered by OCR text boxes.
3. Remove table lines (long straight lines) via morphological filtering.
4. Analyse remaining connected components:
   - Filter out noise (tiny specks, straight shapes).
   - Score the remaining ink by contour complexity + density.
"""

import cv2
import numpy as np

from .ocr_engine import OcrResult

# ── tunable parameters ────────────────────────────────────────────────
SIGNATURE_ZONE_HEIGHT_RATIO = 0.25   # bottom 25 % of page
SIGNATURE_ZONE_WIDTH_RATIO = 0.55    # right 55 % (or left if symmetric)
SIGNATURE_ZONE_X_OFFSET_RATIO = 0.35  # start at 35 % from left

MIN_CONTOUR_AREA = 300               # px² – discard dust/speckles
MIN_CONTOUR_PERIMETER = 80           # px – discard short strokes
MAX_COMPACTNESS = 0.3                # lower = more irregular (4πA/P²)
MIN_BLACK_DENSITY = 0.02             # 2 % black pixels in zone = signature


def _to_gray(img: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)


def _binarise(gray: np.ndarray) -> np.ndarray:
    """Otsu threshold → binary (255 = ink, 0 = background)."""
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return binary


def _mask_text_boxes(
    binary: np.ndarray, ocr: OcrResult, margin: int = 5
) -> np.ndarray:
    """Erase pixels inside OCR text bounding boxes (set to 0)."""
    mask = binary.copy()
    h, w = binary.shape
    for x1, y1, x2, y2, _text, _conf in ocr:
        x1 = max(0, int(x1) - margin)
        y1 = max(0, int(y1) - margin)
        x2 = min(w, int(x2) + margin)
        y2 = min(h, int(y2) + margin)
        mask[y1:y2, x1:x2] = 0
    return mask


def _remove_lines(binary: np.ndarray) -> np.ndarray:
    """
    Remove long straight horizontal / vertical lines that likely
    belong to table borders.
    """
    clean = binary.copy()
    # detect horizontal lines
    h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (80, 1))
    horiz = cv2.morphologyEx(clean, cv2.MORPH_OPEN, h_kernel)
    clean[horiz > 0] = 0

    # detect vertical lines
    v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 80))
    vert = cv2.morphologyEx(clean, cv2.MORPH_OPEN, v_kernel)
    clean[vert > 0] = 0

    return clean


def _is_signature_like(contour: np.ndarray) -> bool:
    """
    Heuristic: real signatures have irregular shapes.
    Compactness = 4πA / P²  (1.0 for a circle, ~0.0 for a squiggle).
    """
    area = cv2.contourArea(contour)
    perimeter = cv2.arcLength(contour, closed=True)
    if area < MIN_CONTOUR_AREA or perimeter < MIN_CONTOUR_PERIMETER:
        return False
    compactness = 4.0 * np.pi * area / (perimeter * perimeter + 1e-6)
    return compactness < MAX_COMPACTNESS


def detect_signature(
    img: np.ndarray, ocr: OcrResult
) -> tuple[bool, float, dict]:
    """
    Run signature detection on one page.

    Args:
        img: (H, W, 3) uint8 RGB image.
        ocr: OCR results for the same image.

    Returns:
        (present, confidence, details) where:
          present – bool,
          confidence – float 0..1,
          details – dict with debug info.
    """
    h, w = img.shape[:2]
    gray = _to_gray(img)
    binary = _binarise(gray)
    binary = _mask_text_boxes(binary, ocr, margin=4)
    binary = _remove_lines(binary)

    # Crop signature zone: bottom-right area
    x_start = int(w * SIGNATURE_ZONE_X_OFFSET_RATIO)
    y_start = int(h * (1 - SIGNATURE_ZONE_HEIGHT_RATIO))
    zone = binary[y_start:, x_start:]

    zone_h, zone_w = zone.shape
    total_pixels = zone_h * zone_w
    black_pixels = int(np.sum(zone > 0))
    density = black_pixels / max(total_pixels, 1)

    # Contour analysis
    contours, _ = cv2.findContours(zone, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    signature_contours = [c for c in contours if _is_signature_like(c)]
    signature_pixels = sum(cv2.contourArea(c) for c in signature_contours)

    # Decision
    has_ink = density >= MIN_BLACK_DENSITY
    has_sig_strokes = len(signature_contours) >= 2
    present = has_ink and has_sig_strokes

    # Confidence heuristic
    if present:
        confidence = min(1.0, (density * 5 + len(signature_contours) * 0.05))
    else:
        confidence = 1.0 - min(1.0, density * 10)

    details = {
        "zone_black_density": round(density, 4),
        "signature_contours": len(signature_contours),
        "signature_pixels": int(signature_pixels),
        "total_contours": len(contours),
    }

    return present, round(confidence, 2), details
```

---

## 8. `main.py` — CLI и главный пайплайн

```python
#!/usr/bin/env python3
"""PDF OCR scanner — извлечение ФИО/должность/email + детекция подписи."""

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from src.pdf_to_images import pdf_to_images
from src.ocr_engine import ocr_image
from src.extract_contacts import extract_contacts
from src.signature_detector import detect_signature


@dataclass
class ScanConfig:
    section_marker: Optional[str] = None
    contact_field_prefixes: Optional[dict[str, str]] = None
    signature_section: Optional[str] = None


DEFAULT_CONFIG = ScanConfig()


def process_pdf(pdf_path: str, config: Optional[ScanConfig] = None) -> dict:
    path = Path(pdf_path)
    if not path.exists():
        return {"error": f"File not found: {pdf_path}"}

    cfg = config or DEFAULT_CONFIG

    print(f"Processing: {path.name}")
    pages = pdf_to_images(str(path), dpi=200)
    print(f"  Pages: {len(pages)}")

    contacts: dict = {}
    signature = None

    for i, img in enumerate(pages):
        print(f"  Page {i+1}: OCR...", end=" ", flush=True)
        ocr = ocr_image(img)
        print(f"{len(ocr)} text blocks")

        c = extract_contacts(
            ocr,
            marker=cfg.section_marker,
            field_prefixes=cfg.contact_field_prefixes,
        )
        if c.full_name and "full_name" not in contacts:
            contacts["full_name"] = c.full_name
        if c.position and "position" not in contacts:
            contacts["position"] = c.position
        if c.email and "email" not in contacts:
            contacts["email"] = c.email

        sig_present, sig_conf, sig_details = detect_signature(img, ocr)
        if signature is None or sig_present:
            signature = {
                "present": sig_present,
                "confidence": sig_conf,
                "details": sig_details,
                "page": i + 1,
            }

    result: dict = {"file": path.name}

    if contacts:
        result["contacts"] = contacts

    if signature is not None:
        result["signature"] = {
            "present": signature["present"],
            "confidence": signature["confidence"],
            "page": signature["page"],
        }

    return result


def main() -> None:
    pdf_path = None
    config = None

    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--config" and i + 1 < len(sys.argv):
            data = json.loads(sys.argv[i + 1])
            config = ScanConfig(
                section_marker=data.get("section_marker"),
                contact_field_prefixes=data.get("contact_field_prefixes"),
                signature_section=data.get("signature_section"),
            )
            i += 2
        else:
            pdf_path = arg
            i += 1

    if not pdf_path:
        print("Usage: python main.py [--config '<json>'] <pdf_path>", file=sys.stderr)
        sys.exit(1)

    result = process_pdf(pdf_path, config)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
```

---

## 9. `run.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

export PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True
DIR="$(cd "$(dirname "$0")" && pwd)"

case "${1:-}" in
    scan)
        if [ $# -lt 2 ]; then
            echo "Usage: $(basename "$0") scan <pdf_path>"
            exit 1
        fi
        cd "$DIR"
        exec uv run python main.py "$2"
        ;;
    *)
        echo "Usage: $(basename "$0") scan <pdf_path>"
        exit 1
        ;;
esac
```

---

## Что делает каждый модуль

| Модуль | Вход | Выход | Ключевая зависимость |
|---|---|---|---|
| `pdf_to_images` | путь к PDF | `list[np.ndarray]` (RGB, uint8) | `pymupdf` (fitz) |
| `ocr_engine` | numpy-изображение | `list[(x1,y1,x2,y2,text,conf)]` | `paddleocr` |
| `extract_contacts` | OCR-результат | `ContactInfo(full_name, position, email)` | только регэкспы |
| `signature_detector` | изображение + OCR | `(bool, float, dict)` | `opencv-python-headless` |

Пайплайн: `process_pdf()` последовательно вызывает их для каждой страницы, мержит результаты.

---

## Ключевые технические детали

- **Переменная окружения**: `PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True` — обязательна, иначе PaddleOCR падает.
- **Модели**: авто-скачивание при первом запуске (~130 MB) в `~/.paddlex/official_models/`. Нужен интернет.
- **DPI**: `main.py` передаёт `dpi=200` в `pdf_to_images`.
- **Конфигурация**: `ScanConfig` позволяет переопределить маркер раздела и префиксы полей через `--config '{"section_marker":"3.1"}'`.
- **Детекция подписи**: чистая эвристика (без ML) — Otsu-бинаризация → маскирование текста → удаление линий → анализ контуров (compactness < 0.3, ≥2 контуров, density ≥ 2%).
- **Fallback'и в extract_contacts**: если поле не найдено по префиксу — регэкспом ищет ФИО (3 слова с заглавных), email, должность — по ключевым словам.

---

## Порядок действий при создании (для Cline)

1. Создать структуру папок и все файлы из списка выше.
2. Запустить: `uv venv --python 3.12 && uv sync`
3. Дать права: `chmod +x run.sh`
4. Проверить: `./run.sh scan путь/к/тестовому.pdf`