# Batch Processing Status Report

## Overview
This report summarizes the batch processing and evaluation of documents using Dolphin document parser.

---

## Processing Summary

### ✅ Completed: Demo Folder (Image Files)
- **Location**: `demo/page_imgs/`
- **Documents Processed**: 9 image files (page_0.jpeg through page_9.jpeg)
- **Total Processing Time**: ~73 minutes
- **JSON Outputs**: `batch_results/output_json/`
- **Evaluation Results**: `demo_evaluation_results.csv`

**Note**: These are image files (JPEG/PNG), not PDFs, so there is no ground truth text to extract for WER/CER calculation. The evaluation shows 0 words for both ground truth and Dolphin output, which is expected for pure images without embedded text.

### 🔄 In Progress: Test-Docs Folder (PDF Documents)
- **Location**: `test-docs/`
- **Documents to Process**: 5 PDF files with extractable text
- **Current Status**: Processing document 1/5 (1PG_Press-release_1GW_v4_clean.pdf)
- **JSON Outputs**: `output_json_testdocs/`
- **Evaluation Results**: `test_docs_evaluation_results.csv` (will be updated as processing completes)

**Document List**:
1. ✅ `1PG_Press-release_1GW_v4_clean.pdf` (118KB, 1 page) - Currently processing
2. ⏳ `1PG_TXT_DP-World-signs-MOU-with-Indian-National-Investment-and-Infrastructure-Fu.pdf` (31KB, 1 page)
3. ⏳ `2PG_TXT_Press-Release-NIIF-and-Abu-Dhabi-Investment-Authority-finalise-investment-agreement-worth-US-1-billion-October-16-2017-converted.pdf` (126KB, 2 pages)
4. ⏳ `2PG_TXT_Press-Release-NIIF-Sells-Two-Road-Assets-To-Cube-Highways.pdf` (200KB, 2 pages)
5. ⏳ `2PG_TXT_Third-Meeting-of-the-Governing-Council-of-National-Investment-and-Infras.22.pdf` (50KB, 2 pages)

---

## Evaluation Metrics

For each document, the following metrics are calculated and saved to CSV:

| Metric | Description |
|--------|-------------|
| **Document_ID** | Filename of the document |
| **WER** | Word Error Rate (0-1, lower is better) |
| **CER** | Character Error Rate (0-1, lower is better) |
| **Substitutions** | Number of word substitutions |
| **Deletions** | Number of word deletions |
| **Insertions** | Number of word insertions |
| **Text_Accuracy** | 1 - CER (0-1, higher is better) |
| **Structure_Score** | Document structure recognition accuracy |
| **Table_Structure_Score** | Table detection accuracy |
| **Layout_Score** | Layout understanding accuracy |
| **Processing_Time_Seconds** | Time taken to parse the document |
| **Status** | Processing status (Success/Error) |

---

## Expected Timeline

- **Single page document**: ~180 seconds (3 minutes) on CPU
- **Multi-page document**: ~360 seconds (6 minutes) on CPU
- **Test-docs folder (5 docs, ~8 pages total)**: ~24 minutes total

---

## Output Files

### Demo Folder Results
- **JSON Outputs**: `/home/ashok/Documents/GitHub/Dolphin/batch_results/output_json/`
  - 9 JSON files (page_0.json through page_9.json)
- **CSV Results**: `/home/ashok/Documents/GitHub/Dolphin/demo_evaluation_results.csv`

### Test-Docs Folder Results (In Progress)
- **JSON Outputs**: `/home/ashok/Documents/GitHub/Dolphin/output_json_testdocs/`
  - Will contain 5 JSON files after processing
- **CSV Results**: `/home/ashok/Documents/GitHub/Dolphin/test_docs_evaluation_results.csv`
  - Updated incrementally as each document completes

---

## How to Monitor Progress

### Check Current Status
```bash
# See current terminal output
# Terminal ID: 0592f492-a2c3-4267-97ff-1ef7b4809544

# Check CSV results (updates after each document)
cat test_docs_evaluation_results.csv

# Count completed JSON files
ls -1 output_json_testdocs/ | wc -l
```

### Check Individual Results
```bash
# View a specific JSON output
cat output_json_testdocs/1PG_Press-release_1GW_v4_clean.json

# View evaluation CSV
column -t -s',' test_docs_evaluation_results.csv
```

---

## Next Steps

Once the test-docs processing completes (~24 minutes):

1. ✅ All 5 PDF documents will be parsed and evaluated
2. ✅ `test_docs_evaluation_results.csv` will contain complete metrics
3. ✅ JSON outputs will be available in `output_json_testdocs/`
4. 📊 You can analyze WER, CER, and accuracy metrics for each document

---

## Scripts Created

1. **`batch_process_evaluate.py`**: Main batch processing script
   - Processes multiple documents with Dolphin
   - Evaluates each against ground truth
   - Generates comprehensive CSV results

2. **`evaluate_existing_results.py`**: Post-processing evaluation script
   - Evaluates already-parsed documents
   - Useful for re-running evaluation without re-parsing

3. **`evaluate_dolphin.py`**: Core evaluation functions
   - WER/CER calculation
   - Structure and layout scoring
   - Ground truth extraction from PDFs

---

## Performance Notes

- **CPU Processing**: ~180 seconds per page
- **GPU Processing**: Would be ~10-20x faster (18 seconds per page)
- **Optimization**: Consider GPU inference or quantization for production use

---

*Report generated: March 6, 2026*
