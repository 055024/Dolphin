# 🐬 Dolphin Batch Processing for GPU Systems

**Complete setup guide for running batch document parsing and evaluation on high-performance GPU systems**

---

## 🚀 Ultra Quick Start (5 Minutes)

```bash
# 1. Clone and setup
git clone https://github.com/055024/Dolphin.git
cd Dolphin
./setup_gpu_system.sh

# 2. Add your PDFs
cp /path/to/your/pdfs/*.pdf ./test-docs/

# 3. Process
source venv/bin/activate
python process_new_files.py

# 4. Get results
cat test_docs_evaluation_results_FINAL.csv
```

**Done!** Your documents are parsed, evaluated, and results are in CSV format. 🎉

---

## 📚 Complete Documentation Suite

| Document | When to Use | Time |
|----------|-------------|------|
| **[QUICKSTART.md](QUICKSTART.md)** | First-time setup on GPU system | 5 min |
| **[BATCH_PROCESSING_README.md](BATCH_PROCESSING_README.md)** | Detailed reference and troubleshooting | 30 min |
| **[SETUP_CHECKLIST.md](SETUP_CHECKLIST.md)** | Step-by-step verification | 15 min |
| **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** | Navigate all documentation | 10 min |

---

## 💡 What This Does

### Input
Place PDF documents in `test-docs/` folder

### Processing
- 🔍 **Parses** documents using Dolphin vision-language model
- 📊 **Extracts** text, tables, formulas, and structure
- 🎯 **Evaluates** accuracy against ground truth
- 📈 **Calculates** metrics (WER, CER, accuracy scores)

### Output
1. **CSV file** with evaluation metrics for each document
2. **JSON files** with structured document data
3. **Markdown files** with readable format

---

## ⚡ Performance

| Hardware | Speed | 100 Pages |
|----------|-------|-----------|
| **RTX 4090/3090 (24GB)** | ~10-15 sec/page | 17-25 min |
| **RTX 3060/3080 (8-12GB)** | ~18-20 sec/page | 30-33 min |
| **CPU (8-core)** | ~180 sec/page | ~5 hours |

**GPU is 10-20x faster than CPU!**

---

## 📊 What You'll Get

### Evaluation Metrics CSV
```csv
Document_ID,WER,CER,Text_Accuracy,Processing_Time_Seconds,Status
document.pdf,0.036,0.0184,0.9816,18.5,Success
```

**Metrics Explained**:
- **WER** (Word Error Rate): 3.6% = 96.4% words correct ✅
- **CER** (Character Error Rate): 1.84% character errors
- **Text_Accuracy**: 98.16% overall accuracy 🎯
- **Processing_Time**: 18.5 seconds (GPU) vs 180 seconds (CPU)

### Structured JSON Output
```json
{
  "label": "para",
  "text": "Your document text here...",
  "bbox": [x1, y1, x2, y2],
  "reading_order": 1
}
```

---

## 🎯 Key Features

- ✅ **Automatic GPU Detection**: Uses GPU if available, falls back to CPU
- ✅ **Incremental Processing**: Only processes new files, skips completed
- ✅ **Progress Tracking**: Monitor progress in real-time
- ✅ **Comprehensive Metrics**: WER, CER, structure scores, and more
- ✅ **Safe Interruption**: Can stop and resume without losing work
- ✅ **Background Processing**: Run with `nohup` for long batches

---

## 🛠️ Requirements

### Minimum
- Python 3.8-3.10
- 8GB RAM
- 10GB disk space

### Recommended
- NVIDIA GPU with 8GB+ VRAM
- CUDA 11.8 or 12.x
- 16GB+ RAM

---

## 📦 What Gets Installed

- PyTorch with CUDA support
- Transformers (Hugging Face)
- Dolphin-v2 model (7.5GB)
- All Python dependencies
- Evaluation tools

**Everything is automated by `setup_gpu_system.sh`**

---

## 🔍 Use Cases

### ✅ Perfect For
- Batch processing press releases
- Converting documents to structured data
- Quality assessment of document parsing
- Benchmarking document understanding
- Extracting text from PDFs at scale

### ⚠️ Consider Alternatives For
- Real-time processing (use single document API)
- Simple OCR tasks (may be overkill)
- Non-text documents (images only)

---

## 📖 Documentation Structure

```
Start Here → QUICKSTART.md (5 min)
    ↓
Need Details? → BATCH_PROCESSING_README.md (30 min)
    ↓
Want Checklist? → SETUP_CHECKLIST.md (15 min)
    ↓
See Everything → DOCUMENTATION_INDEX.md (10 min)
```

---

## 🎓 Learning Path

1. **Read**: [QUICKSTART.md](QUICKSTART.md) ← **Start here!**
2. **Run**: `./setup_gpu_system.sh`
3. **Test**: Process 1-2 documents
4. **Deploy**: Process full batch
5. **Optimize**: Read [BATCH_PROCESSING_README.md](BATCH_PROCESSING_README.md)

---

## 🔧 Key Scripts

| Script | Purpose |
|--------|---------|
| `setup_gpu_system.sh` | One-time setup (installs everything) |
| `process_new_files.py` | Main processing script (run this) |
| `monitor_progress.sh` | Check processing status |
| `evaluate_testdocs.py` | Re-evaluate existing outputs |

---

## 💻 Remote GPU Server Workflow

```bash
# 1. SSH to your GPU server
ssh user@gpu-server

# 2. Setup (one-time)
git clone https://github.com/055024/Dolphin.git
cd Dolphin
./setup_gpu_system.sh

# 3. Transfer documents
scp local-machine:/path/to/pdfs/*.pdf ./test-docs/

# 4. Process in background
nohup python process_new_files.py > batch.log 2>&1 &

# 5. Monitor
tail -f batch.log
# OR
watch -n 60 ./monitor_progress.sh

# 6. Download results
scp gpu-server:~/Dolphin/test_docs_evaluation_results_FINAL.csv ./
scp -r gpu-server:~/Dolphin/batch_results/recognition_json/ ./
```

---

## ❓ Common Questions

**Q: Do I need a GPU?**  
A: No, but GPU is 10-20x faster. CPU works but slower.

**Q: How long will it take?**  
A: GPU: ~18 sec/page. CPU: ~180 sec/page.

**Q: Can I stop and resume?**  
A: Yes! Script tracks progress and skips completed files.

**Q: What PDF types work?**  
A: Best with digital-born PDFs. Scanned docs work but lower accuracy.

**Q: How much disk space?**  
A: ~10GB for model + ~5MB per page of output.

**Q: Can I process in parallel?**  
A: Yes, split documents and run multiple instances.

---

## 🐛 Troubleshooting

| Issue | Quick Fix |
|-------|-----------|
| CUDA out of memory | Reduce batch size in script |
| Model download fails | `huggingface-cli download 055024/Dolphin-v2 --local-dir ./hf_model` |
| GPU not detected | Check `nvidia-smi` and CUDA installation |
| Low accuracy | Check PDF quality and resolution |

**Full troubleshooting**: See [BATCH_PROCESSING_README.md](BATCH_PROCESSING_README.md#troubleshooting)

---

## 📈 Expected Results

| Document Type | Expected Accuracy | Typical WER |
|---------------|-------------------|-------------|
| Single-page press release | 95-97% | 3-5% |
| Multi-page report | 90-95% | 5-10% |
| Complex layouts | 80-90% | 10-20% |

---

## 🎯 Success Checklist

After setup, verify:
- [ ] GPU detected: `nvidia-smi`
- [ ] CUDA available: `python -c "import torch; print(torch.cuda.is_available())"`
- [ ] Model downloaded: `ls hf_model/` (~7.5GB)
- [ ] Test document processes successfully
- [ ] Results appear in CSV with good accuracy

---

## 🚦 Next Steps

1. **New User?** → Read [QUICKSTART.md](QUICKSTART.md)
2. **Ready to Setup?** → Run `./setup_gpu_system.sh`
3. **Need Help?** → Check [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)
4. **Want Details?** → Read [BATCH_PROCESSING_README.md](BATCH_PROCESSING_README.md)

---

## 🔗 Links

- **Model**: https://huggingface.co/055024/Dolphin-v2
- **Repository**: https://github.com/055024/Dolphin
- **Issues**: https://github.com/055024/Dolphin/issues

---

## 📄 License

See LICENSE file in repository.

---

## 🎉 Quick Start Command

**Ready to begin?**

```bash
./setup_gpu_system.sh && source venv/bin/activate && python process_new_files.py
```

**That's it! Your GPU-powered document processing pipeline is ready to go! 🚀**

---

*For detailed documentation, start with [QUICKSTART.md](QUICKSTART.md)*
