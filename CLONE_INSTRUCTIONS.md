# How to Clone and Setup Dolphin Repository on New System

## Problem
When cloning/pulling this repository, you may encounter Git LFS errors because the large model files (safetensors) are stored on the upstream repository (bytedance/Dolphin), not on this fork.

## Quick Fix (3 Steps)

### Option 1: Clone with LFS Skip (Recommended)

```bash
# Step 1: Clone the repository without downloading LFS files
GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/055024/Dolphin.git
cd Dolphin

# Step 2: Download the model directly from Hugging Face
python3 -c "
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='Yifei24/Dolphin-v2',
    local_dir='./hf_model',
    local_dir_use_symlinks=False
)
"

# Step 3: Setup and run
pip install -r requirements.txt
python process_new_files.py
```

### Option 2: Use the Fix Script

If you've already cloned and got the error:

```bash
cd Dolphin
chmod +x fix_lfs_pull.sh
./fix_lfs_pull.sh
```

### Option 3: Manual Setup

```bash
# Configure git to skip LFS for model files
git config lfs.fetchexclude "hf_model/*"

# Pull the repository
git pull

# Download model manually
mkdir -p hf_model
cd hf_model
# Download from https://huggingface.co/Yifei24/Dolphin-v2/tree/main
# Or use the Python script above
```

## Why This Error Occurs

- **GitHub Fork Limitation**: Public forks cannot upload new LFS objects
- **Model Size**: The Dolphin-v2 model files are ~7.5GB
- **Solution**: Download model directly from Hugging Face (original source)

## Verification

After setup, verify the model files exist:

```bash
ls -lh hf_model/*.safetensors
# Should show:
# model-00001-of-00002.safetensors (~5 GB)
# model-00002-of-00002.safetensors (~2.5 GB)
```

## What You Get

All the work from the previous system is included:

✅ **Documentation**: 
- `GPU_BATCH_PROCESSING.md` - Main setup guide
- `QUICKSTART.md` - 5-minute quick start
- `BATCH_PROCESSING_README.md` - Complete reference
- `SETUP_CHECKLIST.md` - Verification steps

✅ **Scripts**:
- `process_new_files.py` - Incremental batch processing
- `evaluate_dolphin.py` - Comprehensive evaluation metrics
- `setup_gpu_system.sh` - Automated GPU setup

✅ **Results**:
- `test_docs_evaluation_results_FINAL.csv` - Previous results
- `batch_results/` - All previous outputs

## Next Steps

After successful clone:

1. **GPU System**: Follow `GPU_BATCH_PROCESSING.md` or run `./setup_gpu_system.sh`
2. **Quick Start**: See `QUICKSTART.md` for immediate usage
3. **Add Documents**: Copy PDFs to `test-docs/` directory
4. **Process**: Run `python process_new_files.py`

## Performance on GPU System

Expected improvements over CPU system:

| Metric | CPU (T1000 4GB) | GPU (8GB+) | Improvement |
|--------|-----------------|------------|-------------|
| Per Page | ~180 seconds | ~18 seconds | **10x faster** |
| 10 Pages | ~30 minutes | ~3 minutes | **10x faster** |
| 100 Pages | ~5 hours | ~30 minutes | **10x faster** |

## Troubleshooting

### Error: "CUDA out of memory"
- Solution: See `BATCH_PROCESSING_README.md` GPU troubleshooting section

### Error: "Model files not found"
- Solution: Re-run the model download command from Option 1, Step 2

### Error: "huggingface_hub not found"
- Solution: `pip install huggingface_hub`

## Support

For detailed instructions, see:
- GPU Setup: `GPU_BATCH_PROCESSING.md`
- Complete Guide: `BATCH_PROCESSING_README.md`
- Documentation Index: `DOCUMENTATION_INDEX.md`
