"""
Dolphin Pipeline
================
End-to-end: parse a document with Dolphin → structured JSON → evaluate metrics.

Usage:
    python dolphin_pipeline.py \
        --model_path ./hf_model \
        --input_path ./demo/page_imgs/page_1.png \
        --save_dir   ./results \
        [--ground_truth ./gt.txt] \
        [--max_batch_size 4]

Outputs
-------
  results/
    parsed_json/<doc_id>.json       ← structured parsed JSON
    evaluation/<doc_id>_eval.json   ← metrics + linearised text
"""

import argparse
import glob
import json
import os

from dolphin_parse_json import DOLPHIN, parse_document
from dolphin_evaluate import evaluate, linearise, print_report
from utils.utils import setup_output_dirs


def run_pipeline(
    model_path: str,
    input_path: str,
    save_dir: str,
    ground_truth_path: str = None,
    max_batch_size: int = 4,
):
    # ------------------------------------------------------------------
    # Collect files
    # ------------------------------------------------------------------
    if os.path.isdir(input_path):
        exts = [".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG",
                ".pdf", ".PDF"]
        files = sorted(
            f for ext in exts
            for f in glob.glob(os.path.join(input_path, f"*{ext}"))
        )
    else:
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input not found: {input_path}")
        files = [input_path]

    if not files:
        print("No supported documents found. Exiting.")
        return

    # ------------------------------------------------------------------
    # Load model once
    # ------------------------------------------------------------------
    print(f"\n📦 Loading Dolphin model from: {model_path}")
    model = DOLPHIN(model_path)

    # ------------------------------------------------------------------
    # Output dirs
    # ------------------------------------------------------------------
    os.makedirs(os.path.join(save_dir, "parsed_json"), exist_ok=True)
    os.makedirs(os.path.join(save_dir, "evaluation"), exist_ok=True)
    setup_output_dirs(save_dir)

    # ------------------------------------------------------------------
    # Load ground truth (optional)
    # ------------------------------------------------------------------
    gt_text = None
    if ground_truth_path:
        if os.path.exists(ground_truth_path):
            with open(ground_truth_path, "r", encoding="utf-8") as f:
                gt_text = f.read()
            print(f"✅ Ground-truth loaded: {ground_truth_path}")
        else:
            print(f"⚠️  Ground-truth file not found: {ground_truth_path}. "
                  "Text metrics will be skipped.")

    # ------------------------------------------------------------------
    # Process files
    # ------------------------------------------------------------------
    all_metrics = []

    for fpath in files:
        print(f"\n{'='*60}")
        print(f"📄 Processing: {os.path.basename(fpath)}")
        print("=" * 60)

        try:
            # ── Step 1: Parse ──────────────────────────────────────────
            parsed = parse_document(fpath, model, save_dir, max_batch_size)
            doc_id = parsed["metadata"]["doc_id"]

            json_out = os.path.join(save_dir, "parsed_json", f"{doc_id}.json")
            with open(json_out, "w", encoding="utf-8") as f:
                json.dump(parsed, f, indent=2, ensure_ascii=False)
            print(f"  📁 Structured JSON → {json_out}")
            print(f"  Pages: {parsed['metadata']['num_pages']}  |  "
                  f"Parse time: {parsed['metadata']['processing_time_sec']}s")

            # ── Step 2: Evaluate ───────────────────────────────────────
            metrics = evaluate(parsed, gt_text)

            # Print human-readable report
            print_report(metrics, doc_id)

            # Show linearised text preview
            lin = linearise(parsed)
            print("── Linearised Text (first 500 chars) " + "─" * 20)
            print(lin[:500])
            if len(lin) > 500:
                print(f"  ... [{len(lin)-500} more chars]")
            print()

            # Save evaluation JSON
            eval_out = os.path.join(
                save_dir, "evaluation", f"{doc_id}_eval.json"
            )
            with open(eval_out, "w", encoding="utf-8") as f:
                json.dump(
                    {"doc_id": doc_id, "metrics": metrics,
                     "linearised_text": lin},
                    f, indent=2, ensure_ascii=False,
                )
            print(f"  📊 Evaluation JSON → {eval_out}")

            all_metrics.append({"doc_id": doc_id, "metrics": metrics})

        except Exception as e:
            print(f"  ❌ Error processing {fpath}: {e}")
            import traceback; traceback.print_exc()

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    if len(all_metrics) > 1:
        print("\n" + "=" * 60)
        print("BATCH SUMMARY")
        print("=" * 60)
        for item in all_metrics:
            m = item["metrics"]
            wer = m.get("WER", "N/A")
            acc = m.get("Text_Accuracy", "N/A")
            ls  = m.get("Layout_Score", "N/A")
            pt  = m.get("Processing_Time_Seconds", "—")
            wer_str = f"{wer:.2%}" if isinstance(wer, float) else str(wer)
            acc_str = f"{acc:.4f}" if isinstance(acc, float) else str(acc)
            ls_str  = f"{ls:.4f}" if isinstance(ls, float) else str(ls)
            print(f"  {item['doc_id']:<30}  WER={wer_str}  "
                  f"Acc={acc_str}  Layout={ls_str}  t={pt}s")
        print("=" * 60 + "\n")

    print(f"\n✅ All done. Outputs in: {os.path.abspath(save_dir)}")


def main():
    ap = argparse.ArgumentParser(
        description="Dolphin end-to-end pipeline: parse → JSON → evaluate"
    )
    ap.add_argument("--model_path", default="./hf_model",
                    help="Path to Dolphin-v2 model directory")
    ap.add_argument("--input_path", required=True,
                    help="Image / PDF file or directory of documents")
    ap.add_argument("--save_dir", default="./results",
                    help="Root output directory (default: ./results)")
    ap.add_argument("--ground_truth", default=None,
                    help="Optional plain-text ground-truth file")
    ap.add_argument("--max_batch_size", type=int, default=4,
                    help="Max elements per inference batch (default: 4)")
    args = ap.parse_args()

    run_pipeline(
        model_path=args.model_path,
        input_path=args.input_path,
        save_dir=args.save_dir,
        ground_truth_path=args.ground_truth,
        max_batch_size=args.max_batch_size,
    )


if __name__ == "__main__":
    main()
