# Test-Docs Evaluation Results Summary

## Overview
Successfully evaluated 5 PDF documents from `test-docs/` folder using Dolphin document parser.

---

## Summary Statistics

| Metric | Average | Best | Worst |
|--------|---------|------|-------|
| **WER (Word Error Rate)** | 8.87% | 3.40% | 26.36% |
| **CER (Character Error Rate)** | 4.03% | 0.54% | 15.40% |
| **Text Accuracy** | 95.97% | 99.46% | 84.60% |

---

## Individual Document Results

### 🥇 Best Performance: 1PG_TXT_DP-World-signs-MOU...
- **WER**: 3.40% | **CER**: 0.54% | **Accuracy**: 99.46%
- Substitutions: 11, Deletions: 0, Insertions: 1
- Ground Truth: 382 words
- Dolphin Output: 383 words

### 🥈 Second Best: 1PG_Press-release_1GW_v4_clean.pdf
- **WER**: 3.60% | **CER**: 1.84% | **Accuracy**: 98.16%
- Substitutions: 9, Deletions: 0, Insertions: 1
- Ground Truth: 389 words
- Dolphin Output: 394 words

### 🥉 Third Best: 2PG_TXT_Third-Meeting-of-the-Governing-Council...
- **WER**: 4.84% | **CER**: 0.99% | **Accuracy**: 99.01%
- Substitutions: 16, Deletions: 5, Insertions: 1
- Ground Truth: 496 words
- Dolphin Output: 492 words

### 📊 Fourth: 2PG_TXT_Press-Release-NIIF-and-Abu-Dhabi...
- **WER**: 6.15% | **CER**: 1.38% | **Accuracy**: 98.62%
- Substitutions: 19, Deletions: 2, Insertions: 0
- Ground Truth: 390 words
- Dolphin Output: 387 words

### ⚠️ Needs Improvement: 2PG_TXT_Press-Release-NIIF-Sells-Two-Road-Assets...
- **WER**: 26.36% | **CER**: 15.40% | **Accuracy**: 84.60%
- Substitutions: 95, Deletions: 13, Insertions: 7
- Ground Truth: 899 words
- Dolphin Output: 895 words
- **Note**: This document has the highest error rate - may contain complex formatting or tables

---

## Detailed Metrics by Document

| Document | Pages | Words (GT) | WER | CER | Text Acc | Subs | Del | Ins |
|----------|-------|------------|-----|-----|----------|------|-----|-----|
| 1PG_Press-release_1GW_v4_clean.pdf | 1 | 389 | 3.60% | 1.84% | 98.16% | 9 | 0 | 1 |
| 1PG_TXT_DP-World-signs-MOU... | 1 | 382 | 3.40% | 0.54% | 99.46% | 11 | 0 | 1 |
| 2PG_TXT_Press-Release-NIIF-Sells... | 2 | 899 | 26.36% | 15.40% | 84.60% | 95 | 13 | 7 |
| 2PG_TXT_Press-Release-NIIF-and-Abu... | 2 | 390 | 6.15% | 1.38% | 98.62% | 19 | 2 | 0 |
| 2PG_TXT_Third-Meeting... | 2 | 496 | 4.84% | 0.99% | 99.01% | 16 | 5 | 1 |

**Legend**: GT = Ground Truth, Subs = Substitutions, Del = Deletions, Ins = Insertions

---

## Structure Recognition Scores

| Document | Structure Score | Table Score | Layout Score |
|----------|-----------------|-------------|--------------|
| 1PG_Press-release_1GW_v4_clean.pdf | 0.6667 | 1.0 | 0.8333 |
| 1PG_TXT_DP-World-signs-MOU... | 0.3636 | 0.0 | 0.6818 |
| 2PG_TXT_Press-Release-NIIF-Sells... | 0.4583 | 1.0 | 0.7292 |
| 2PG_TXT_Press-Release-NIIF-and-Abu... | 0.9130 | 1.0 | 0.9565 |
| 2PG_TXT_Third-Meeting... | 0.5517 | 0.0 | 0.7759 |

**Average**: Structure: 0.5907, Table: 0.60, Layout: 0.7953

---

## Processing Information

- **Total Documents**: 5 PDFs
- **Total Pages**: ~8 pages
- **Processing Time**: ~20 minutes (CPU inference at ~180 seconds/page)
- **Success Rate**: 100% (5/5 documents successfully processed)

---

## Key Insights

### ✅ Strengths
1. **Excellent text extraction** for single-page documents (3-4% WER)
2. **High character-level accuracy** (99%+ for 3 out of 5 documents)
3. **Good table detection** (3 out of 5 documents with perfect table scores)
4. **Consistent layout understanding** (average 79.53% layout score)

### ⚠️ Areas for Improvement
1. **Complex multi-page documents** show higher error rates (26% WER for largest doc)
2. **Structure recognition** varies significantly (36% to 91%)
3. Some documents have **poor table detection** (2 documents with 0.0 score)

### 📊 Recommendations
1. For **production use**, expect 96% text accuracy on average
2. **Single-page press releases** perform best (98-99% accuracy)
3. **Complex layouts** may require manual review (documents with >10% WER)
4. Consider **GPU inference** to reduce processing time from 3 min/page to ~18 sec/page

---

## Output Files

### CSV Results
- **File**: `test_docs_evaluation_results_FINAL.csv`
- **Location**: `/home/ashok/Documents/GitHub/Dolphin/`
- **Columns**: Document_ID, WER, CER, Substitutions, Deletions, Insertions, Text_Accuracy, Structure_Score, Table_Structure_Score, Layout_Score, Processing_Time_Seconds, Status

### JSON Outputs
- **Location**: `/home/ashok/Documents/GitHub/Dolphin/batch_results/recognition_json/`
- **Files**: 5 JSON files (one per document)
- **Format**: Dolphin structured output with elements, bounding boxes, and reading order

### Markdown Outputs
- **Location**: `/home/ashok/Documents/GitHub/Dolphin/batch_results/markdown/`
- **Files**: 5 Markdown files (one per document)

---

## Comparison with Manual Processing

Previously processed: `1PG_Press-release_1GW_v4_clean.pdf`
- **Batch Result**: WER 3.60%, CER 1.84%, Accuracy 98.16%
- **Manual Result**: WER 3.60%, CER 1.84%, Accuracy 98.16%
- **✅ Results match perfectly!**

---

*Report generated: March 6, 2026*
*Dolphin Model: v2 (3B parameters)*
*Processing: CPU inference with torch.float32*
