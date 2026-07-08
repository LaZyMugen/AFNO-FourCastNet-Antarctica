import os
from pathlib import Path
import numpy as np
import xarray as xr
import gc
import time

def preprocess_maitri_safe():
    base_dir = Path("D:/AFNO-FourCastNet-Antarctica")
    raw_dir = base_dir / "data" / "raw"
    grib_path = raw_dir / "maitri_2016_2025.grib"
    out_maitri_path = base_dir / "era5_maitri.npy"
    
    # 1. Clean up old index files first to prevent cfgrib incompatibility errors
    print("Cleaning up old index files...")
    for idx_file in raw_dir.glob("*.idx"):
        try:
            idx_file.unlink()
            print(f"  Removed index file: {idx_file.name}")
        except Exception as e:
            print(f"  Warning: Could not remove {idx_file.name}: {e}")
            
    if not grib_path.exists():
        raise FileNotFoundError(f"GRIB file not found at {grib_path}")
    
    # 2. Open GRIB file in memory (since it's only 362 MB, we can load it directly)
    print("\nOpening GRIB file and loading to memory...")
    ds = xr.open_dataset(str(grib_path), engine="cfgrib")
    print(f"Dataset opened. Dimensions: {ds.dims}")
    
    # Variables in order: [t2m, u10, v10, z]
    maitri_vars = ["t2m", "u10", "v10", "z"]
    
    print("Extracting variables...")
    # Stack along variable dimension: shape (Time, Variables, Lat, Lon)
    maitri_data = np.stack([ds[v].values for v in maitri_vars], axis=1) # (13860, 4, 21, 81)
    print(f"Extracted shape: {maitri_data.shape}")
    
    # 3. Compute exact stats
    print("Computing normalization statistics...")
    maitri_means = maitri_data.mean(axis=(0, 2, 3), keepdims=True) # (1, 4, 1, 1)
    maitri_stds = maitri_data.std(axis=(0, 2, 3), keepdims=True)
    
    print("Maitri Stats:")
    for idx, var in enumerate(maitri_vars):
        print(f"  {var}: Mean = {maitri_means[0, idx, 0, 0]:.4f}, Std = {maitri_stds[0, idx, 0, 0]:.4f}")
        
    # 4. Normalize and save
    print("Normalizing dataset...")
    maitri_norm = (maitri_data - maitri_means) / maitri_stds
    
    print(f"Saving final dataset to {out_maitri_path}...")
    # Delete old file if it exists
    if out_maitri_path.exists():
        out_maitri_path.unlink()
    np.save(str(out_maitri_path), maitri_norm.astype(np.float32))
    
    ds.close()
    print("Preprocessing completed successfully for Maitri!")

if __name__ == "__main__":
    preprocess_safe_start = time.time()
    preprocess_maitri_safe()
    print(f"Total time taken: {time.time() - preprocess_safe_start:.2f} seconds")
