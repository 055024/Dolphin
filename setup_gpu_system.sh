#!/bin/bash
# Quick Setup Script for Dolphin Batch Processing on GPU Systems
# Usage: ./setup_gpu_system.sh

set -e  # Exit on error

echo "======================================"
echo "Dolphin Batch Processing Setup"
echo "GPU-Optimized Configuration"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Python version: $python_version"

if python3 -c "import sys; sys.exit(0 if (3,8) <= sys.version_info < (3,11) else 1)"; then
    echo -e "${GREEN}✅ Python version compatible${NC}"
else
    echo -e "${RED}❌ Python 3.8-3.10 required. Current: $python_version${NC}"
    exit 1
fi
echo ""

# Check for NVIDIA GPU
echo "🖥️  Checking for NVIDIA GPU..."
if command -v nvidia-smi &> /dev/null; then
    echo -e "${GREEN}✅ NVIDIA GPU detected:${NC}"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader | head -1
    
    # Check CUDA version
    cuda_version=$(nvidia-smi | grep "CUDA Version" | awk '{print $9}')
    echo "   CUDA Version: $cuda_version"
else
    echo -e "${YELLOW}⚠️  No NVIDIA GPU detected. Will use CPU (slower).${NC}"
fi
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment already exists. Skipping.${NC}"
else
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip -q
echo -e "${GREEN}✅ pip upgraded${NC}"
echo ""

# Install PyTorch with CUDA support
echo "🔥 Installing PyTorch with CUDA support..."
if command -v nvidia-smi &> /dev/null; then
    echo "   Detecting CUDA version for optimal PyTorch installation..."
    
    # Get CUDA major version
    cuda_major=$(nvidia-smi | grep "CUDA Version" | awk '{print $9}' | cut -d. -f1)
    
    if [ "$cuda_major" == "12" ]; then
        echo "   Installing PyTorch for CUDA 12.x..."
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
    elif [ "$cuda_major" == "11" ]; then
        echo "   Installing PyTorch for CUDA 11.x..."
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    else
        echo -e "${YELLOW}⚠️  Unknown CUDA version. Installing default PyTorch...${NC}"
        pip install torch torchvision torchaudio
    fi
else
    echo "   Installing CPU-only PyTorch..."
    pip install torch torchvision torchaudio
fi
echo -e "${GREEN}✅ PyTorch installed${NC}"
echo ""

# Install other dependencies
echo "📦 Installing dependencies from requirements.txt..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt -q
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${RED}❌ requirements.txt not found!${NC}"
    exit 1
fi
echo ""

# Verify GPU setup
echo "🔍 Verifying GPU setup..."
python3 << EOF
import torch
print(f"   PyTorch version: {torch.__version__}")
print(f"   CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"   CUDA version: {torch.version.cuda}")
    print(f"   GPU count: {torch.cuda.device_count()}")
    print(f"   GPU name: {torch.cuda.get_device_name(0)}")
    print(f"   GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
else:
    print("   Running in CPU mode")
EOF
echo ""

# Download Dolphin model
echo "📥 Checking Dolphin model..."
if [ -d "hf_model" ] && [ "$(ls -A hf_model)" ]; then
    echo -e "${GREEN}✅ Model already downloaded${NC}"
else
    echo "   Downloading Dolphin-v2 model (7.5GB)..."
    echo "   This will take a few minutes..."
    
    # Install huggingface-hub if not already installed
    pip install -q huggingface-hub
    
    # Download model
    huggingface-cli download 055024/Dolphin-v2 --local-dir ./hf_model
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Model downloaded successfully${NC}"
    else
        echo -e "${RED}❌ Model download failed${NC}"
        echo "   Try manual download: huggingface-cli download 055024/Dolphin-v2 --local-dir ./hf_model"
        exit 1
    fi
fi
echo ""

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p test-docs
mkdir -p batch_results/recognition_json
mkdir -p batch_results/markdown
mkdir -p batch_results/layout_visualization
echo -e "${GREEN}✅ Directories created${NC}"
echo ""

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x monitor_progress.sh 2>/dev/null || true
echo -e "${GREEN}✅ Scripts configured${NC}"
echo ""

# Final summary
echo "======================================"
echo "✅ Setup Complete!"
echo "======================================"
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Copy your PDF files to test-docs folder:"
echo "   cp /path/to/your/*.pdf ./test-docs/"
echo ""
echo "2. Activate the virtual environment (if not already active):"
echo "   source venv/bin/activate"
echo ""
echo "3. Run batch processing:"
echo "   python process_new_files.py"
echo ""
echo "4. Monitor progress:"
echo "   ./monitor_progress.sh"
echo "   # OR"
echo "   tail -f <terminal output>"
echo ""
echo "5. Check results:"
echo "   cat test_docs_evaluation_results_FINAL.csv"
echo ""
echo "======================================"
echo "📚 For detailed documentation, see:"
echo "   BATCH_PROCESSING_README.md"
echo "======================================"
echo ""

# Performance estimate
if command -v nvidia-smi &> /dev/null; then
    echo -e "${GREEN}🚀 GPU Mode Enabled${NC}"
    echo "   Expected speed: ~18 seconds per page"
    echo "   100 pages: ~30 minutes"
else
    echo -e "${YELLOW}🐌 CPU Mode (Slower)${NC}"
    echo "   Expected speed: ~180 seconds per page"
    echo "   100 pages: ~5 hours"
fi
echo ""
