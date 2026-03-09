#!/bin/bash
# Fix for Git LFS errors when cloning/pulling the Dolphin repository

echo "=== Dolphin Repository LFS Fix ==="
echo ""
echo "This script fixes the Git LFS error when pulling the repository."
echo "The model files are large and need to be downloaded separately."
echo ""

# Skip LFS during clone/pull
echo "Step 1: Configure Git to skip LFS downloads temporarily"
git config lfs.fetchexclude "hf_model/*"

# If you've already cloned and got errors, you can also do:
# GIT_LFS_SKIP_SMUDGE=1 git pull

echo ""
echo "Step 2: Download the Dolphin-v2 model directly"
echo "The model will be downloaded to hf_model/ directory"
echo ""

# Create model directory
mkdir -p hf_model

# Download model files using Python
python3 << 'PYEOF'
from huggingface_hub import snapshot_download
import os

print("Downloading Dolphin-v2 model from Hugging Face...")
print("This may take several minutes (model is ~7.5GB)")
print("")

model_path = snapshot_download(
    repo_id="Yifei24/Dolphin-v2",
    local_dir="./hf_model",
    local_dir_use_symlinks=False
)

print(f"\n✓ Model downloaded successfully to: {model_path}")
PYEOF

echo ""
echo "=== Setup Complete ==="
echo ""
echo "The model files are now in place. You can proceed with:"
echo "  1. Install dependencies: pip install -r requirements.txt"
echo "  2. Run batch processing: python process_new_files.py"
echo ""
