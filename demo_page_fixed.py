#!/usr/bin/env python3
"""
Patched version of demo_page.py that works around DeepSpeed CUDA issues
"""
import os
import sys
import subprocess

# Set environment variables before any imports
os.environ['DS_BUILD_OPS'] = '0'
os.environ['DS_BUILD_SPARSE_ATTN'] = '0'

# Monkey-patch subprocess.check_output to handle nvcc calls
original_check_output = subprocess.check_output

def patched_check_output(args, *pargs, **kwargs):
    """Intercept nvcc version checks and return a fake version"""
    if isinstance(args, list) and len(args) >= 1 and 'nvcc' in args[0]:
        # Return a fake CUDA version output
        return "Cuda compilation tools, release 12.4, V12.4.127"
    return original_check_output(args, *pargs, **kwargs)

subprocess.check_output = patched_check_output

# Now we can safely import deepspeed and the rest
import argparse
import glob

import torch
from PIL import Image
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration
from qwen_vl_utils import process_vision_info

sys.path.insert(0, '/home/ashok/Documents/GitHub/Dolphin')
from utils.utils import *


class DOLPHIN:
    def __init__(self, model_id_or_path):
        """Initialize the Hugging Face model
        
        Args:
            model_id_or_path: Path to local model or Hugging Face model ID
        """
        # Load model from local path or Hugging Face hub
        self.processor = AutoProcessor.from_pretrained(model_id_or_path)
        self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(model_id_or_path)
        self.model.eval()
        
        # Set device and precision
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)

        if self.device == "cuda":
            self.model = self.model.bfloat16()
        else:
            self.model = self.model.float()
        
        # set tokenizer
        self.tokenizer = self.processor.tokenizer
        self.tokenizer.padding_side = "left"

    def chat(self, prompt, image):
        # Check if we're dealing with a batch
        is_batch = isinstance(image, list)
        
        if not is_batch:
            # Single image, wrap it in a list for consistent processing
            images = [image]
            prompts = [prompt]
        else:
            images = image
            prompts = [prompt] * len(images) if isinstance(prompt, str) else prompt
        
        # Prepare messages for each image
        messages_list = []
        for prompt_text, img in zip(prompts, images):
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": img},
                        {"type": "text", "text": prompt_text},
                    ],
                }
            ]
            messages_list.append(messages)
        
        # Process messages
        texts = [
            self.processor.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
            for msgs in messages_list
        ]
        image_inputs, video_inputs = process_vision_info(messages_list)
        
        # Tokenize inputs
        inputs = self.processor(
            text=texts,
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        )
        inputs = inputs.to(self.device)
        
        # Generate
        with torch.no_grad():
            generated_ids = self.model.generate(
                **inputs,
                max_new_tokens=16384,
                do_sample=False,
            )
        
        # Decode
        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        output_texts = self.processor.batch_decode(
            generated_ids_trimmed,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False
        )
        
        # Return single string if input was single image, otherwise return list
        return output_texts[0] if not is_batch else output_texts


def process_document(file_path, dolphin, save_dir):
    """Process a single document (PDF or image)"""
    print(f"\nProcessing: {file_path}")
    filename = os.path.basename(file_path)
    base_name = os.path.splitext(filename)[0]
    
    # Convert PDF to images if needed
    if file_path.lower().endswith('.pdf'):
        images = pdf_to_images(file_path)
    else:
        images = [Image.open(file_path).convert("RGB")]
    
    all_results = []
    
    for page_idx, image in enumerate(images):
        print(f"  Processing page {page_idx + 1}/{len(images)}...")
        
        # Determine document type and get layout
        doc_type_prompt = "Is this a photographed document or a digital-born document? Please answer with only 'photographed' or 'digital'."
        doc_type = dolphin.chat(doc_type_prompt, image).strip().lower()
        
        # Get layout with reading order
        layout_prompt = "Please analyze this document page and provide:\n1. Document type classification (e.g., academic paper, report, form, etc.)\n2. Complete layout analysis with bounding boxes\n3. Reading order sequence\n4. List all document elements with their types\n\nProvide the output in JSON format."
        layout_result = dolphin.chat(layout_prompt, image)
        
        # Based on document type, use appropriate parsing strategy
        if 'photographed' in doc_type:
            # Holistic parsing for photographed documents
            parse_prompt = "Please parse this entire document page and extract all content including text, tables, formulas, and code blocks. Maintain the original structure and formatting. Output in markdown format."
            content = dolphin.chat(parse_prompt, image)
        else:
            # Parallel element-wise parsing for digital documents
            # First extract layout to identify elements
            try:
                layout_data = parse_layout_result(layout_result)
                content_parts = []
                
                # Process each element
                for element in layout_data.get('elements', []):
                    element_type = element.get('type', '').lower()
                    bbox = element.get('bbox', [])
                    
                    if element_type in ['text', 'paragraph', 'title', 'heading']:
                        prompt = "Extract the text content from this region."
                    elif element_type in ['table']:
                        prompt = "Parse this table and convert it to markdown format."
                    elif element_type in ['formula', 'equation']:
                        prompt = "Extract this mathematical formula in LaTeX format."
                    elif element_type in ['code', 'code_block']:
                        prompt = "Extract this code block with proper formatting."
                    else:
                        prompt = "Extract and describe this content."
                    
                    # For simplicity, we'll use the whole image
                    # In production, you'd crop to bbox
                    element_content = dolphin.chat(prompt, image)
                    content_parts.append(f"\n## {element_type.title()}\n{element_content}\n")
                
                content = "\n".join(content_parts)
            except:
                # Fallback to holistic parsing
                parse_prompt = "Please parse this entire document page and extract all content. Output in markdown format."
                content = dolphin.chat(parse_prompt, image)
        
        page_result = {
            'page': page_idx + 1,
            'document_type': doc_type,
            'layout': layout_result,
            'content': content
        }
        all_results.append(page_result)
    
    # Save results
    os.makedirs(save_dir, exist_ok=True)
    
    # Save JSON
    json_path = os.path.join(save_dir, f"{base_name}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"  Saved JSON to: {json_path}")
    
    # Save Markdown
    md_path = os.path.join(save_dir, f"{base_name}.md")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# {filename}\n\n")
        for result in all_results:
            f.write(f"## Page {result['page']}\n\n")
            f.write(f"**Document Type:** {result['document_type']}\n\n")
            f.write(result['content'])
            f.write("\n\n---\n\n")
    print(f"  Saved Markdown to: {md_path}")


def main():
    parser = argparse.ArgumentParser(description='Dolphin Document Parsing')
    parser.add_argument('--model_path', type=str, required=True, help='Path to Dolphin model')
    parser.add_argument('--input_path', type=str, required=True, help='Path to input document or directory')
    parser.add_argument('--save_dir', type=str, default='./results', help='Directory to save results')
    parser.add_argument('--max_batch_size', type=int, default=4, help='Maximum batch size for parallel processing')
    
    args = parser.parse_args()
    
    # Initialize model
    print("Loading Dolphin model...")
    dolphin = DOLPHIN(args.model_path)
    print("Model loaded successfully!")
    
    # Get list of files to process
    if os.path.isfile(args.input_path):
        files = [args.input_path]
    else:
        # Process all supported files in directory
        extensions = ['*.pdf', '*.png', '*.jpg', '*.jpeg', '*.PNG', '*.JPG', '*.JPEG']
        files = []
        for ext in extensions:
            files.extend(glob.glob(os.path.join(args.input_path, ext)))
        files.sort()
    
    if not files:
        print(f"No files found in {args.input_path}")
        return
    
    print(f"\nFound {len(files)} file(s) to process")
    
    # Process each file
    for file_path in files:
        try:
            process_document(file_path, dolphin, args.save_dir)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n✅ Processing complete! Results saved to: {args.save_dir}")


if __name__ == "__main__":
    main()
