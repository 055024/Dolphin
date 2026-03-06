#!/usr/bin/env python3
"""
Evaluate already-parsed Dolphin results
For documents that have already been processed, just evaluate them
"""

import os
import sys
import json
import csv
import glob
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from evaluate_dolphin import (
    extract_ground_truth_from_pdf,
    normalize_text,
    calculate_wer,
    calculate_cer,
    calculate_text_accuracy,
    calculate_structure_score,
    calculate_table_structure_score,
    calculate_layout_score,
    load_dolphin_output,
    extract_dolphin_text
)


def evaluate_document(doc_path, json_path):
    """Evaluate a single document"""
    try:
        print(f"\n{'='*60}")
        print(f"Evaluating: {os.path.basename(doc_path)}")
        print(f"{'='*60}")
        
        # Extract ground truth
        ground_truth = extract_ground_truth_from_pdf(doc_path)
        gt_text_normalized = normalize_text(ground_truth['text'])
        
        # Load Dolphin output
        dolphin_output = load_dolphin_output(json_path)
        dolphin_text = extract_dolphin_text(dolphin_output)
        dolphin_text_normalized = normalize_text(dolphin_text)
        
        print(f"Ground truth words: {len(gt_text_normalized.split())}")
        print(f"Dolphin words: {len(dolphin_text_normalized.split())}")
        
        # Calculate metrics
        wer, wer_details = calculate_wer(gt_text_normalized, dolphin_text_normalized)
        cer = calculate_cer(gt_text_normalized, dolphin_text_normalized)
        text_accuracy = calculate_text_accuracy(gt_text_normalized, dolphin_text_normalized)
        structure_score = calculate_structure_score(ground_truth, dolphin_output)
        table_structure_score = calculate_table_structure_score(ground_truth, dolphin_output)
        layout_score = calculate_layout_score(ground_truth, dolphin_output)
        
        results = {
            'Document_ID': os.path.basename(doc_path),
            'WER': round(wer, 4),
            'CER': round(cer, 4),
            'Substitutions': wer_details['substitutions'],
            'Deletions': wer_details['deletions'],
            'Insertions': wer_details['insertions'],
            'Text_Accuracy': round(text_accuracy, 4),
            'Structure_Score': round(structure_score, 4),
            'Table_Structure_Score': round(table_structure_score, 4),
            'Layout_Score': round(layout_score, 4),
            'Processing_Time_Seconds': 'N/A',
            'Status': 'Success'
        }
        
        print(f"✅ WER: {wer*100:.2f}% | CER: {cer*100:.2f}% | Accuracy: {text_accuracy*100:.2f}%")
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'Document_ID': os.path.basename(doc_path),
            'WER': 'N/A',
            'CER': 'N/A',
            'Substitutions': 'N/A',
            'Deletions': 'N/A',
            'Insertions': 'N/A',
            'Text_Accuracy': 'N/A',
            'Structure_Score': 'N/A',
            'Table_Structure_Score': 'N/A',
            'Layout_Score': 'N/A',
            'Processing_Time_Seconds': 'N/A',
            'Status': f'Error: {str(e)}'
        }


def main():
    # Find all JSON files in batch_results
    json_files = glob.glob('./batch_results/output_json/*.json')
    json_files.sort()
    
    print(f"Found {len(json_files)} JSON files to evaluate")
    
    all_results = []
    
    for json_path in json_files:
        base_name = Path(json_path).stem
        
        # Try to find corresponding source document
        possible_docs = [
            f'./demo/page_imgs/{base_name}.jpeg',
            f'./demo/page_imgs/{base_name}.jpg',
            f'./demo/page_imgs/{base_name}.png',
            f'./demo/page_imgs/{base_name}.pdf',
        ]
        
        doc_path = None
        for p in possible_docs:
            if os.path.exists(p):
                doc_path = p
                break
        
        if not doc_path:
            print(f"⚠️  Could not find source document for {base_name}")
            continue
        
        # Evaluate
        results = evaluate_document(doc_path, json_path)
        all_results.append(results)
    
    # Save results
    output_csv = './demo_evaluation_results.csv'
    
    fieldnames = [
        'Document_ID', 'WER', 'CER', 'Substitutions', 'Deletions', 'Insertions',
        'Text_Accuracy', 'Structure_Score', 'Table_Structure_Score', 'Layout_Score',
        'Processing_Time_Seconds', 'Status'
    ]
    
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)
    
    print(f"\n{'='*80}")
    print(f"✅ Evaluation complete! Results saved to: {output_csv}")
    print(f"{'='*80}\n")
    
    # Print summary
    successful = sum(1 for r in all_results if r['Status'] == 'Success')
    
    if successful > 0:
        avg_wer = sum(float(r['WER']) for r in all_results if r['Status'] == 'Success') / successful
        avg_cer = sum(float(r['CER']) for r in all_results if r['Status'] == 'Success') / successful
        avg_text_acc = sum(float(r['Text_Accuracy']) for r in all_results if r['Status'] == 'Success') / successful
        
        print(f"Summary Statistics ({successful} successful documents):")
        print(f"  Average WER: {avg_wer*100:.2f}%")
        print(f"  Average CER: {avg_cer*100:.2f}%")
        print(f"  Average Text Accuracy: {avg_text_acc*100:.2f}%")
        print()


if __name__ == '__main__':
    main()
