#!/usr/bin/env python3
"""
Quick test for dataset normalization fix
"""

import sys
from pathlib import Path
import numpy as np

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from dataset import ERA5Dataset

print("Testing normalization with different means/stds shapes...\n")

# Test 1: 1D means/stds (what user has)
print("Test 1: 1D means/stds shape (4,)")
print("-" * 50)

dummy_data = np.random.randn(100, 4, 120, 200)
means_1d = np.array([10.0, 20.0, 30.0, 40.0])  # shape (4,)
stds_1d = np.array([1.0, 2.0, 3.0, 4.0])      # shape (4,)

print(f"Data shape: {dummy_data.shape}")
print(f"Means shape: {means_1d.shape}")
print(f"Stds shape: {stds_1d.shape}")

try:
    dataset_1d = ERA5Dataset(
        dummy_data,
        in_steps=8,
        out_steps=4,
        means=means_1d,
        stds=stds_1d,
        normalize=True
    )
    
    x, y = dataset_1d[0]
    print(f"✓ Sample X shape: {x.shape}")
    print(f"✓ Sample Y shape: {y.shape}")
    print(f"✓ Test 1 PASSED\n")
except Exception as e:
    print(f"✗ Test 1 FAILED: {e}\n")
    sys.exit(1)

# Test 2: 3D means/stds (spatial statistics)
print("Test 2: 3D means/stds shape (4, 120, 200)")
print("-" * 50)

means_3d = np.random.randn(4, 120, 200)
stds_3d = np.abs(np.random.randn(4, 120, 200)) + 0.1  # Ensure positive

print(f"Data shape: {dummy_data.shape}")
print(f"Means shape: {means_3d.shape}")
print(f"Stds shape: {stds_3d.shape}")

try:
    dataset_3d = ERA5Dataset(
        dummy_data,
        in_steps=8,
        out_steps=4,
        means=means_3d,
        stds=stds_3d,
        normalize=True
    )
    
    x, y = dataset_3d[0]
    print(f"✓ Sample X shape: {x.shape}")
    print(f"✓ Sample Y shape: {y.shape}")
    print(f"✓ Test 2 PASSED\n")
except Exception as e:
    print(f"✗ Test 2 FAILED: {e}\n")
    sys.exit(1)

# Test 3: No normalization
print("Test 3: No normalization (normalize=False)")
print("-" * 50)

try:
    dataset_no_norm = ERA5Dataset(
        dummy_data,
        in_steps=8,
        out_steps=4,
        means=means_1d,
        stds=stds_1d,
        normalize=False
    )
    
    x, y = dataset_no_norm[0]
    print(f"✓ Sample X shape: {x.shape}")
    print(f"✓ Sample Y shape: {y.shape}")
    print(f"✓ Test 3 PASSED\n")
except Exception as e:
    print(f"✗ Test 3 FAILED: {e}\n")
    sys.exit(1)

print("=" * 50)
print("✓ All normalization tests passed!")
print("=" * 50)
print("\nYou can now run: cd src && python train.py")
