"""
Dolphin Parse JSON
==================
Runs the Dolphin v2 two-stage document parser on an image or PDF and saves
a structured JSON file matching the schema:

{
  "metadata": { "doc_id", "num_pages", "processing_time_sec" },
  "pages": [
    {
      "page_no", "text", "words", "numbers",
      "tables": [{"rows": [[...]]}],
      "formulas": [...],
      "reading_order": [...]
    }
  ]
}

Usage:
    python dolphin_parse_json.py --model_path ./hf_model \
        --input_path ./demo/page_imgs/page_1.png \
        --save_dir ./results
"""

import argparse
import glob
import json
import os
import re
import time

import torch
from PIL import Image
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration
from qwen_vl_utils import process_vision_info

from utils.utils import (
    convert_pdf_to_images,
    parse_layout_string,
    process_coordinates,
    check_bbox_overlap,
    setup_output_dirs,
    save_figure_to_local,
    resize_img,
)


# ---------------------------------------------------------------------------
# HTML table → list-of-rows parser
# ---------------------------------------------------------------------------

def _html_table_to_rows(html: str):
    """Parse an HTML table string into a list of row-lists of cell strings."""
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        rows = []
        for tr in soup.find_all("tr"):
            cells = [td.get_text(separator=" ", strip=True)
                     for td in tr.find_all(["td", "th"])]
            if cells:
                rows.append(cells)
        return rows
    except Exception as e:
        # Fallback: return raw html as single cell
        return [[html]]


# ---------------------------------------------------------------------------
# DOLPHIN model wrapper (same as demo_page.py)
# ---------------------------------------------------------------------------

class DOLPHIN:
    def __init__(self, model_id_or_path):
        self.processor = AutoProcessor.from_pretrained(model_id_or_path)
        self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            model_id_or_path
        )
        self.model.eval()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        if self.device == "cuda":
            self.model = self.model.bfloat16()
        else:
            self.model = self.model.float()
        self.tokenizer = self.processor.tokenizer
        self.tokenizer.padding_side = "left"

    def chat(self, prompt, image):
        is_batch = isinstance(image, list)
        images = image if is_batch else [image]
        prompts = (prompt if isinstance(prompt, list)
                   else [prompt] * len(images))
        assert len(images) == len(prompts)

        processed_images = [resize_img(img) for img in images]
        all_messages = []
        for img, question in zip(processed_images, prompts):
            all_messages.append([
                {"role": "user", "content": [
                    {"type": "image", "image": img},
                    {"type": "text", "text": question},
                ]}
            ])

        texts = [
            self.processor.apply_chat_template(
                msgs, tokenize=False, add_generation_prompt=True
            )
            for msgs in all_messages
        ]
        all_image_inputs = []
        for msgs in all_messages:
            image_inputs, _ = process_vision_info(msgs)
            all_image_inputs.extend(image_inputs)

        inputs = self.processor(
            text=texts,
            images=all_image_inputs if all_image_inputs else None,
            padding=True,
            return_tensors="pt",
        ).to(self.model.device)

        generated_ids = self.model.generate(
            **inputs, max_new_tokens=4096, do_sample=False, temperature=None
        )
        trimmed = [
            out[len(inp):]
            for inp, out in zip(inputs.input_ids, generated_ids)
        ]
        results = self.processor.batch_decode(
            trimmed, skip_special_tokens=True,
            clean_up_tokenization_spaces=False
        )
        return results if is_batch else results[0]


# ---------------------------------------------------------------------------
# Element-level batched processing
# ---------------------------------------------------------------------------

def _process_element_batch(elements, model, prompt, max_batch_size=None):
    results = []
    batch_size = len(elements)
    if max_batch_size and max_batch_size > 0:
        batch_size = min(batch_size, max_batch_size)
    for i in range(0, len(elements), batch_size):
        batch = elements[i: i + batch_size]
        crops = [e["crop"] for e in batch]
        prompts = [prompt] * len(crops)
        outputs = model.chat(prompts, crops)
        for j, out in enumerate(outputs):
            e = batch[j]
            results.append({
                "label": e["label"],
                "bbox": e["bbox"],
                "text": out.strip(),
                "reading_order": e["reading_order"],
                "tags": e["tags"],
            })
    return results


# ---------------------------------------------------------------------------
# Core: parse one PIL image → list of element dicts
# ---------------------------------------------------------------------------

def _parse_image_elements(pil_image, model, max_batch_size, save_dir, name):
    layout_output = model.chat("Parse the reading order of this document.", pil_image)
    layout_list = parse_layout_string(layout_output)

    if not layout_list or not (layout_output.startswith("[") and layout_output.endswith("]")):
        layout_list = [([0, 0, *pil_image.size], "distorted_page", [])]
    elif len(layout_list) > 1 and check_bbox_overlap(layout_list, pil_image):
        print("  Falling back to distorted_page mode (high bbox overlap)")
        layout_list = [([0, 0, *pil_image.size], "distorted_page", [])]

    tab_els, equ_els, code_els, text_els = [], [], [], []
    fig_results = []
    reading_order = 0

    for bbox, label, tags in layout_list:
        try:
            if label == "distorted_page":
                x1, y1, x2, y2 = 0, 0, *pil_image.size
                crop = pil_image
            else:
                x1, y1, x2, y2 = process_coordinates(bbox, pil_image)
                crop = pil_image.crop((x1, y1, x2, y2))

            if crop.size[0] <= 3 or crop.size[1] <= 3:
                reading_order += 1
                continue

            info = {
                "crop": crop,
                "label": label,
                "bbox": [x1, y1, x2, y2],
                "reading_order": reading_order,
                "tags": tags,
            }

            if label == "fig":
                fig_fn = save_figure_to_local(crop, save_dir, name, reading_order)
                fig_results.append({
                    "label": label,
                    "text": f"![Figure](figures/{fig_fn})",
                    "figure_path": f"figures/{fig_fn}",
                    "bbox": [x1, y1, x2, y2],
                    "reading_order": reading_order,
                    "tags": tags,
                })
            elif label == "tab":
                tab_els.append(info)
            elif label == "equ":
                equ_els.append(info)
            elif label == "code":
                code_els.append(info)
            else:
                text_els.append(info)

            reading_order += 1
        except Exception as e:
            print(f"  Warning: skipped element label={label}: {e}")
            reading_order += 1

    recognition = list(fig_results)
    if tab_els:
        recognition.extend(_process_element_batch(
            tab_els, model, "Parse the table in the image.", max_batch_size))
    if equ_els:
        recognition.extend(_process_element_batch(
            equ_els, model, "Read formula in the image.", max_batch_size))
    if code_els:
        recognition.extend(_process_element_batch(
            code_els, model, "Read code in the image.", max_batch_size))
    if text_els:
        recognition.extend(_process_element_batch(
            text_els, model, "Read text in the image.", max_batch_size))

    recognition.sort(key=lambda x: x.get("reading_order", 0))
    return recognition


# ---------------------------------------------------------------------------
# Build structured JSON page dict from element list
# ---------------------------------------------------------------------------

def _build_page_json(page_no: int, elements: list) -> dict:
    """Convert a flat list of element dicts into the structured page schema."""
    text_parts = []
    words = []
    numbers = []
    tables = []
    formulas = []
    reading_order_list = []

    for elem in elements:
        label = elem.get("label", "")
        raw_text = elem.get("text", "")
        ro = elem.get("reading_order", 0)
        reading_order_list.append(ro)

        if label == "tab":
            # Parse HTML → row structure
            rows = _html_table_to_rows(raw_text)
            tables.append({"rows": rows})
            # Also add flattened cell text for full-text
            flat = " ".join(cell for row in rows for cell in row)
            text_parts.append(flat)
            words.extend(flat.split())
        elif label == "equ":
            formulas.append(raw_text)
            text_parts.append(raw_text)
        elif label == "fig":
            # Figures: add placeholder text
            text_parts.append(raw_text)
        else:
            # para, sec_*, list, code, distorted_page, etc.
            text_parts.append(raw_text)
            words.extend(raw_text.split())

    # Extract numbers from all text
    full_text = " ".join(text_parts)
    numbers = re.findall(r"\b\d+(?:\.\d+)?\b", full_text)

    return {
        "page_no": page_no,
        "text": full_text.strip(),
        "words": words,
        "numbers": numbers,
        "tables": tables,
        "formulas": formulas,
        "reading_order": reading_order_list,
    }


# ---------------------------------------------------------------------------
# Main document parser
# ---------------------------------------------------------------------------

def parse_document(doc_path: str, model, save_dir: str,
                   max_batch_size: int = 4) -> dict:
    """Parse a document (image or PDF) and return the structured JSON dict."""
    doc_id = os.path.splitext(os.path.basename(doc_path))[0]
    ext = os.path.splitext(doc_path)[1].lower()

    t_start = time.perf_counter()
    pages_out = []

    if ext == ".pdf":
        images = convert_pdf_to_images(doc_path)
        if not images:
            raise RuntimeError(f"Failed to convert PDF: {doc_path}")
        for page_idx, pil_img in enumerate(images):
            print(f"  Page {page_idx + 1}/{len(images)}")
            name = f"{doc_id}_page_{page_idx + 1:03d}"
            elements = _parse_image_elements(
                pil_img, model, max_batch_size, save_dir, name)
            pages_out.append(_build_page_json(page_idx + 1, elements))
    else:
        pil_img = Image.open(doc_path).convert("RGB")
        elements = _parse_image_elements(
            pil_img, model, max_batch_size, save_dir, doc_id)
        pages_out.append(_build_page_json(1, elements))

    elapsed = round(time.perf_counter() - t_start, 3)

    return {
        "metadata": {
            "doc_id": doc_id,
            "num_pages": len(pages_out),
            "processing_time_sec": elapsed,
        },
        "pages": pages_out,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description="Dolphin document parser → structured JSON"
    )
    ap.add_argument("--model_path", default="./hf_model",
                    help="Path to Dolphin-v2 model")
    ap.add_argument("--input_path", required=True,
                    help="Image / PDF file or directory of files")
    ap.add_argument("--save_dir", default="./results",
                    help="Root directory for outputs")
    ap.add_argument("--max_batch_size", type=int, default=4,
                    help="Max elements per inference batch")
    args = ap.parse_args()

    # Collect files
    if os.path.isdir(args.input_path):
        exts = [".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG", ".pdf", ".PDF"]
        files = sorted(
            f for ext in exts
            for f in glob.glob(os.path.join(args.input_path, f"*{ext}"))
        )
    else:
        files = [args.input_path]

    # Output dirs
    os.makedirs(os.path.join(args.save_dir, "parsed_json"), exist_ok=True)
    setup_output_dirs(args.save_dir)

    # Load model
    print(f"Loading Dolphin model from {args.model_path} ...")
    model = DOLPHIN(args.model_path)

    # Process each file
    for fpath in files:
        print(f"\nProcessing: {fpath}")
        try:
            result = parse_document(fpath, model, args.save_dir,
                                    args.max_batch_size)
            out_path = os.path.join(
                args.save_dir, "parsed_json",
                f"{result['metadata']['doc_id']}.json"
            )
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"  ✅ Saved: {out_path}")
            print(f"  Pages: {result['metadata']['num_pages']} | "
                  f"Time: {result['metadata']['processing_time_sec']}s")
        except Exception as e:
            print(f"  ❌ Error: {e}")


if __name__ == "__main__":
    main()
