"""
Wrapper script to run Dolphin without CUDA compilation requirements
"""
import os
import sys

# Disable DeepSpeed ops building before any imports
os.environ['DS_BUILD_OPS'] = '0'
os.environ['DS_BUILD_SPARSE_ATTN'] = '0'
os.environ['DS_BUILD_FUSED_ADAM'] = '0'
os.environ['DS_BUILD_CPU_ADAM'] = '0'
os.environ['DS_BUILD_UTILS'] = '0'
os.environ['DS_BUILD_AIO'] = '0'

# Mock CUDA_HOME if not available
if 'CUDA_HOME' not in os.environ:
    # Check if nvcc exists
    import shutil
    nvcc_path = shutil.which('nvcc')
    if nvcc_path:
        os.environ['CUDA_HOME'] = os.path.dirname(os.path.dirname(nvcc_path))
    else:
        # Set a dummy path to avoid errors during import
        os.environ['CUDA_HOME'] = '/usr/local/cuda'

# Now run the actual demo_page script
import runpy
sys.argv[0] = 'demo_page.py'
runpy.run_path('demo_page.py', run_name='__main__')
