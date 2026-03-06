#!/usr/bin/env python3
"""
Patched version of demo_page.py that works around DeepSpeed CUDA issues
"""
import os
import sys

# Set environment variables before any imports
os.environ['DS_BUILD_OPS'] = '0'
os.environ['DS_BUILD_SPARSE_ATTN'] = '0'

# Monkey-patch the deepspeed builder to avoid CUDA checks
import deepspeed.ops.op_builder.builder as builder_module

original_installed_cuda_version = builder_module.installed_cuda_version

def patched_installed_cuda_version():
    """Return a default CUDA version without checking nvcc"""
    try:
        return original_installed_cuda_version()
    except:
        # Return a reasonable default if CUDA check fails
        return (12, 4)  # CUDA 12.4 as shown by nvidia-smi

builder_module.installed_cuda_version = patched_installed_cuda_version

# Now import and run the original demo_page
exec(open('/home/ashok/Documents/GitHub/Dolphin/demo_page.py').read())
