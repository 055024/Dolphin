#!/usr/bin/env python3
"""
Evaluate Dolphin's document parsing performance
Calculates WER, CER, and various accuracy metrics by comparing with ground truth
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple
import re

import pymupdf
import Levenshtein
from datetime import datetime


def extract_ground_truth_from_pdf(pdf_path: str) -> Dict[str, any]:
    """Extract ground truth text and structure from PDF using PyMuPDF"""
    doc = pymupdf.open(pdf_path)
    
    ground_truth = {
        'text': '',
        'pages': [],
        'tables': [],
        'structure_elements': []
    }
    
    for page_num, page in enumerate(doc):
        # Extract text with layout preservation
        text = page.get_text("text")
        blocks = page.get_text("dict")["blocks"]
        
        page_data = {
            'page_num': page_num + 1,
            'text': text,
            'blocks': []
        }
        
        # Extract blocks with coordinates
        for block in blocks:
            if block.get("type") == 0:  # Text block
                block_data = {
                    'bbox': block.get('bbox'),
                    'text': '\n'.join([span['text'] for line in block.get('lines', []) 
                                      for span in line.get('spans', [])]),
                    'type': 'text'
                }
                page_data['blocks'].append(block_data)
                ground_truth['structure_elements'].append(block_data)
        
        ground_truth['pages'].append(page_data)
        ground_truth['text'] += text + '\n'
    
    # Try to detect tables (basic heuristic)
    ground_truth['tables'] = detect_tables_from_text(ground_truth['text'])
    
    doc.close()
    return ground_truth


def detect_tables_from_text(text: str) -> List[Dict]:
    """Basic table detection from text"""
    tables = []
    lines = text.split('\n')
    
    # Look for patterns that suggest tables (multiple columns, consistent spacing)
    table_patterns = []
    for i, line in enumerate(lines):
        # Check if line has multiple tab-separated or space-separated columns
        if '\t' in line or re.search(r'\s{3,}', line):
            table_patterns.append({'line_num': i, 'text': line})
    
    if table_patterns:
        tables.append({
            'detected': True,
            'lines': len(table_patterns),
            'content': table_patterns
        })
    
    return tables


def normalize_text(text: str) -> str:
    """Normalize text for comparison"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove punctuation variations
    text = text.strip()
    # Convert to lowercase
    text = text.lower()
    return text


def calculate_wer(reference: str, hypothesis: str) -> Tuple[float, Dict]:
    """Calculate Word Error Rate"""
    ref_words = reference.split()
    hyp_words = hypothesis.split()
    
    # Calculate Levenshtein distance at word level
    distance = Levenshtein.distance(ref_words, hyp_words)
    
    # Calculate substitutions, deletions, insertions using opcodes
    opcodes = Levenshtein.opcodes(ref_words, hyp_words)
    
    subs = sum(1 for op, _, _, _, _ in opcodes if op == 'replace')
    dels = sum(1 for op, _, _, _, _ in opcodes if op == 'delete')
    ins = sum(1 for op, _, _, _, _ in opcodes if op == 'insert')
    
    wer = distance / len(ref_words) if len(ref_words) > 0 else 0.0
    
    return wer, {
        'substitutions': subs,
        'deletions': dels,
        'insertions': ins,
        'total_words_ref': len(ref_words),
        'total_words_hyp': len(hyp_words)
    }


def calculate_cer(reference: str, hypothesis: str) -> float:
    """Calculate Character Error Rate"""
    distance = Levenshtein.distance(reference, hypothesis)
    cer = distance / len(reference) if len(reference) > 0 else 0.0
    return cer


def calculate_text_accuracy(reference: str, hypothesis: str) -> float:
    """Calculate overall text accuracy (1 - CER)"""
    cer = calculate_cer(reference, hypothesis)
    return max(0.0, 1.0 - cer)


def calculate_structure_score(ground_truth: Dict, dolphin_output: Dict) -> float:
    """Calculate structure preservation score"""
    # Compare number of blocks/elements detected
    gt_elements = len(ground_truth.get('structure_elements', []))
    
    # Count elements in Dolphin output
    dolphin_elements = 0
    if 'pages' in dolphin_output:
        for page in dolphin_output['pages']:
            if 'elements' in page:
                dolphin_elements += len(page['elements'])
            elif 'layout' in page:
                layout = page['layout']
                # Count different element types
                if isinstance(layout, dict):
                    dolphin_elements += len(layout.get('elements', []))
                elif isinstance(layout, list):
                    dolphin_elements += len(layout)
    elif 'elements' in dolphin_output:
        dolphin_elements = len(dolphin_output['elements'])
    
    # Calculate similarity
    if gt_elements == 0 and dolphin_elements == 0:
        return 1.0
    elif gt_elements == 0 or dolphin_elements == 0:
        return 0.0
    else:
        return 1.0 - abs(gt_elements - dolphin_elements) / max(gt_elements, dolphin_elements)


def calculate_table_structure_score(ground_truth: Dict, dolphin_output: Dict) -> float:
    """Calculate table structure preservation score"""
    gt_tables = len(ground_truth.get('tables', []))
    
    # Count tables in Dolphin output
    dolphin_tables = 0
    if 'pages' in dolphin_output:
        for page in dolphin_output['pages']:
            content = page.get('content', '')
            # Count markdown tables
            dolphin_tables += content.count('|')  # Rough heuristic
    
    # If no tables in either, perfect score
    if gt_tables == 0 and dolphin_tables == 0:
        return 1.0
    elif gt_tables == 0:
        return 0.5  # False positives
    elif dolphin_tables == 0:
        return 0.0  # Missed tables
    else:
        return min(1.0, dolphin_tables / (gt_tables * 10))  # Rough scoring


def calculate_layout_score(ground_truth: Dict, dolphin_output: Dict) -> float:
    """Calculate layout analysis score"""
    # Compare page count
    gt_pages = len(ground_truth.get('pages', []))
    dolphin_pages = len(dolphin_output.get('pages', [])) if 'pages' in dolphin_output else 0
    
    if gt_pages != dolphin_pages:
        page_score = 0.5
    else:
        page_score = 1.0
    
    # Combine with structure score
    structure_score = calculate_structure_score(ground_truth, dolphin_output)
    
    return (page_score + structure_score) / 2


def load_dolphin_output(json_path: str) -> Dict:
    """Load Dolphin's output JSON"""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_dolphin_text(dolphin_output: Dict) -> str:
    """Extract all text from Dolphin's output"""
    text_parts = []
    
    if isinstance(dolphin_output, list):
        # Format: list of pages
        for page in dolphin_output:
            if 'content' in page:
                text_parts.append(page['content'])
            elif 'elements' in page:
                # Extract text from elements
                for element in page['elements']:
                    if 'text' in element and element['text']:
                        text_parts.append(element['text'])
    elif isinstance(dolphin_output, dict):
        # Format: dict with pages
        if 'pages' in dolphin_output:
            for page in dolphin_output['pages']:
                if 'content' in page:
                    text_parts.append(page['content'])
                elif 'elements' in page:
                    # Extract text from elements (Dolphin format)
                    for element in page['elements']:
                        if 'text' in element and element['text']:
                            # Skip figure markdown links
                            text = element['text']
                            if not text.startswith('!['):
                                text_parts.append(text)
        elif 'content' in dolphin_output:
            text_parts.append(dolphin_output['content'])
        elif 'elements' in dolphin_output:
            # Single page with elements
            for element in dolphin_output['elements']:
                if 'text' in element and element['text']:
                    if not element['text'].startswith('!['):
                        text_parts.append(element['text'])
    
    return '\n'.join(text_parts)


def evaluate_document(pdf_path: str, dolphin_json_path: str, processing_time: float = None) -> Dict:
    """Comprehensive evaluation of a document"""
    
    print(f"\n{'='*80}")
    print(f"Evaluating: {os.path.basename(pdf_path)}")
    print(f"{'='*80}\n")
    
    # Extract ground truth
    print("Extracting ground truth from PDF...")
    ground_truth = extract_ground_truth_from_pdf(pdf_path)
    gt_text_normalized = normalize_text(ground_truth['text'])
    
    # Load Dolphin output
    print("Loading Dolphin output...")
    dolphin_output = load_dolphin_output(dolphin_json_path)
    dolphin_text = extract_dolphin_text(dolphin_output)
    dolphin_text_normalized = normalize_text(dolphin_text)
    
    # Calculate metrics
    print("Calculating metrics...")
    
    # WER and related metrics
    wer, wer_details = calculate_wer(gt_text_normalized, dolphin_text_normalized)
    
    # CER
    cer = calculate_cer(gt_text_normalized, dolphin_text_normalized)
    
    # Text accuracy
    text_accuracy = calculate_text_accuracy(gt_text_normalized, dolphin_text_normalized)
    
    # Structure scores
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
        'Processing_Time_Seconds': round(processing_time, 2) if processing_time else 'N/A',
        'Ground_Truth_Words': wer_details['total_words_ref'],
        'Dolphin_Output_Words': wer_details['total_words_hyp'],
        'Ground_Truth_Chars': len(gt_text_normalized),
        'Dolphin_Output_Chars': len(dolphin_text_normalized)
    }
    
    return results


def print_results(results: Dict):
    """Pretty print evaluation results"""
    print(f"\n{'='*80}")
    print("EVALUATION RESULTS")
    print(f"{'='*80}\n")
    
    print(f"Document ID:              {results['Document_ID']}")
    print(f"\n--- ERROR METRICS ---")
    print(f"WER (Word Error Rate):    {results['WER']:.4f} ({results['WER']*100:.2f}%)")
    print(f"CER (Character Error Rate): {results['CER']:.4f} ({results['CER']*100:.2f}%)")
    print(f"\n--- ERROR BREAKDOWN ---")
    print(f"Substitutions:            {results['Substitutions']}")
    print(f"Deletions:                {results['Deletions']}")
    print(f"Insertions:               {results['Insertions']}")
    print(f"\n--- ACCURACY METRICS ---")
    print(f"Text Accuracy:            {results['Text_Accuracy']:.4f} ({results['Text_Accuracy']*100:.2f}%)")
    print(f"Structure Score:          {results['Structure_Score']:.4f} ({results['Structure_Score']*100:.2f}%)")
    print(f"Table Structure Score:    {results['Table_Structure_Score']:.4f} ({results['Table_Structure_Score']*100:.2f}%)")
    print(f"Layout Score:             {results['Layout_Score']:.4f} ({results['Layout_Score']*100:.2f}%)")
    print(f"\n--- PROCESSING ---")
    print(f"Processing Time:          {results['Processing_Time_Seconds']} seconds")
    print(f"\n--- STATISTICS ---")
    print(f"Ground Truth Words:       {results['Ground_Truth_Words']}")
    print(f"Dolphin Output Words:     {results['Dolphin_Output_Words']}")
    print(f"Ground Truth Characters:  {results['Ground_Truth_Chars']}")
    print(f"Dolphin Output Characters: {results['Dolphin_Output_Chars']}")
    print(f"\n{'='*80}\n")


def save_results_to_json(results: Dict, output_path: str):
    """Save evaluation results to JSON"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Results saved to: {output_path}")


def save_results_to_csv(results: Dict, output_path: str):
    """Save evaluation results to CSV"""
    import csv
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=results.keys())
        writer.writeheader()
        writer.writerow(results)
    print(f"Results saved to: {output_path}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Evaluate Dolphin document parsing')
    parser.add_argument('--pdf', type=str, required=True, help='Path to input PDF')
    parser.add_argument('--json', type=str, required=True, help='Path to Dolphin output JSON')
    parser.add_argument('--output_dir', type=str, default='./evaluation_results', help='Output directory for results')
    parser.add_argument('--processing_time', type=float, help='Processing time in seconds')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Evaluate document
    results = evaluate_document(args.pdf, args.json, args.processing_time)
    
    # Print results
    print_results(results)
    
    # Save results
    base_name = Path(args.pdf).stem
    json_output = os.path.join(args.output_dir, f"{base_name}_evaluation.json")
    csv_output = os.path.join(args.output_dir, f"{base_name}_evaluation.csv")
    
    save_results_to_json(results, json_output)
    save_results_to_csv(results, csv_output)
    
    print(f"\n✅ Evaluation complete!")


if __name__ == "__main__":
    main()
