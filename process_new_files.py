#!/usr/bin/env python3
"""
Process NEW files in test-docs folder and append evaluation results to existing CSV
"""

import os
import sys
import time
import json
import csv
import glob
from pathlib import Path
import subprocess

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


def get_already_processed_files(csv_path):
    """Get list of already processed document IDs from CSV"""
    if not os.path.exists(csv_path):
        return set()
    
    processed = set()
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            processed.add(row['Document_ID'])
    
    return processed


def process_single_document(pdf_path, model_path):
    """Process a single document with Dolphin"""
    print(f"\n{'='*80}")
    print(f"Processing: {os.path.basename(pdf_path)}")
    print(f"{'='*80}")
    
    base_name = Path(pdf_path).stem
    json_output_path = f"./batch_results/recognition_json/{base_name}.json"
    
    # Check if already processed
    if os.path.exists(json_output_path):
        print(f"⚠️  Already processed. Using existing output.")
        return json_output_path, 0.0
    
    # Run Dolphin parsing
    cmd = [
        'python', 'demo_page.py',
        '--model_path', model_path,
        '--input_path', pdf_path,
        '--save_dir', './batch_results',
        '--max_batch_size', '4'
    ]
    
    print(f"Running: {' '.join(cmd)}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout for large documents
        )
        
        processing_time = time.time() - start_time
        
        if result.returncode != 0:
            print(f"❌ Error processing document:")
            print(result.stderr[-2000:])  # Last 2000 chars of error
            return None, processing_time
        
        # Check if JSON was created
        if os.path.exists(json_output_path):
            print(f"✅ Processing complete in {processing_time:.2f} seconds ({processing_time/60:.2f} minutes)")
            return json_output_path, processing_time
        else:
            print(f"⚠️  No JSON output found at {json_output_path}")
            return None, processing_time
        
    except subprocess.TimeoutExpired:
        processing_time = time.time() - start_time
        print(f"❌ Timeout after {processing_time:.2f} seconds")
        return None, processing_time
    except Exception as e:
        processing_time = time.time() - start_time
        print(f"❌ Error: {str(e)}")
        return None, processing_time


def evaluate_document(doc_path, json_path, processing_time):
    """Evaluate a single document"""
    try:
        print(f"\nEvaluating: {os.path.basename(doc_path)}")
        
        # Extract ground truth
        ground_truth = extract_ground_truth_from_pdf(doc_path)
        gt_text_normalized = normalize_text(ground_truth['text'])
        
        # Load Dolphin output
        dolphin_output = load_dolphin_output(json_path)
        dolphin_text = extract_dolphin_text(dolphin_output)
        dolphin_text_normalized = normalize_text(dolphin_text)
        
        gt_words = len(gt_text_normalized.split())
        dolphin_words = len(dolphin_text_normalized.split())
        
        print(f"Ground truth: {gt_words} words, {len(gt_text_normalized)} chars")
        print(f"Dolphin output: {dolphin_words} words, {len(dolphin_text_normalized)} chars")
        
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
            'Processing_Time_Seconds': round(processing_time, 2),
            'Status': 'Success'
        }
        
        print(f"✅ WER: {wer*100:.2f}% | CER: {cer*100:.2f}% | Accuracy: {text_accuracy*100:.2f}%")
        
        return results
        
    except Exception as e:
        print(f"❌ Evaluation error: {str(e)}")
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
            'Processing_Time_Seconds': round(processing_time, 2) if processing_time else 'N/A',
            'Status': f'Error: {str(e)}'
        }


def append_to_csv(results, csv_path):
    """Append results to existing CSV"""
    fieldnames = [
        'Document_ID', 'WER', 'CER', 'Substitutions', 'Deletions', 'Insertions',
        'Text_Accuracy', 'Structure_Score', 'Table_Structure_Score', 'Layout_Score',
        'Processing_Time_Seconds', 'Status'
    ]
    
    # Append mode
    with open(csv_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerow(results)
    
    print(f"📊 Results appended to: {csv_path}")


def main():
    input_folder = './test-docs'
    model_path = './hf_model'
    output_csv = './test_docs_evaluation_results_FINAL.csv'
    
    # Get already processed files
    already_processed = get_already_processed_files(output_csv)
    print(f"\n{'='*80}")
    print(f"INCREMENTAL BATCH PROCESSING")
    print(f"{'='*80}")
    print(f"Already processed: {len(already_processed)} documents")
    print(f"Existing results: {output_csv}")
    print(f"{'='*80}\n")
    
    # Find all PDF files
    all_pdfs = glob.glob(os.path.join(input_folder, '*.pdf'))
    all_pdfs.sort()
    
    # Filter out already processed
    new_pdfs = [pdf for pdf in all_pdfs if os.path.basename(pdf) not in already_processed]
    
    if not new_pdfs:
        print("✅ No new documents to process!")
        return
    
    print(f"Found {len(new_pdfs)} NEW document(s) to process:\n")
    for idx, pdf in enumerate(new_pdfs, 1):
        size = os.path.getsize(pdf) / (1024 * 1024)  # Size in MB
        print(f"  {idx}. {os.path.basename(pdf)} ({size:.2f} MB)")
    
    print(f"\n{'='*80}\n")
    
    total_start = time.time()
    
    for idx, pdf_path in enumerate(new_pdfs, 1):
        print(f"\n{'#'*80}")
        print(f"Document {idx}/{len(new_pdfs)}: {os.path.basename(pdf_path)}")
        print(f"{'#'*80}")
        
        try:
            # Process with Dolphin
            json_path, processing_time = process_single_document(pdf_path, model_path)
            
            if json_path and os.path.exists(json_path):
                # Evaluate
                results = evaluate_document(pdf_path, json_path, processing_time)
            else:
                results = {
                    'Document_ID': os.path.basename(pdf_path),
                    'WER': 'N/A',
                    'CER': 'N/A',
                    'Substitutions': 'N/A',
                    'Deletions': 'N/A',
                    'Insertions': 'N/A',
                    'Text_Accuracy': 'N/A',
                    'Structure_Score': 'N/A',
                    'Table_Structure_Score': 'N/A',
                    'Layout_Score': 'N/A',
                    'Processing_Time_Seconds': round(processing_time, 2),
                    'Status': 'Processing Failed'
                }
            
            # Append to CSV immediately
            append_to_csv(results, output_csv)
            
        except Exception as e:
            print(f"❌ Critical error: {str(e)}")
            continue
    
    total_time = time.time() - total_start
    
    print(f"\n{'='*80}")
    print(f"BATCH PROCESSING COMPLETE")
    print(f"{'='*80}")
    print(f"New documents processed: {len(new_pdfs)}")
    print(f"Total time: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
    print(f"Results appended to: {output_csv}")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    main()
