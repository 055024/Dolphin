# Dolphin Document Parsing Evaluation Report

## Document Information
- **Document ID**: 1PG_Press-release_1GW_v4_clean.pdf
- **Total Pages**: 1
- **Processing Time**: 180.0 seconds (3 minutes)

---

## Performance Metrics Summary

### Error Rates
| Metric | Value | Percentage |
|--------|-------|------------|
| **WER (Word Error Rate)** | 0.0360 | 3.60% |
| **CER (Character Error Rate)** | 0.0184 | 1.84% |

### Error Breakdown
| Error Type | Count |
|------------|-------|
| **Substitutions** | 9 |
| **Deletions** | 0 |
| **Insertions** | 1 |

### Accuracy Scores
| Metric | Score | Percentage |
|--------|-------|------------|
| **Text Accuracy** | 0.9816 | 98.16% |
| **Structure Score** | 0.6667 | 66.67% |
| **Table Structure Score** | 1.0000 | 100.00% |
| **Layout Score** | 0.8333 | 83.33% |

### Text Statistics
| Metric | Ground Truth | Dolphin Output |
|--------|--------------|----------------|
| **Total Words** | 389 | 394 |
| **Total Characters** | 2554 | 2587 |

---

## Performance Analysis

### ✅ Strengths
1. **Excellent Text Accuracy (98.16%)**: Dolphin accurately extracted almost all text from the document
2. **Perfect Table Structure Score (100%)**: Successfully preserved table structures
3. **Strong Layout Preservation (83.33%)**: Good understanding of document layout
4. **Low Error Rates**: WER of 3.60% and CER of 1.84% indicate high-quality extraction

### ⚠️ Areas for Improvement
1. **Structure Score (66.67%)**: Some document elements may not have been perfectly segmented
2. **Word Substitutions**: 9 words were substituted (could be OCR errors or formatting differences)
3. **Word Count Difference**: 5 more words in output suggests possible text splitting or formatting variations

### 📊 Overall Assessment
Dolphin demonstrates **strong performance** on this document with:
- Near-perfect text extraction accuracy
- Excellent structural understanding
- Minimal errors in recognition
- Good preservation of document layout

The processing time of 3 minutes on CPU is reasonable for a 1-page document with a 3B parameter model.

---

## Detailed Metrics Table

| Metric | Value |
|--------|-------|
| Document_ID | 1PG_Press-release_1GW_v4_clean.pdf |
| WER | 0.0360 |
| CER | 0.0184 |
| Substitutions | 9 |
| Deletions | 0 |
| Insertions | 1 |
| Text_Accuracy | 0.9816 |
| Structure_Score | 0.6667 |
| Table_Structure_Score | 1.0000 |
| Layout_Score | 0.8333 |
| Processing_Time_Seconds | 180.0 |
| Ground_Truth_Words | 389 |
| Dolphin_Output_Words | 394 |
| Ground_Truth_Chars | 2554 |
| Dolphin_Output_Chars | 2587 |

---

## Conclusion

Dolphin-v2 successfully parsed this press release document with high accuracy. The model achieved:
- **98.16% text accuracy**
- **Low error rates** (WER: 3.60%, CER: 1.84%)
- **Strong structural understanding** with 83.33% layout score

The evaluation demonstrates Dolphin's capability for high-quality document parsing, particularly for business documents like press releases. The minimal errors (9 substitutions, 0 deletions, 1 insertion) indicate robust OCR and text extraction capabilities.

---

*Generated on: 2026-03-06*
*Evaluation Tool: Dolphin Evaluation Script v1.0*
