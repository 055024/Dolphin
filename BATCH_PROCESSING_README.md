# Dolphin Batch Processing & Evaluation Guide

**Quick Setup Guide for High-Performance GPU Systems**

This guide walks you through setting up and running batch document parsing and evaluation using the Dolphin document parser on a new system with GPU acceleration.

---

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Quick Start](#quick-start)
3. [Installation](#installation)
4. [Batch Processing](#batch-processing)
5. [Evaluation Metrics](#evaluation-metrics)
6. [Performance Optimization](#performance-optimization)
7. [Troubleshooting](#troubleshooting)

---

## 🖥️ System Requirements

### Minimum Requirements
- **OS**: Linux (Ubuntu 20.04+), Windows 10/11, or macOS
- **Python**: 3.8 - 3.10
- **RAM**: 16GB+ recommended
- **Storage**: 10GB free space for model + outputs

### GPU Requirements (Recommended)
- **GPU**: NVIDIA GPU with 8GB+ VRAM
  - Optimal: RTX 3090/4090, A100, V100 (24GB+ VRAM)
  - Minimum: RTX 3060 (12GB), T4, or similar
- **CUDA**: 11.8 or 12.x
- **cuDNN**: Compatible with your CUDA version

### Performance Comparison
| Hardware | Speed per Page | 100 Pages | 
|----------|----------------|-----------|
| **CPU** (8-core) | ~180 seconds | ~5 hours |
| **GPU** (8GB) | ~18 seconds | ~30 min |
| **GPU** (24GB) | ~10 seconds | ~17 min |

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/055024/Dolphin.git
cd Dolphin

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download Dolphin model (7.5GB)
huggingface-cli download 055024/Dolphin-v2 --local-dir ./hf_model

# 5. Process documents
python process_new_files.py

# Done! Results in test_docs_evaluation_results_FINAL.csv
```

---

## 📦 Installation

### Step 1: Set Up Python Environment

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Upgrade pip
pip install --upgrade pip
```

### Step 2: Install Dependencies

#### For GPU Systems (Recommended)
```bash
# Install PyTorch with CUDA support first
# For CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install other dependencies
pip install -r requirements.txt
```

#### For CPU-Only Systems
```bash
# Install all dependencies
pip install -r requirements.txt
```

### Step 3: Verify GPU Setup (Optional but Recommended)

```bash
python -c "import torch; print('CUDA Available:', torch.cuda.is_available()); print('GPU Count:', torch.cuda.device_count()); print('GPU Name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"
```

Expected output (GPU system):
```
CUDA Available: True
GPU Count: 1
GPU Name: NVIDIA GeForce RTX 4090
```

### Step 4: Download Dolphin Model

```bash
# Method 1: Using huggingface-cli (Recommended)
pip install huggingface-hub
huggingface-cli download 055024/Dolphin-v2 --local-dir ./hf_model

# Method 2: Using Python script
python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='055024/Dolphin-v2', local_dir='./hf_model')"
```

Model size: ~7.5GB (3B parameters)

---

## 📂 Batch Processing

### Directory Structure

```
Dolphin/
├── test-docs/                    # Input: Place your PDF files here
├── batch_results/
│   ├── recognition_json/         # Output: Structured JSON results
│   ├── markdown/                 # Output: Markdown files
│   └── layout_visualization/     # Output: Layout visualizations
├── test_docs_evaluation_results_FINAL.csv  # Output: Evaluation metrics
├── hf_model/                     # Dolphin model files
├── process_new_files.py          # Main batch processing script
├── evaluate_testdocs.py          # Evaluation script
└── monitor_progress.sh           # Progress monitoring script
```

### Processing New Documents

#### 1. Add Your Documents

```bash
# Copy your PDF files to test-docs folder
cp /path/to/your/documents/*.pdf ./test-docs/
```

#### 2. Run Batch Processing

```bash
# Activate virtual environment
source venv/bin/activate

# Process all NEW files (skips already processed)
python process_new_files.py
```

The script will:
- ✅ Detect new files automatically
- ✅ Process each document with Dolphin
- ✅ Calculate evaluation metrics (WER, CER, accuracy)
- ✅ Append results to CSV after each document
- ✅ Save JSON outputs for each document

#### 3. Monitor Progress

**Option 1: Use monitoring script**
```bash
./monitor_progress.sh

# Or watch continuously (updates every 60 seconds)
watch -n 60 ./monitor_progress.sh
```

**Option 2: Check CSV file**
```bash
# Count documents processed
wc -l test_docs_evaluation_results_FINAL.csv

# View latest results
tail -5 test_docs_evaluation_results_FINAL.csv

# View formatted table
column -t -s',' test_docs_evaluation_results_FINAL.csv
```

**Option 3: Check JSON outputs**
```bash
ls -lh batch_results/recognition_json/
```

---

## 📊 Evaluation Metrics

The system automatically calculates comprehensive evaluation metrics by comparing Dolphin's output with ground truth (extracted from the PDF).

### Metrics Calculated

| Metric | Description | Range | Better Value |
|--------|-------------|-------|--------------|
| **WER** | Word Error Rate | 0-1 | Lower ➘ |
| **CER** | Character Error Rate | 0-1 | Lower ➘ |
| **Text_Accuracy** | 1 - CER | 0-1 | Higher ➚ |
| **Substitutions** | Words replaced | Count | Lower ➘ |
| **Deletions** | Words missed | Count | Lower ➘ |
| **Insertions** | Extra words added | Count | Lower ➘ |
| **Structure_Score** | Document structure recognition | 0-1 | Higher ➚ |
| **Table_Structure_Score** | Table detection accuracy | 0-1 | Higher ➚ |
| **Layout_Score** | Layout understanding | 0-1 | Higher ➚ |
| **Processing_Time_Seconds** | Time to process document | Seconds | Lower ➘ |

### Understanding Results

**Example Results:**
```csv
Document_ID,WER,CER,Substitutions,Deletions,Insertions,Text_Accuracy,Processing_Time_Seconds
1PG_Press-release.pdf,0.036,0.0184,9,0,1,0.9816,162.33
```

**Interpretation:**
- **WER 0.036** = 3.6% word error rate (96.4% of words correct)
- **CER 0.0184** = 1.84% character error rate
- **Text_Accuracy 0.9816** = 98.16% accuracy
- **9 substitutions, 0 deletions, 1 insertion** = 10 total word errors
- **162 seconds** = 2.7 minutes to process (CPU) or ~16 seconds (GPU)

### Expected Performance Benchmarks

| Document Type | Expected WER | Expected Accuracy | Notes |
|---------------|--------------|-------------------|-------|
| Single-page press release | 3-5% | 95-97% | Best performance |
| Multi-page report | 5-10% | 90-95% | Good performance |
| Complex layouts with tables | 10-20% | 80-90% | May need review |
| Scanned documents | 15-30% | 70-85% | OCR quality dependent |

---

## ⚡ Performance Optimization

### GPU Configuration (Automatic)

The system automatically detects and uses GPU if available. The original `demo_page.py` has been modified to handle both GPU and CPU inference.

**GPU Mode (Automatic)**:
- Uses `bfloat16` precision for faster inference
- ~10-20x faster than CPU
- Recommended for batch processing

**CPU Mode (Fallback)**:
- Uses `float32` precision
- Slower but works without GPU
- Suitable for small batches

### Force GPU Usage

If you want to ensure GPU is being used:

```bash
# Check GPU availability
nvidia-smi

# Run with explicit GPU check
python -c "import torch; assert torch.cuda.is_available(), 'GPU not available!'"

# Then run processing
python process_new_files.py
```

### Optimize for Large Batches

**For documents with 50+ pages:**

1. **Increase batch size** (if you have sufficient VRAM):
```python
# Edit process_new_files.py, line ~40
'--max_batch_size', '8'  # Change from 4 to 8 for GPUs with 24GB+ VRAM
```

2. **Process in parallel** (multiple documents simultaneously):
```bash
# Split documents into folders
mkdir test-docs-batch1 test-docs-batch2

# Run multiple instances (in separate terminals)
python process_new_files.py --input_folder test-docs-batch1 &
python process_new_files.py --input_folder test-docs-batch2 &
```

3. **Use quantization** (for memory-constrained GPUs):
```python
# Edit demo_page.py, add after model loading:
from transformers import BitsAndBytesConfig

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.bfloat16
)

# Then load model with:
self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
    model_id_or_path,
    quantization_config=quantization_config,
    device_map="auto"
)
```

### Disk Space Management

For large batches, manage disk space:

```bash
# Check space usage
du -sh batch_results/

# Remove old visualization files (keep JSON and CSV)
rm -rf batch_results/layout_visualization/

# Compress markdown files
tar -czf markdown_backup.tar.gz batch_results/markdown/
rm -rf batch_results/markdown/
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. CUDA Out of Memory

**Error**: `RuntimeError: CUDA out of memory`

**Solutions**:
```bash
# Option A: Reduce batch size
# Edit process_new_files.py, change --max_batch_size to 2 or 1

# Option B: Use CPU instead
# Edit demo_page.py, force CPU:
self.device = "cpu"  # Line ~50

# Option C: Use 4-bit quantization (see optimization section)
```

#### 2. DeepSpeed CUDA Compilation Errors

**Error**: `CUDA_HOME does not exist, unable to compile CUDA op(s)`

**Solution**: Already handled in `demo_page.py` (lines 6-10):
```python
os.environ['DS_BUILD_OPS'] = '0'
os.environ['CUDA_HOME'] = '/usr/local/cuda'
```

If still failing, check your CUDA installation:
```bash
which nvcc
export CUDA_HOME=/usr/local/cuda  # Adjust path as needed
```

#### 3. Model Download Fails

**Error**: `Connection timeout` or `Failed to download`

**Solutions**:
```bash
# Option A: Use git-lfs
git lfs install
git clone https://huggingface.co/055024/Dolphin-v2 ./hf_model

# Option B: Download manually
# Visit: https://huggingface.co/055024/Dolphin-v2
# Download all files to ./hf_model/

# Option C: Use mirror
export HF_ENDPOINT=https://hf-mirror.com
huggingface-cli download 055024/Dolphin-v2 --local-dir ./hf_model
```

#### 4. Processing Stalls/Hangs

**Symptoms**: Script appears stuck on one document

**Solutions**:
```bash
# Check if still running (look for CPU/GPU usage)
nvidia-smi  # GPU usage
top         # CPU usage

# If truly stuck, kill and restart (safe - progress is saved)
pkill -f process_new_files.py

# Resume (will skip completed files)
python process_new_files.py
```

#### 5. Low Accuracy Results

**Issue**: WER > 20%, Accuracy < 80%

**Possible causes and solutions**:
1. **Poor PDF quality**: Use higher quality source documents
2. **Complex layouts**: May require manual review
3. **Scanned documents**: Consider pre-processing with OCR enhancement
4. **Wrong document type**: Check if document is supported (text-based PDFs work best)

---

## 📈 Processing Time Estimates

### Single Document

| Document Size | CPU (8-core) | GPU (8GB) | GPU (24GB) |
|---------------|--------------|-----------|------------|
| 1 page | ~3 min | ~18 sec | ~10 sec |
| 5 pages | ~15 min | ~90 sec | ~50 sec |
| 10 pages | ~30 min | ~3 min | ~100 sec |
| 50 pages | ~2.5 hours | ~15 min | ~8 min |
| 100 pages | ~5 hours | ~30 min | ~17 min |

### Batch Processing

**Current test-docs batch** (169 pages):
- CPU: ~8-9 hours
- GPU (8GB): ~50 minutes
- GPU (24GB): ~28 minutes

---

## 🎯 Workflow Examples

### Example 1: Process 10 New PDFs

```bash
# 1. Copy PDFs to test-docs
cp ~/Documents/*.pdf ./test-docs/

# 2. Activate environment
source venv/bin/activate

# 3. Run processing
python process_new_files.py

# 4. Check results
cat test_docs_evaluation_results_FINAL.csv
```

### Example 2: Process Large Batch on GPU Server

```bash
# 1. SSH to GPU server
ssh user@gpu-server

# 2. Clone repository
git clone https://github.com/055024/Dolphin.git
cd Dolphin

# 3. Setup environment
python3 -m venv venv
source venv/bin/activate
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt

# 4. Download model
huggingface-cli download 055024/Dolphin-v2 --local-dir ./hf_model

# 5. Copy documents
scp -r local-machine:~/documents/*.pdf ./test-docs/

# 6. Verify GPU
python -c "import torch; print('GPU:', torch.cuda.get_device_name(0))"

# 7. Run in background with nohup
nohup python process_new_files.py > batch_processing.log 2>&1 &

# 8. Monitor progress
tail -f batch_processing.log
# OR
watch -n 60 ./monitor_progress.sh

# 9. Download results when complete
scp gpu-server:~/Dolphin/test_docs_evaluation_results_FINAL.csv ./
```

### Example 3: Re-evaluate Existing Outputs

```bash
# If you already have JSON outputs and want to recalculate metrics
python evaluate_testdocs.py

# This will read from batch_results/recognition_json/
# and regenerate test_docs_evaluation_results_FINAL.csv
```

---

## 📝 Output Files Reference

### JSON Output Format

Each document produces a JSON file with structured data:

```json
[
  {
    "label": "para",
    "bbox": [219, 238, 1405, 458],
    "text": "Sample paragraph text...",
    "reading_order": 1,
    "tags": []
  },
  {
    "label": "table",
    "bbox": [220, 500, 1400, 800],
    "text": "Table content in markdown...",
    "reading_order": 2,
    "tags": []
  }
]
```

### CSV Output Format

```csv
Document_ID,WER,CER,Substitutions,Deletions,Insertions,Text_Accuracy,Structure_Score,Table_Structure_Score,Layout_Score,Processing_Time_Seconds,Status
document1.pdf,0.036,0.0184,9,0,1,0.9816,0.6667,1.0,0.8333,162.33,Success
```

---

## 🔐 Best Practices

1. **Always use virtual environment** to avoid dependency conflicts
2. **Verify GPU availability** before large batches
3. **Monitor disk space** for large document sets
4. **Save CSV backups** before re-running evaluations
5. **Use screen/tmux** for long-running processes on servers
6. **Start with small test batch** to verify setup

---

## 📞 Support

**Issues**: https://github.com/055024/Dolphin/issues
**Model**: https://huggingface.co/055024/Dolphin-v2

---

## 📄 License

See LICENSE file in repository.

---

## 🎉 Quick Reference Card

```bash
# Setup (one-time)
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
huggingface-cli download 055024/Dolphin-v2 --local-dir ./hf_model

# Process documents
cp /path/to/pdfs/*.pdf ./test-docs/
python process_new_files.py

# Monitor
./monitor_progress.sh
tail test_docs_evaluation_results_FINAL.csv

# Results location
batch_results/recognition_json/          # Structured outputs
test_docs_evaluation_results_FINAL.csv   # Evaluation metrics
```

**Happy document parsing! 🚀**
