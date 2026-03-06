#!/bin/bash
# Monitor batch processing progress

echo "======================================"
echo "BATCH PROCESSING PROGRESS MONITOR"
echo "======================================"
echo ""

# Count files in CSV
echo "📊 Current Results:"
total_lines=$(wc -l < test_docs_evaluation_results_FINAL.csv)
total_docs=$((total_lines - 1))  # Subtract header
echo "   Total documents evaluated: $total_docs"
echo ""

# Show latest entries
echo "📄 Latest 3 Results:"
tail -3 test_docs_evaluation_results_FINAL.csv | column -t -s','
echo ""

# Count JSON files
json_count=$(ls -1 batch_results/recognition_json/*.json 2>/dev/null | wc -l)
echo "📁 JSON files created: $json_count"
echo ""

# Show new files to process
echo "⏳ Remaining to process:"
echo "   1. 14pg_txt+Sci For_AI_generality_Mccarthy 1959.pdf (14 pages, ~42 min)"
echo "   2. 20PGS_1COL_TEXT+FIG+TABLES.pdf (20 pages, ~60 min)"
echo "   3. 3PG_PLAIN TEXT_NIIFs-India-Japan-Fund-invests-INR-500-cr-US-57-mn-in-EKA-Mobility.pdf (3 pages, ~9 min)"
echo "   4. 47pg_photo+2col+fig+charts+table_capegemini 2024.pdf (47 pages, ~2.4 hours)"
echo "   5. 85pg_photo+Table+3 Col+Fig _curro holding 2024.pdf (85 pages, ~4.3 hours)"
echo ""
echo "   Total: 169 pages (~8-9 hours on CPU)"
echo ""

echo "======================================"
echo "To check detailed progress:"
echo "  tail -f <terminal output>"
echo "  watch -n 60 ./monitor_progress.sh"
echo "======================================"
