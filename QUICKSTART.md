# 🚀 Quick Start - Dolphin Batch Processing on New GPU System

## Important: Clone Instructions

```bash
# Use this to avoid Git LFS errors
GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/055024/Dolphin.git && cd Dolphin && ./setup_gpu_system.sh
```

> **Why?** The large model files (~7.5GB) need to be downloaded from Hugging Face, not Git LFS. The setup script handles this automatically. See `CLONE_INSTRUCTIONS.md` for details.

---

## Step-by-Step (5 Minutes)

### 1️⃣ Clone & Setup
```bash
GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/055024/Dolphin.git
cd Dolphin
./setup_gpu_system.sh  # Automated setup (downloads model from Hugging Face, installs deps)
```

### 2️⃣ Add Documents
```bash
cp /path/to/your/pdfs/*.pdf ./test-docs/
```

### 3️⃣ Process
```bash
source venv/bin/activate
python process_new_files.py
```

### 4️⃣ Get Results
```bash
cat test_docs_evaluation_results_FINAL.csv
```

---

## Performance Reference

| Hardware | Speed/Page | 100 Pages |
|----------|------------|-----------|
| **RTX 4090** | ~10 sec | ~17 min |
| **RTX 3090** | ~15 sec | ~25 min |
| **RTX 3060** | ~20 sec | ~33 min |
| **CPU (8-core)** | ~180 sec | ~5 hours |

---

## Key Files

| File | Purpose |
|------|---------|
| `test-docs/` | Input PDFs here |
| `process_new_files.py` | Main processing script |
| `test_docs_evaluation_results_FINAL.csv` | Results CSV |
| `batch_results/recognition_json/` | Structured JSON outputs |
| `monitor_progress.sh` | Check progress |
| `BATCH_PROCESSING_README.md` | Full documentation |

---

## Common Commands

```bash
# Check GPU
nvidia-smi

# Verify CUDA in Python
python -c "import torch; print('CUDA:', torch.cuda.is_available())"

# Monitor progress
./monitor_progress.sh

# View results
column -t -s',' test_docs_evaluation_results_FINAL.csv

# Count processed documents
wc -l test_docs_evaluation_results_FINAL.csv
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| CUDA out of memory | Reduce batch size or use 4-bit quantization |
| Model download fails | Use: `huggingface-cli download 055024/Dolphin-v2 --local-dir ./hf_model` |
| Processing hangs | Check GPU usage with `nvidia-smi`, restart if needed |
| Low accuracy | Check PDF quality, use higher resolution source |

---

## What Gets Evaluated

- ✅ **WER** (Word Error Rate) - % of word errors
- ✅ **CER** (Character Error Rate) - % of character errors
- ✅ **Text_Accuracy** - Overall text accuracy
- ✅ **Structure_Score** - Document structure recognition
- ✅ **Table_Score** - Table detection accuracy
- ✅ **Layout_Score** - Layout understanding
- ✅ **Processing_Time** - Seconds to process

---

## Expected Results

| Document Type | WER | Accuracy |
|---------------|-----|----------|
| Single-page press release | 3-5% | 95-97% |
| Multi-page report | 5-10% | 90-95% |
| Complex layouts | 10-20% | 80-90% |

---

## Remote GPU Server Workflow

```bash
# 1. SSH to server
ssh user@gpu-server

# 2. Setup
git clone https://github.com/055024/Dolphin.git
cd Dolphin
./setup_gpu_system.sh

# 3. Copy documents
scp local-machine:/path/to/pdfs/*.pdf ./test-docs/

# 4. Run in background
nohup python process_new_files.py > batch.log 2>&1 &

# 5. Monitor
tail -f batch.log
# OR
watch -n 60 ./monitor_progress.sh

# 6. Download results when done
scp gpu-server:~/Dolphin/test_docs_evaluation_results_FINAL.csv ./
scp -r gpu-server:~/Dolphin/batch_results/recognition_json/ ./results/
```

---

## Directory After Setup

```
Dolphin/
├── hf_model/                 # 7.5GB model (auto-downloaded)
├── test-docs/                # Your PDFs go here
├── batch_results/
│   └── recognition_json/     # Structured outputs
├── test_docs_evaluation_results_FINAL.csv  # Metrics
├── process_new_files.py      # Run this
├── setup_gpu_system.sh       # Setup script
└── BATCH_PROCESSING_README.md # Full docs
```

---

## Need Help?

📖 **Full Documentation**: `BATCH_PROCESSING_README.md`
🐛 **Issues**: https://github.com/055024/Dolphin/issues
🤗 **Model**: https://huggingface.co/055024/Dolphin-v2

---

**Ready? Run this:**
```bash
./setup_gpu_system.sh && source venv/bin/activate && python process_new_files.py
```
