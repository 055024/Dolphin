"""
Dolphin Evaluate
================
Linearises the structured JSON produced by dolphin_parse_json.py and computes:

  WER, CER, Substitutions, Deletions, Insertions,
  Text_Accuracy, Structure_Score, Table_Structure_Score,
  Layout_Score, Processing_Time_Seconds

Usage (with ground truth):
    python dolphin_evaluate.py \
        --parsed_json ./results/parsed_json/page_1.json \
        --ground_truth ./my_ground_truth.txt

Usage (without ground truth – text-independent metrics only):
    python dolphin_evaluate.py \
        --parsed_json ./results/parsed_json/page_1.json

Ground-truth format:
  Plain text file. Use  ---  (three dashes on its own line) to separate pages;
  page 1 text before the first separator, page 2 between 1st and 2nd, etc.
"""

import argparse
import json
import math
import re
import os


# ---------------------------------------------------------------------------
# Lineariser
# ---------------------------------------------------------------------------

def linearise(parsed_json: dict) -> str:
    """Return the full document as a single plain-text string
    (pages separated by newlines, tables flattened to pipe-delimited rows)."""
    lines = []
    for page in parsed_json.get("pages", []):
        # Use the pre-built full text (already in reading order)
        page_text = page.get("text", "").strip()
        if page_text:
            lines.append(page_text)
        lines.append("")          # blank line between pages
    return "\n".join(lines).strip()


def linearise_per_page(parsed_json: dict):
    """Return list of per-page plain-text strings."""
    results = []
    for page in parsed_json.get("pages", []):
        results.append(page.get("text", "").strip())
    return results


# ---------------------------------------------------------------------------
# WER / CER helpers (using jiwer if available, else built-in)
# ---------------------------------------------------------------------------

def _normalise(text: str) -> str:
    """Lower-case and collapse whitespace."""
    return re.sub(r"\s+", " ", text.lower()).strip()


def _edit_ops(ref_tokens, hyp_tokens):
    """Wagner-Fischer edit distance with backtracking.
    Returns (subs, dels, ins)."""
    m, n = len(ref_tokens), len(hyp_tokens)
    # DP table
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if ref_tokens[i - 1] == hyp_tokens[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j - 1],  # sub
                                    dp[i - 1][j],      # del
                                    dp[i][j - 1])      # ins
    # Backtrack
    subs = dels = ins = 0
    i, j = m, n
    while i > 0 or j > 0:
        if i > 0 and j > 0 and ref_tokens[i-1] == hyp_tokens[j-1]:
            i -= 1; j -= 1
        elif i > 0 and j > 0 and dp[i][j] == dp[i-1][j-1] + 1:
            subs += 1; i -= 1; j -= 1
        elif i > 0 and dp[i][j] == dp[i-1][j] + 1:
            dels += 1; i -= 1
        else:
            ins += 1; j -= 1
    return subs, dels, ins


def compute_wer_cer(reference: str, hypothesis: str):
    """Compute WER, CER, and edit operation counts."""
    ref_n = _normalise(reference)
    hyp_n = _normalise(hypothesis)

    # Word-level
    ref_words = ref_n.split()
    hyp_words = hyp_n.split()
    w_subs, w_dels, w_ins = _edit_ops(ref_words, hyp_words)
    n_ref_words = max(len(ref_words), 1)
    wer = (w_subs + w_dels + w_ins) / n_ref_words

    # Char-level
    ref_chars = list(ref_n)
    hyp_chars = list(hyp_n)
    c_subs, c_dels, c_ins = _edit_ops(ref_chars, hyp_chars)
    n_ref_chars = max(len(ref_chars), 1)
    cer = (c_subs + c_dels + c_ins) / n_ref_chars

    return {
        "WER": round(wer, 4),
        "CER": round(cer, 4),
        "Substitutions": w_subs,
        "Deletions": w_dels,
        "Insertions": w_ins,
        "Text_Accuracy": round(max(0.0, 1.0 - wer), 4),
    }


# ---------------------------------------------------------------------------
# Structure / Layout scores
# ---------------------------------------------------------------------------

def _teds_lite(pred_tables, ref_tables):
    """
    Simple TEDS-lite: for each matched table compare cell-level accuracy.
    Returns a 0-1 score.
    """
    if not ref_tables:
        return 1.0 if not pred_tables else 0.0

    total_ref_cells = 0
    total_matched_cells = 0

    n = min(len(pred_tables), len(ref_tables))
    for i in range(n):
        pred_rows = pred_tables[i].get("rows", [])
        ref_rows = ref_tables[i].get("rows", [])
        for r_idx, ref_row in enumerate(ref_rows):
            for c_idx, ref_cell in enumerate(ref_row):
                total_ref_cells += 1
                try:
                    pred_cell = pred_rows[r_idx][c_idx]
                    # Normalise and compare
                    if _normalise(pred_cell) == _normalise(ref_cell):
                        total_matched_cells += 1
                except IndexError:
                    pass

    # Penalise missing tables
    for i in range(n, len(ref_tables)):
        for row in ref_tables[i].get("rows", []):
            total_ref_cells += len(row)

    if total_ref_cells == 0:
        return 1.0
    return round(total_matched_cells / total_ref_cells, 4)


def compute_structure_scores(parsed_json: dict, ref_json: dict = None):
    """
    Structure_Score     : ratio of non-text elements correctly detected
    Table_Structure_Score : TEDS-lite across all tables
    Layout_Score        : reading-order completeness vs expected
    """
    pred_pages = parsed_json.get("pages", [])

    if ref_json is None:
        # Without ground truth: compute self-consistency scores
        total_elements = sum(len(p.get("reading_order", [])) for p in pred_pages)
        total_tables = sum(len(p.get("tables", [])) for p in pred_pages)
        total_formulas = sum(len(p.get("formulas", [])) for p in pred_pages)

        structure_score = (
            round((total_tables + total_formulas) / max(total_elements, 1), 4)
        )
        layout_score = 1.0 if total_elements > 0 else 0.0
        table_structure_score = 1.0 if total_tables > 0 else 0.0  # no GT to compare

        return {
            "Structure_Score": structure_score,
            "Table_Structure_Score": table_structure_score,
            "Layout_Score": layout_score,
        }

    # With reference JSON
    ref_pages = ref_json.get("pages", [])

    # Structure Score: overlap of detected element counts
    pred_elem_counts = [len(p.get("reading_order", [])) for p in pred_pages]
    ref_elem_counts = [len(p.get("reading_order", [])) for p in ref_pages]
    structure_numerator = sum(
        min(p, r) for p, r in zip(pred_elem_counts, ref_elem_counts)
    )
    structure_denominator = max(sum(ref_elem_counts), 1)
    structure_score = round(structure_numerator / structure_denominator, 4)

    # TEDS-lite across all pages
    all_pred_tables = [t for p in pred_pages for t in p.get("tables", [])]
    all_ref_tables = [t for p in ref_pages for t in p.get("tables", [])]
    teds = _teds_lite(all_pred_tables, all_ref_tables)

    # Layout Score: reading-order element count similarity
    pred_ro_total = sum(len(p.get("reading_order", [])) for p in pred_pages)
    ref_ro_total = sum(len(p.get("reading_order", [])) for p in ref_pages)
    layout_score = round(
        min(pred_ro_total, ref_ro_total) / max(ref_ro_total, 1), 4
    )

    return {
        "Structure_Score": structure_score,
        "Table_Structure_Score": teds,
        "Layout_Score": layout_score,
    }


# ---------------------------------------------------------------------------
# Full evaluation
# ---------------------------------------------------------------------------

def evaluate(parsed_json: dict, ground_truth_text: str = None,
             ref_json: dict = None) -> dict:
    """
    Run all metrics and return an evaluation dict.

    Args:
        parsed_json:        Output of dolphin_parse_json.py
        ground_truth_text:  Optional raw ground-truth text string
        ref_json:           Optional reference parsed JSON (for structure scores)
    """
    hypothesis = linearise(parsed_json)
    proc_time = parsed_json.get("metadata", {}).get("processing_time_sec", 0)

    metrics = {"Processing_Time_Seconds": proc_time}

    if ground_truth_text:
        reference = _normalise(ground_truth_text)
        text_metrics = compute_wer_cer(reference, hypothesis)
        metrics.update(text_metrics)
    else:
        na = "N/A (no ground truth provided)"
        metrics.update({
            "WER": na,
            "CER": na,
            "Substitutions": na,
            "Deletions": na,
            "Insertions": na,
            "Text_Accuracy": na,
        })

    struct_metrics = compute_structure_scores(parsed_json, ref_json)
    metrics.update(struct_metrics)

    return metrics


# ---------------------------------------------------------------------------
# Pretty report
# ---------------------------------------------------------------------------

def print_report(metrics: dict, doc_id: str = ""):
    title = f"Evaluation Report — {doc_id}" if doc_id else "Evaluation Report"
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

    order = [
        "WER", "CER", "Substitutions", "Deletions", "Insertions",
        "Text_Accuracy", "Structure_Score", "Table_Structure_Score",
        "Layout_Score", "Processing_Time_Seconds",
    ]
    for key in order:
        val = metrics.get(key, "—")
        if isinstance(val, float):
            if key in ("WER", "CER"):
                print(f"  {key:<28} {val:.2%}")
            elif key == "Processing_Time_Seconds":
                print(f"  {key:<28} {val:.3f} s")
            else:
                print(f"  {key:<28} {val:.4f}")
        else:
            print(f"  {key:<28} {val}")
    print("=" * 60 + "\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description="Evaluate Dolphin parsed JSON against optional ground truth"
    )
    ap.add_argument("--parsed_json", required=True,
                    help="Path to parsed JSON from dolphin_parse_json.py")
    ap.add_argument("--ground_truth", default=None,
                    help="Plain-text ground-truth file (pages separated by ---)")
    ap.add_argument("--ref_json", default=None,
                    help="Optional reference parsed JSON for structure scores")
    ap.add_argument("--save_dir", default="./results",
                    help="Directory to save evaluation JSON")
    args = ap.parse_args()

    # Load parsed JSON
    with open(args.parsed_json, "r", encoding="utf-8") as f:
        parsed = json.load(f)

    # Load ground truth if provided
    gt_text = None
    if args.ground_truth:
        with open(args.ground_truth, "r", encoding="utf-8") as f:
            gt_text = f.read()

    # Load reference JSON if provided
    ref_json = None
    if args.ref_json:
        with open(args.ref_json, "r", encoding="utf-8") as f:
            ref_json = json.load(f)

    # Evaluate
    metrics = evaluate(parsed, gt_text, ref_json)
    doc_id = parsed.get("metadata", {}).get("doc_id", "unknown")

    # Print report
    print_report(metrics, doc_id)

    # Also show linearised text
    print("--- Linearised Text Preview (first 1000 chars) ---")
    lin = linearise(parsed)
    print(lin[:1000])
    if len(lin) > 1000:
        print(f"... [{len(lin) - 1000} more chars]")
    print()

    # Save evaluation JSON
    out_dir = os.path.join(args.save_dir, "evaluation")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{doc_id}_eval.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"doc_id": doc_id, "metrics": metrics, "linearised_text": lin},
                  f, indent=2, ensure_ascii=False)
    print(f"Evaluation saved to: {out_path}")


if __name__ == "__main__":
    main()
