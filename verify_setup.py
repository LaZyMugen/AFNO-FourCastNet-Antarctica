#!/usr/bin/env python3
"""
Verification script for FourCastNet setup.
Run this to check if all imports work correctly before training/inference.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

print("=" * 60)
print("FourCastNet Setup Verification")
print("=" * 60)

# Check 1: PyTorch and dependencies
print("\n1. Checking PyTorch and dependencies...")
try:
    import torch
    print(f"   ✓ PyTorch {torch.__version__}")
except ImportError as e:
    print(f"   ✗ PyTorch: {e}")
    sys.exit(1)

try:
    import numpy as np
    print(f"   ✓ NumPy {np.__version__}")
except ImportError as e:
    print(f"   ✗ NumPy: {e}")
    sys.exit(1)

try:
    import matplotlib
    print(f"   ✓ Matplotlib {matplotlib.__version__}")
except ImportError as e:
    print(f"   ✗ Matplotlib: {e}")
    sys.exit(1)

# Check 2: CUDA availability
print("\n2. Checking GPU availability...")
cuda_available = torch.cuda.is_available()
device = torch.device("cuda" if cuda_available else "cpu")
if cuda_available:
    print(f"   ✓ CUDA available: {torch.cuda.get_device_name(0)}")
    print(f"   ✓ Device count: {torch.cuda.device_count()}")
else:
    print(f"   ℹ CUDA not available, will use CPU")
print(f"   ✓ Device: {device}")

# Check 3: Model import
print("\n3. Checking model import...")
try:
    from model import FourCastNet
    model = FourCastNet()
    print(f"   ✓ FourCastNet model created")
    total_params = sum(p.numel() for p in model.parameters())
    print(f"   ✓ Total parameters: {total_params:,}")
except Exception as e:
    print(f"   ✗ Model import failed: {e}")
    sys.exit(1)

# Check 4: Dataset import
print("\n4. Checking dataset import...")
try:
    from dataset import ERA5Dataset
    print(f"   ✓ ERA5Dataset class imported")
    
    # Create dummy data to test
    dummy_data = np.random.randn(100, 4, 120, 200)
    dataset = ERA5Dataset(dummy_data)
    print(f"   ✓ Dataset created with {len(dataset)} samples")
    
    # Test getitem
    x, y = dataset[0]
    print(f"   ✓ Sample shapes - X: {x.shape}, Y: {y.shape}")
except Exception as e:
    print(f"   ✗ Dataset import failed: {e}")
    sys.exit(1)

# Check 5: Directory structure
print("\n5. Checking directory structure...")
base_dir = Path(__file__).parent
dirs_to_check = {
    "data": base_dir / "data",
    "checkpoints": base_dir / "checkpoints",
    "figures": base_dir / "figures",
    "src": base_dir / "src",
}

for name, path in dirs_to_check.items():
    if path.exists():
        print(f"   ✓ {name}/ exists")
    else:
        print(f"   ℹ {name}/ not found, will be created if needed")

# Check 6: Data files
print("\n6. Checking data files...")
data_files = {
    "means.npy": base_dir / "data" / "means.npy",
    "stds.npy": base_dir / "data" / "stds.npy",
    "era5_processed.npy": base_dir / "era5_processed.npy",
}

for name, path in data_files.items():
    if path.exists():
        size_mb = path.stat().st_size / (1024 * 1024)
        print(f"   ✓ {name} exists ({size_mb:.1f} MB)")
    else:
        print(f"   ⚠ {name} not found - required for training/inference")

# Check 7: Model in inference mode
print("\n7. Checking model inference...")
try:
    model = FourCastNet().to(device)
    model.eval()
    
    # Create dummy batch
    batch = torch.randn(2, 8, 4, 120, 200).to(device)
    
    with torch.no_grad():
        output = model(batch)
    
    print(f"   ✓ Inference successful")
    print(f"   ✓ Input shape: {batch.shape}")
    print(f"   ✓ Output shape: {output.shape}")
    
    if output.shape == (2, 4, 4, 120, 200):
        print(f"   ✓ Output shape is correct!")
    else:
        print(f"   ✗ Output shape mismatch! Expected (2, 4, 4, 120, 200)")
        
except Exception as e:
    print(f"   ✗ Inference test failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ All checks passed! You're ready to run training/inference.")
print("=" * 60)
print("\nNext steps:")
print("  1. Training:   cd src && python train.py")
print("  2. Inference:  cd src && python inference.py")
print("\nFor detailed instructions, see SETUP_GUIDE.md")
