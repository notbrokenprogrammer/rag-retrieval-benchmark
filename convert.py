"""Convert PDFs to normalized text chunks for retrieval benchmarking."""

# pymorphy3 does not currently provide type stubs.
# mypy: disable-error-code=import-untyped

import re
import sys
from pathlib import Path

import pymorphy3  # type: ignore
from pypdf import PdfReader

MORPH = pymorphy3.MorphAnalyzer()

PDF_DIR = Path("data/pdfs")
DOCUMENTS_DIR = Path("data/documents")
CHUNKS_DIR = Path("data/chunks")
NORMALIZED_DIR = Path("preparsing")

CHUNK_SIZE = 250
CHUNK_OVERLAP = 50


def normalize_text(text: str) -> str:
    """Нормализует и лемматизирует текст."""
    words = re.findall(r"[а-яёa-z0-9]+", text.lower())

    normalized_words = []

    for word in words:
        if re.fullmatch(r"[а-яё]+", word):
            word = MORPH.parse(word)[0].normal_form

        normalized_words.append(word)

    return " ".join(normalized_words)


def pdf_to_text(pdf_path: Path) -> str:
    """Извлекает текст из PDF."""
    reader = PdfReader(pdf_path)

    pages = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            pages.append(text)

    return "\n".join(pages)


def convert_pdfs() -> None:
    """Преобразует PDF-файлы в TXT."""
    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)

    for pdf_path in PDF_DIR.glob("*.pdf"):
        text = pdf_to_text(pdf_path)

        output_path = DOCUMENTS_DIR / f"{pdf_path.stem}.txt"

        output_path.write_text(
            text,
            encoding="utf-8",
        )

        print(f"PDF converted: {pdf_path.name}")


def chunk_text(text: str) -> list[str]:
    """Разбивает текст на чанки."""
    words = text.split()

    chunks = []

    step = CHUNK_SIZE - CHUNK_OVERLAP

    for start in range(0, len(words), step):
        end = start + CHUNK_SIZE

        chunk = words[start:end]

        if not chunk:
            break

        chunks.append(" ".join(chunk))

        if end >= len(words):
            break

    return chunks


def create_chunks() -> None:
    """Разбивает TXT-документы на чанки."""
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

    for file_path in DOCUMENTS_DIR.glob("*.txt"):
        text = file_path.read_text(encoding="utf-8")

        chunks = chunk_text(text)

        for index, chunk in enumerate(chunks, start=1):
            output_name = f"{file_path.stem}_chunk_{index:03d}.txt"

            output_path = CHUNKS_DIR / output_name

            output_path.write_text(
                chunk,
                encoding="utf-8",
            )

        print(f"Chunks created: {file_path.name} -> {len(chunks)}")


def normalize_chunks() -> None:
    """Лемматизирует все чанки."""
    NORMALIZED_DIR.mkdir(parents=True, exist_ok=True)

    for file_path in CHUNKS_DIR.glob("*.txt"):
        text = file_path.read_text(encoding="utf-8")

        normalized_text = normalize_text(text)

        output_path = NORMALIZED_DIR / file_path.name

        output_path.write_text(
            normalized_text,
            encoding="utf-8",
        )

        print(f"Normalized: {file_path.name}")


def process_documents() -> None:
    """Запускает полный preprocessing документов."""
    convert_pdfs()
    create_chunks()
    normalize_chunks()


def main() -> None:
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])

        print(normalize_text(query))

        return

    process_documents()


if __name__ == "__main__":
    main()
