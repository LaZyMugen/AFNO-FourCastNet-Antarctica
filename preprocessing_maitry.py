"""
preprocessing_maitry.py

Converts GRIB files (from CDN) into normalized numpy arrays for FourCastNet training.

Pipeline:
  GRIB Files (raw/) 
    ↓ Extract 4 variables (T, U, V, Z)
    ↓ Stack into channels
    ↓ Compute mean/std
    ↓ Normalize
    ↓ Save as .npy files (processed/)

Usage:
    python preprocessing_maitry.py
"""

import numpy as np
import xarray as xr
import os
from pathlib import Path
import glob
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

# Directory structure
BASE_DIR = Path(__file__).parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

# Create processed directory if it doesn't exist
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Output file names
OUTPUT_DATA_FILE = PROCESSED_DATA_DIR / "era5_maitri.npy"
OUTPUT_MEAN_FILE = PROCESSED_DATA_DIR / "mean.npy"
OUTPUT_STD_FILE = PROCESSED_DATA_DIR / "std.npy"

# Variables to extract (4-channel)
# T:  Temperature (2m)
# U:  U-wind component (10m)
# V:  V-wind component (10m)
# Z:  Geopotential height
VARIABLES = ["t", "u", "v", "z"]  # lowercase for xarray
VARIABLE_NAMES = {
    "t": "Temperature (2m)",
    "u": "U-wind (10m)",
    "v": "V-wind (10m)",
    "z": "Geopotential Height"
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def find_grib_files():
    """
    Find all GRIB files in raw data directory.
    
    Returns:
        list: Paths to all .grib files found
    """
    grib_pattern = RAW_DATA_DIR / "*.grib"
    grib_files = sorted(glob.glob(str(grib_pattern)))
    
    if not grib_files:
        raise FileNotFoundError(
            f"No GRIB files found in {RAW_DATA_DIR}\n"
            f"Expected: {RAW_DATA_DIR}/*.grib"
        )
    
    return grib_files


def load_and_extract_variables(grib_file, variables):
    """
    Load GRIB file and extract specified variables.
    
    Args:
        grib_file (str): Path to .grib file
        variables (list): List of variable names to extract
        
    Returns:
        dict: Dictionary with variable names as keys, data arrays as values
        
    Example:
        data = load_and_extract_variables("maitri_2016.grib", ["t", "u", "v", "z"])
        # Returns: {"t": array, "u": array, "v": array, "z": array}
    """
    print(f"\n📖 Loading: {Path(grib_file).name}")
    
    try:
        # Open GRIB file with xarray
        # backend_kwargs handles GRIB-specific options
        ds = xr.open_dataset(
            grib_file,
            engine="cfgrib",
            backend_kwargs={"indexpath": ""}
        )
        
        print(f"   File loaded. Available variables: {list(ds.data_vars)}")
        
        # Extract variables
        extracted_data = {}
        
        for var in variables:
            # Try different naming conventions
            var_name = None
            
            # Try exact match (lowercase)
            if var in ds.data_vars:
                var_name = var
            # Try uppercase
            elif var.upper() in ds.data_vars:
                var_name = var.upper()
            # Try with numbers (GRIB often has var1, var2, etc.)
            else:
                # Find by long_name or other attributes
                for name, data_var in ds.data_vars.items():
                    if var.lower() in str(name).lower():
                        var_name = name
                        break
            
            if var_name is None:
                print(f"   ⚠️  Warning: Variable '{var}' not found in file")
                continue
            
            # Get the data
            data_array = ds[var_name].values
            extracted_data[var] = data_array
            
            print(f"   ✓ Extracted '{var}' (shape: {data_array.shape})")
        
        ds.close()
        return extracted_data
    
    except Exception as e:
        print(f"   ❌ Error loading file: {e}")
        raise


def stack_variables_into_channels(all_timesteps_data):
    """
    Stack variables into channel dimension.
    
    Input shape for each variable: (time, lat, lon)
    Output shape: (time, channels, lat, lon) where channels = 4
    
    Args:
        all_timesteps_data (list): List of dicts with variable data
                                   Each dict from one GRIB file
        
    Returns:
        np.ndarray: Stacked data of shape (total_time, 4, lat, lon)
        
    Example:
        Input:  [{"t": (8760, 120, 200), "u": (8760, 120, 200), ...}, ...]
        Output: (35040, 4, 120, 200)  # 4 files × 8760 timesteps each
    """
    print("\n📚 Stacking variables into channels...")
    
    all_data = []
    
    for file_idx, file_data in enumerate(all_timesteps_data):
        # Stack variables along new axis
        # Variables: [T, U, V, Z] → shape (time, 4, lat, lon)
        stacked = np.stack([
            file_data["t"],
            file_data["u"],
            file_data["v"],
            file_data["z"]
        ], axis=1)
        
        print(f"   File {file_idx + 1}: Stacked shape {stacked.shape}")
        all_data.append(stacked)
    
    # Concatenate all files along time axis
    concatenated = np.concatenate(all_data, axis=0)
    print(f"\n   ✓ Total concatenated shape: {concatenated.shape}")
    print(f"      (timesteps, channels, lat, lon)")
    
    return concatenated


def validate_data(data):
    """
    Validate data integrity.
    
    Args:
        data (np.ndarray): Data array to validate
        
    Returns:
        bool: True if valid
    """
    print("\n🔍 Validating data...")
    
    # Check for NaN values
    nan_count = np.isnan(data).sum()
    if nan_count > 0:
        print(f"   ⚠️  Found {nan_count} NaN values")
    
    # Check for infinite values
    inf_count = np.isinf(data).sum()
    if inf_count > 0:
        print(f"   ⚠️  Found {inf_count} infinite values")
    
    # Show data statistics
    print(f"   Data range: [{data.min():.4f}, {data.max():.4f}]")
    print(f"   Data mean: {data.mean():.4f}")
    print(f"   Data std: {data.std():.4f}")
    
    return True


def compute_normalization_statistics(data):
    """
    Compute mean and std per channel across time and space.
    
    Input shape: (time, channels, lat, lon)
    
    Mean/Std shape: (channels,) - one value per channel
    
    Why? Each variable (T, U, V, Z) has different scale:
      - Temperature: 250-310 K
      - Wind: -20 to +20 m/s
      - Geopotential: 45000-55000 m²/s²
    
    Normalizing per-channel ensures fair representation.
    
    Args:
        data (np.ndarray): Shape (time, channels, lat, lon)
        
    Returns:
        tuple: (mean, std) each of shape (channels,)
    """
    print("\n📊 Computing normalization statistics...")
    print("   Averaging across: time, latitude, longitude")
    print("   Computing per: channel")
    
    # Compute mean and std
    # axis=(0, 2, 3) means average over time (0), lat (2), lon (3)
    # Keep channel (1) separate
    mean = data.mean(axis=(0, 2, 3))
    std = data.std(axis=(0, 2, 3))
    
    print(f"\n   Channel means: {mean}")
    print(f"   Channel stds:  {std}")
    
    # Check for zero std (would cause division by zero)
    if np.any(std == 0):
        print("   ⚠️  Warning: Some channels have std=0 (constant values)")
    
    return mean, std


def normalize_data(data, mean, std, epsilon=1e-6):
    """
    Normalize data: (x - mean) / (std + epsilon)
    
    epsilon prevents division by zero if std is very small.
    
    Input shape: (time, channels, lat, lon)
    mean/std shape: (channels,)
    
    Broadcasting:
      data:   (T, C, H, W)
      mean:   (C,) → (1, C, 1, 1) for broadcasting
      std:    (C,) → (1, C, 1, 1) for broadcasting
    
    Args:
        data (np.ndarray): Shape (time, channels, lat, lon)
        mean (np.ndarray): Shape (channels,)
        std (np.ndarray): Shape (channels,)
        epsilon (float): Small value to prevent division by zero
        
    Returns:
        np.ndarray: Normalized data, same shape as input
    """
    print("\n🔧 Normalizing data...")
    
    # Reshape for broadcasting
    mean_reshaped = mean[None, :, None, None]  # (1, C, 1, 1)
    std_reshaped = std[None, :, None, None]    # (1, C, 1, 1)
    
    # Normalize
    normalized = (data - mean_reshaped) / (std_reshaped + epsilon)
    
    print(f"   Normalized range: [{normalized.min():.4f}, {normalized.max():.4f}]")
    print(f"   Normalized mean (should be ~0): {normalized.mean():.6f}")
    print(f"   Normalized std (should be ~1): {normalized.std():.6f}")
    
    return normalized


def save_processed_data(data, mean, std):
    """
    Save processed data and statistics to .npy files.
    
    Args:
        data (np.ndarray): Processed data array
        mean (np.ndarray): Mean statistics
        std (np.ndarray): Std statistics
    """
    print("\n💾 Saving files...")
    
    # Save data
    np.save(str(OUTPUT_DATA_FILE), data.astype(np.float32))
    print(f"   ✓ Data saved: {OUTPUT_DATA_FILE}")
    print(f"     Size: {OUTPUT_DATA_FILE.stat().st_size / (1024**3):.2f} GB")
    
    # Save mean
    np.save(str(OUTPUT_MEAN_FILE), mean.astype(np.float32))
    print(f"   ✓ Mean saved: {OUTPUT_MEAN_FILE}")
    print(f"     Shape: {mean.shape}")
    
    # Save std
    np.save(str(OUTPUT_STD_FILE), std.astype(np.float32))
    print(f"   ✓ Std saved: {OUTPUT_STD_FILE}")
    print(f"     Shape: {std.shape}")


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def main():
    """Main preprocessing pipeline"""
    
    print("=" * 70)
    print("🌍 FourCastNet MAITRI Data Preprocessing Pipeline")
    print("=" * 70)
    
    # Step 1: Find GRIB files
    print("\n[Step 1/6] Finding GRIB files...")
    grib_files = find_grib_files()
    print(f"✓ Found {len(grib_files)} GRIB files:")
    for f in grib_files:
        print(f"    - {Path(f).name}")
    
    # Step 2: Load and extract variables from all files
    print("\n[Step 2/6] Loading and extracting variables...")
    all_file_data = []
    
    for grib_file in grib_files:
        try:
            file_data = load_and_extract_variables(grib_file, VARIABLES)
            all_file_data.append(file_data)
        except Exception as e:
            print(f"   ❌ Error processing {grib_file}: {e}")
            continue
    
    if not all_file_data:
        raise RuntimeError("Could not process any GRIB files")
    
    print(f"✓ Successfully processed {len(all_file_data)} files")
    
    # Step 3: Stack variables into channels
    print("\n[Step 3/6] Stacking variables into channels...")
    data = stack_variables_into_channels(all_file_data)
    print(f"✓ Stacking complete. Shape: {data.shape}")
    
    # Step 4: Validate data
    print("\n[Step 4/6] Validating data...")
    validate_data(data)
    print("✓ Data validation passed")
    
    # Step 5: Compute normalization statistics
    print("\n[Step 5/6] Computing normalization statistics...")
    mean, std = compute_normalization_statistics(data)
    print("✓ Statistics computed")
    
    # Step 6: Normalize data
    print("\n[Step 6/6] Normalizing data...")
    normalized_data = normalize_data(data, mean, std)
    print("✓ Data normalized")
    
    # Step 7: Save files
    print("\n[Step 7/7] Saving processed files...")
    save_processed_data(normalized_data, mean, std)
    print("✓ All files saved")
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ PREPROCESSING COMPLETE")
    print("=" * 70)
    print(f"\nOutput files:")
    print(f"  📁 {OUTPUT_DATA_FILE}")
    print(f"  📁 {OUTPUT_MEAN_FILE}")
    print(f"  📁 {OUTPUT_STD_FILE}")
    print(f"\nNext steps:")
    print(f"  1. Verify files exist:")
    print(f"     ls -lh {PROCESSED_DATA_DIR}/")
    print(f"  2. Update train.py to use: era5_maitri.npy")
    print(f"  3. Run training:")
    print(f"     cd src && python train.py")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
