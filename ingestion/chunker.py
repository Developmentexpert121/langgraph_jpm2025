import re
from typing import List, Dict
import pickle
from ingestion.pdf_loader import extract_pages_with_images

def is_heading(line: str) -> bool:
    return (
        line.isupper()
        and 3 < len(line) < 120
        and not line.isdigit()
    )

def is_subheading(line: str) -> bool:
    return (
        re.match(r"^\d{1,2}\s[A-Z]", line)
        or (line.istitle() and len(line) < 100)
    )

def build_sections(pages: List[Dict]) -> List[Dict]:
    sections = []
    current_section = None
    chunk_id = 0

    for page in pages:
        lines = page["text"].split("\n")

        for raw_line in lines:
            line = raw_line.strip()
            if not line:
                continue

            if is_heading(line):
                if current_section:
                    sections.append(current_section)

                current_section = {
                    "chunk_id": chunk_id,
                    "doc_name": page["doc_name"],
                    "heading": line,
                    "subheading": None,
                    "text": "",
                    "images": [],
                    "page_start": page["page"],
                    "page_end": page["page"],
                }
                chunk_id += 1

            elif is_subheading(line) and current_section:
                current_section["subheading"] = line

            elif current_section:
                current_section["text"] += line + " "
                current_section["page_end"] = page["page"]

        if current_section and page["images"]:
            current_section["images"].extend(page["images"])

    if current_section:
        sections.append(current_section)

    return sections


def split_large_sections(
    sections: List[Dict],
    max_words: int = 800,
    overlap: int = 100,
) -> List[Dict]:
    final_chunks = []
    new_chunk_id = 0

    for sec in sections:
        words = sec["text"].split()

        page_start = sec.get("page_start")
        page_end = sec.get("page_end")

        if len(words) <= max_words:
            final_chunks.append({
                **sec,
                "chunk_id": new_chunk_id,
                "page_start": page_start,
                "page_end": page_end,
            })
            new_chunk_id += 1
            continue

        start = 0
        while start < len(words):
            end = start + max_words
            chunk_text = " ".join(words[start:end])

            final_chunks.append({
                **sec,
                "chunk_id": new_chunk_id,
                "text": chunk_text,
                "page_start": page_start,
                "page_end": page_end,
            })

            new_chunk_id += 1
            start += max_words - overlap

    return final_chunks

def chunk_documents(
    pages: List[Dict],
    max_words: int = 800,
    overlap: int = 100,
) -> List[Dict]:
    
    sections = build_sections(pages)
    chunks = split_large_sections(
        sections, max_words=max_words, overlap=overlap
    )
    return chunks

if __name__ == "__main__":
    pdfs = [
        "data/raw/outlook_2025.pdf",
        "data/raw/midyear_2025.pdf",
    ]

    all_pages = []
    for pdf in pdfs:
        all_pages.extend(extract_pages_with_images(pdf))

    chunks = chunk_documents(all_pages)
    print(f"Created {len(chunks)} semantic chunks")
    with open("data/processed/semantic_chunks.pkl", "wb") as f:
        pickle.dump(chunks, f)
