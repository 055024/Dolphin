import os
import sys

# Must be set before deepspeed import
os.environ.setdefault('DS_BUILD_OPS', '0')
os.environ.setdefault('DS_BUILD_SPARSE_ATTN', '0')
os.environ.setdefault('CUDA_HOME', '/home/ashok/Documents/GitHub/Dolphin/fake_cuda')
