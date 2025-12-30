import pdfplumber
import pytesseract
from PIL import Image
import os
import uuid

def clamp_bbox(bbox, page_width, page_height):
    x0, top, x1, bottom = bbox

    x0 = max(0, x0)
    top = max(0, top)
    x1 = min(page_width, x1)
    bottom = min(page_height, bottom)

    if x1 <= x0 or bottom <= top:
        return None

    return (x0, top, x1, bottom)

def extract_pages_with_images(
    pdf_path: str,
    image_dir: str = "data/images",
    use_ocr: bool = True,
):
    os.makedirs(image_dir, exist_ok=True)

    doc_name = os.path.basename(pdf_path).replace(".pdf", "")
    pages_data = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            page_text = (page.extract_text() or "").strip()

            page_width = page.width
            page_height = page.height

            images_data = []

            for img_idx, img in enumerate(page.images):
                try:
                    raw_bbox = (
                        img["x0"],
                        img["top"],
                        img["x1"],
                        img["bottom"],
                    )

                    bbox = clamp_bbox(
                        raw_bbox, page_width, page_height
                    )

                    if bbox is None:
                        continue

                    cropped_page = page.crop(bbox).to_image(
                        resolution=300
                    )

                    image_id = (
                        f"{doc_name}_p{page_num}_{img_idx}_"
                        f"{uuid.uuid4().hex[:6]}"
                    )
                    image_path = os.path.join(
                        image_dir, f"{image_id}.png"
                    )
                    cropped_page.save(image_path)

                    ocr_text = ""
                    if use_ocr:
                        ocr_text = pytesseract.image_to_string(
                            Image.open(image_path)
                        ).strip()

                    images_data.append(
                        {
                            "page": page_num,
                            "image_path": image_path,
                            "ocr_text": ocr_text,
                        }
                    )

                except Exception as e:
                    print(
                        f"[WARN] Image extraction failed "
                        f"(page {page_num}): {e}"
                    )

            pages_data.append(
                {
                    "doc_name": doc_name,
                    "page": page_num,
                    "text": page_text,
                    "images": images_data,
                }
            )

    return pages_data

if __name__ == "__main__":
    pdfs = [
        "data/raw/outlook_2025.pdf",
        "data/raw/midyear_2025.pdf",
    ]

    all_pages = []
    for pdf in pdfs:
        all_pages.extend(extract_pages_with_images(pdf))

    print(f"Extracted {len(all_pages)} pages")
    print("Sample:", all_pages[0])
