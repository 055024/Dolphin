#!/usr/bin/env python3
"""
Batch Document Processing and Evaluation for Dolphin
Processes multiple documents, evaluates them, and generates a comprehensive CSV report
"""

import os
import sys
import time
import json
import csv
import glob
from pathlib import Path
from datetime import datetime
import argparse

# Add current directory to path for imports
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


def process_single_document_with_dolphin(pdf_path, model_path, output_json_dir):
    """
    Process a single document using Dolphin and return processing time
    
    Returns:
        tuple: (json_output_path, processing_time_seconds)
    """
    import subprocess
    
    print(f"\n{'='*80}")
    print(f"Processing: {os.path.basename(pdf_path)}")
    print(f"{'='*80}")
    
    # Prepare output path
    base_name = Path(pdf_path).stem
    json_output_path = os.path.join(output_json_dir, f"{base_name}.json")
    
    # Check if already processed
    if os.path.exists(json_output_path):
        print(f"⚠️  Already processed. Using existing output: {json_output_path}")
        # Try to get processing time from file (won't be accurate, but we'll use 0)
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
            timeout=600  # 10 minute timeout per document
        )
        
        processing_time = time.time() - start_time
        
        if result.returncode != 0:
            print(f"❌ Error processing document:")
            print(result.stderr)
            return None, processing_time
        
        # Find the generated JSON file in save_dir/output_json/
        # demo_page.py saves to save_dir/output_json/filename.json
        json_path_in_save_dir = f"./batch_results/output_json/{base_name}.json"
        
        if not os.path.exists(json_path_in_save_dir):
            print(f"⚠️  No JSON output found for {base_name} at {json_path_in_save_dir}")
            # Also check recognition_json for older versions
            alt_path = f"./batch_results/recognition_json/{base_name}.json"
            if os.path.exists(alt_path):
                json_path_in_save_dir = alt_path
            else:
                return None, processing_time
        
        # Copy to output directory
        import shutil
        shutil.copy(json_path_in_save_dir, json_output_path)
        
        print(f"✅ Processing complete in {processing_time:.2f} seconds")
        print(f"📄 Output saved to: {json_output_path}")
        
        return json_output_path, processing_time
        
    except subprocess.TimeoutExpired:
        processing_time = time.time() - start_time
        print(f"❌ Timeout after {processing_time:.2f} seconds")
        return None, processing_time
    except Exception as e:
        processing_time = time.time() - start_time
        print(f"❌ Error: {str(e)}")
        return None, processing_time


def evaluate_single_document(pdf_path, json_path, processing_time):
    """
    Evaluate a single document and return metrics
    
    Returns:
        dict: Evaluation metrics
    """
    try:
        print(f"\nEvaluating: {os.path.basename(pdf_path)}")
        
        # Extract ground truth
        ground_truth = extract_ground_truth_from_pdf(pdf_path)
        gt_text_normalized = normalize_text(ground_truth['text'])
        
        # Load Dolphin output
        dolphin_output = load_dolphin_output(json_path)
        dolphin_text = extract_dolphin_text(dolphin_output)
        dolphin_text_normalized = normalize_text(dolphin_text)
        
        # Calculate metrics
        wer, wer_details = calculate_wer(gt_text_normalized, dolphin_text_normalized)
        cer = calculate_cer(gt_text_normalized, dolphin_text_normalized)
        text_accuracy = calculate_text_accuracy(gt_text_normalized, dolphin_text_normalized)
        structure_score = calculate_structure_score(ground_truth, dolphin_output)
        table_structure_score = calculate_table_structure_score(ground_truth, dolphin_output)
        layout_score = calculate_layout_score(ground_truth, dolphin_output)
        
        # Compile results
        results = {
            'Document_ID': os.path.basename(pdf_path),
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
        
        print(f"✅ Evaluation complete - Text Accuracy: {text_accuracy*100:.2f}%")
        
        return results
        
    except Exception as e:
        print(f"❌ Evaluation error: {str(e)}")
        return {
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
            'Processing_Time_Seconds': round(processing_time, 2) if processing_time else 'N/A',
            'Status': f'Error: {str(e)}'
        }


def process_and_evaluate_batch(input_folder, model_path, output_json_dir, output_csv_path):
    """
    Process all documents in a folder and evaluate them
    """
    # Create output directories
    os.makedirs(output_json_dir, exist_ok=True)
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    os.makedirs('./batch_results', exist_ok=True)
    
    # Find all document files
    extensions = ['*.pdf', '*.png', '*.jpg', '*.jpeg', '*.PNG', '*.JPG', '*.JPEG']
    all_files = []
    
    for ext in extensions:
        all_files.extend(glob.glob(os.path.join(input_folder, ext)))
    
    all_files.sort()
    
    if not all_files:
        print(f"❌ No document files found in {input_folder}")
        return
    
    print(f"\n{'='*80}")
    print(f"BATCH PROCESSING - Found {len(all_files)} document(s)")
    print(f"{'='*80}")
    print(f"Input folder: {input_folder}")
    print(f"Output JSON folder: {output_json_dir}")
    print(f"Output CSV: {output_csv_path}")
    print(f"{'='*80}\n")
    
    all_results = []
    
    for idx, file_path in enumerate(all_files, 1):
        print(f"\n{'#'*80}")
        print(f"Document {idx}/{len(all_files)}: {os.path.basename(file_path)}")
        print(f"{'#'*80}")
        
        try:
            # Process with Dolphin
            json_output_path, processing_time = process_single_document_with_dolphin(
                file_path, model_path, output_json_dir
            )
            
            if json_output_path and os.path.exists(json_output_path):
                # Evaluate
                results = evaluate_single_document(file_path, json_output_path, processing_time)
            else:
                results = {
                    'Document_ID': os.path.basename(file_path),
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
            
            all_results.append(results)
            
            # Save intermediate results after each document
            save_results_to_csv(all_results, output_csv_path)
            
        except Exception as e:
            print(f"❌ Critical error processing {file_path}: {str(e)}")
            all_results.append({
                'Document_ID': os.path.basename(file_path),
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
                'Status': f'Critical Error: {str(e)}'
            })
            continue
    
    # Save final results
    save_results_to_csv(all_results, output_csv_path)
    
    # Print summary
    print_summary(all_results)
    
    return all_results


def save_results_to_csv(results, csv_path):
    """Save results to CSV file"""
    if not results:
        return
    
    fieldnames = [
        'Document_ID', 'WER', 'CER', 'Substitutions', 'Deletions', 'Insertions',
        'Text_Accuracy', 'Structure_Score', 'Table_Structure_Score', 'Layout_Score',
        'Processing_Time_Seconds', 'Status'
    ]
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n📊 Results saved to: {csv_path}")


def print_summary(results):
    """Print summary statistics"""
    print(f"\n{'='*80}")
    print("BATCH PROCESSING SUMMARY")
    print(f"{'='*80}\n")
    
    total = len(results)
    successful = sum(1 for r in results if r['Status'] == 'Success')
    failed = total - successful
    
    print(f"Total documents processed: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    
    if successful > 0:
        # Calculate averages for successful documents
        avg_wer = sum(float(r['WER']) for r in results if r['Status'] == 'Success') / successful
        avg_cer = sum(float(r['CER']) for r in results if r['Status'] == 'Success') / successful
        avg_text_acc = sum(float(r['Text_Accuracy']) for r in results if r['Status'] == 'Success') / successful
        avg_time = sum(float(r['Processing_Time_Seconds']) for r in results if r['Status'] == 'Success') / successful
        
        print(f"\nAverage Metrics (Successful Documents):")
        print(f"  WER: {avg_wer:.4f} ({avg_wer*100:.2f}%)")
        print(f"  CER: {avg_cer:.4f} ({avg_cer*100:.2f}%)")
        print(f"  Text Accuracy: {avg_text_acc:.4f} ({avg_text_acc*100:.2f}%)")
        print(f"  Avg Processing Time: {avg_time:.2f} seconds")
    
    print(f"\n{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(description='Batch process and evaluate documents with Dolphin')
    parser.add_argument('--input_folder', type=str, required=True, 
                       help='Folder containing documents to process')
    parser.add_argument('--model_path', type=str, default='./hf_model',
                       help='Path to Dolphin model')
    parser.add_argument('--output_json_dir', type=str, default='./output_json',
                       help='Directory to save JSON outputs')
    parser.add_argument('--output_csv', type=str, default='./batch_evaluation_results.csv',
                       help='Path to save CSV results')
    
    args = parser.parse_args()
    
    # Validate inputs
    if not os.path.exists(args.input_folder):
        print(f"❌ Input folder not found: {args.input_folder}")
        sys.exit(1)
    
    if not os.path.exists(args.model_path):
        print(f"❌ Model path not found: {args.model_path}")
        sys.exit(1)
    
    # Process and evaluate
    start_time = time.time()
    
    results = process_and_evaluate_batch(
        args.input_folder,
        args.model_path,
        args.output_json_dir,
        args.output_csv
    )
    
    total_time = time.time() - start_time
    
    print(f"\n✅ Batch processing complete!")
    print(f"⏱️  Total time: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
    print(f"📊 Results saved to: {args.output_csv}")
    print(f"📁 JSON outputs in: {args.output_json_dir}")


if __name__ == "__main__":
    main()
