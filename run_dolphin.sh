#!/bin/bash
# Wrapper script to run Dolphin with proper environment

cd /home/ashok/Documents/GitHub/Dolphin
source venv/bin/activate

# Set environment variables to avoid DeepSpeed compilation
export DS_BUILD_OPS=0
export DS_BUILD_SPARSE_ATTN=0
export DS_BUILD_FUSED_ADAM=0
export DS_BUILD_CPU_ADAM=0
export DS_BUILD_UTILS=0
export DS_BUILD_AIO=0

# Run the demo
python demo_page.py "$@"
