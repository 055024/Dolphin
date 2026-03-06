# ✅ GPU System Setup Checklist

**Use this checklist when setting up Dolphin on a new GPU system**

---

## Pre-Setup Verification

- [ ] System has NVIDIA GPU (check with `nvidia-smi`)
- [ ] CUDA 11.8+ or 12.x installed
- [ ] Python 3.8-3.10 installed
- [ ] At least 16GB RAM available
- [ ] At least 10GB disk space free
- [ ] Git installed

---

## Setup Steps

### Phase 1: Repository Setup
- [ ] Clone repository: `git clone https://github.com/055024/Dolphin.git`
- [ ] Navigate to directory: `cd Dolphin`
- [ ] Make setup script executable: `chmod +x setup_gpu_system.sh`

### Phase 2: Automated Setup
- [ ] Run setup script: `./setup_gpu_system.sh`
- [ ] Verify virtual environment created: `ls venv/`
- [ ] Verify model downloaded (7.5GB): `ls hf_model/`
- [ ] Check GPU detection in output

### Phase 3: Verify Installation
- [ ] Activate environment: `source venv/bin/activate`
- [ ] Test GPU: `python -c "import torch; print(torch.cuda.is_available())"`
  - Expected: `True` for GPU systems
- [ ] Verify model exists: `ls -lh hf_model/`
  - Should show ~7.5GB of files

---

## Document Processing Setup

### Add Documents
- [ ] Copy PDF files to test-docs: `cp /path/to/pdfs/*.pdf ./test-docs/`
- [ ] Verify files copied: `ls -lh test-docs/`
- [ ] Count documents: `ls test-docs/*.pdf | wc -l`

### Pre-Processing Check
- [ ] Activate environment (if not active): `source venv/bin/activate`
- [ ] Check existing results: `cat test_docs_evaluation_results_FINAL.csv`
  - Note: Shows already processed files
- [ ] Make monitor script executable: `chmod +x monitor_progress.sh`

---

## Processing

### Start Processing
- [ ] Run processing: `python process_new_files.py`
- [ ] Confirm GPU is being used (check nvidia-smi in another terminal)
- [ ] Note start time for estimation

### During Processing (Optional)
- [ ] Monitor with script: `./monitor_progress.sh`
- [ ] Check CSV updates: `tail test_docs_evaluation_results_FINAL.csv`
- [ ] Monitor GPU usage: `watch -n 5 nvidia-smi`
- [ ] Check disk space: `df -h .`

---

## Post-Processing Verification

### Check Outputs
- [ ] Verify CSV updated: `wc -l test_docs_evaluation_results_FINAL.csv`
- [ ] Count JSON files: `ls batch_results/recognition_json/*.json | wc -l`
- [ ] Check file sizes reasonable: `du -sh batch_results/`
- [ ] Verify all documents processed: Compare count with input

### Review Results
- [ ] View formatted results: `column -t -s',' test_docs_evaluation_results_FINAL.csv`
- [ ] Check for errors in Status column
- [ ] Verify WER/CER values reasonable (< 0.30 for good quality PDFs)
- [ ] Note processing times

### Sample Check
- [ ] Open a random JSON output: `cat batch_results/recognition_json/[filename].json`
- [ ] Verify structure looks correct
- [ ] Check text extraction quality
- [ ] Verify bounding boxes present

---

## Performance Verification

### Expected Benchmarks
- [ ] Check processing time per page:
  - GPU (24GB): ~10 seconds/page ✓
  - GPU (8-12GB): ~15-20 seconds/page ✓
  - CPU: ~180 seconds/page (fallback)

### Accuracy Benchmarks
- [ ] Average WER should be < 0.10 (10%) for good quality PDFs
- [ ] Average CER should be < 0.05 (5%) for good quality PDFs
- [ ] Average Text Accuracy should be > 0.90 (90%) for good quality PDFs

---

## Backup & Documentation

### Save Results
- [ ] Backup CSV: `cp test_docs_evaluation_results_FINAL.csv results_backup_$(date +%Y%m%d).csv`
- [ ] Backup JSON outputs: `tar -czf results_$(date +%Y%m%d).tar.gz batch_results/recognition_json/`
- [ ] Save processing log (if using nohup/background)

### Document Run
- [ ] Note GPU model used
- [ ] Note total documents processed
- [ ] Note total processing time
- [ ] Note average accuracy achieved
- [ ] Save any error messages or issues encountered

---

## Troubleshooting Checklist

If issues occur, check:

### GPU Issues
- [ ] Run `nvidia-smi` - should show GPU
- [ ] Check CUDA available: `python -c "import torch; print(torch.cuda.is_available())"`
- [ ] Check CUDA version matches PyTorch: `python -c "import torch; print(torch.version.cuda)"`
- [ ] Verify VRAM not full: `nvidia-smi` memory usage
- [ ] Try reducing batch size if OOM errors

### Model Issues
- [ ] Verify model directory exists: `ls hf_model/`
- [ ] Check model size: `du -sh hf_model/` (should be ~7.5GB)
- [ ] Re-download if needed: `rm -rf hf_model && huggingface-cli download 055024/Dolphin-v2 --local-dir ./hf_model`

### Processing Issues
- [ ] Check document permissions: `ls -l test-docs/`
- [ ] Verify PDFs not corrupted: Try opening in PDF reader
- [ ] Check disk space: `df -h .`
- [ ] Review error messages in terminal output
- [ ] Check Python environment activated: `which python` should show venv path

### Performance Issues
- [ ] Verify GPU being used (not CPU): Check nvidia-smi during processing
- [ ] Check other processes not using GPU: `nvidia-smi`
- [ ] Verify no thermal throttling: Check GPU temperature
- [ ] Close other applications to free resources

---

## Remote Server Specific Checks

If using remote GPU server:

### Before Processing
- [ ] SSH connection stable
- [ ] Using screen/tmux for persistence: `screen -S dolphin`
- [ ] Can detach and reattach: `Ctrl+A, D` then `screen -r dolphin`

### During Processing
- [ ] Processing running in background: `nohup python process_new_files.py > batch.log 2>&1 &`
- [ ] Can monitor remotely: `tail -f batch.log`
- [ ] Can check via cron/scheduled script

### After Processing
- [ ] Download results: `scp server:~/Dolphin/test_docs_evaluation_results_FINAL.csv ./`
- [ ] Download JSON outputs: `scp -r server:~/Dolphin/batch_results/recognition_json/ ./`
- [ ] Clean up large files if needed

---

## Success Criteria

Processing is successful when:

- ✅ All input PDFs have corresponding entries in CSV
- ✅ All entries show Status = "Success"
- ✅ Average Text_Accuracy > 0.85 (85%)
- ✅ JSON files created for all documents
- ✅ Processing time reasonable for hardware
- ✅ No critical errors in logs
- ✅ Results are reproducible

---

## Quick Reference

```bash
# Setup
./setup_gpu_system.sh

# Activate
source venv/bin/activate

# Process
python process_new_files.py

# Monitor
./monitor_progress.sh

# Results
cat test_docs_evaluation_results_FINAL.csv
```

---

## Need Help?

- 📖 Full docs: `BATCH_PROCESSING_README.md`
- 🚀 Quick start: `QUICKSTART.md`
- 🐛 Issues: https://github.com/055024/Dolphin/issues

---

**Date Completed**: ________________

**GPU Used**: ________________

**Documents Processed**: ________________

**Average Accuracy**: ________________

**Notes**: 

_____________________________________________________________

_____________________________________________________________

_____________________________________________________________
