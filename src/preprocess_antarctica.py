import os
from pathlib import Path
import numpy as np
import xarray as xr
import gc

def preprocess_all():
    base_dir = Path("D:/AFNO-FourCastNet-Antarctica")
    raw_dir = base_dir / "data" / "raw"
    
    old_grib_path = raw_dir / "61415ef17b226157ddae17aa0dcd7f29 (1).grib"
    new_grib_path = raw_dir / "era5_antarctica_2016_2025.grib"
    
    # 1. Rename the GRIB file
    if old_grib_path.exists():
        print(f"Renaming {old_grib_path.name} to {new_grib_path.name}...")
        old_grib_path.rename(new_grib_path)
    else:
        print(f"File already renamed or not found at {old_grib_path}")
        
    if not new_grib_path.exists():
        raise FileNotFoundError(f"GRIB file not found at {new_grib_path}")
        
    # 2. Get the total number of time steps first
    print("Opening GRIB file to get dimensions...")
    temp_ds = xr.open_dataset(str(new_grib_path), engine="cfgrib")
    num_steps = int(temp_ds.sizes["time"])
    temp_ds.close()
    del temp_ds
    gc.collect()
    
    print(f"Total time steps: {num_steps}")
    chunk_size = 500  # Process in chunks of 500 steps to keep RAM extremely low
    
    # 3. Preprocess BHARATI Station Region (using Memory-Mapped files)
    print("\nProcessing BHARATI Station Dataset (using Memory-Mapped files to prevent RAM freezing)...")
    bharati_vars = ["u10", "v10", "t2m", "msl"]
    out_bharati_path = base_dir / "era5_processed.npy"
    
    # Pre-allocate the .npy file on disk using np.memmap (uses ZERO RAM)
    print(f"Pre-allocating memory-mapped file for Bharati: {out_bharati_path.name}")
    # Note: np.save writes a header. To make it a standard .npy file, we can write it using np.lib.format
    # but the easiest way to create a valid .npy file of a specific shape is to write a dummy header.
    # We will write the array directly as a raw binary file first, or we can use a helper to create the .npy header.
    # To keep it simple and create a valid .npy file, we can initialize it with a small array and then memmap it:
    # Actually, we can use np.lib.format.open_memmap which is the standard numpy function to create a memmapped .npy file!
    bharati_data = np.lib.format.open_memmap(
        str(out_bharati_path),
        dtype=np.float32,
        mode="w+",
        shape=(num_steps, 4, 120, 200)
    )
    
    print("Extracting variables in chunks...")
    for start in range(0, num_steps, chunk_size):
        end = min(start + chunk_size, num_steps)
        print(f"  Bharati: Extracting steps {start} to {end}...")
        
        # Open dataset for this chunk only
        ds = xr.open_dataset(str(new_grib_path), engine="cfgrib")
        
        # Slice chunk and spatial region
        ds_chunk = ds.isel(time=slice(start, end))
        ds_bharati_chunk = ds_chunk.sel(latitude=slice(-60.0, -89.75), longitude=slice(50.0, 99.75))
        
        # Load values directly into the memory-mapped file
        for v_idx, v in enumerate(bharati_vars):
            bharati_data[start:end, v_idx] = ds_bharati_chunk[v].values
            
        # Close and delete to free eccodes memory
        ds.close()
        del ds_chunk
        del ds_bharati_chunk
        del ds
        gc.collect()
        
    # Compute stats for normalization in a memory-efficient way (chunked)
    print("Computing normalization statistics in chunks...")
    total_pixels = num_steps * 120 * 200
    sums = np.zeros(4, dtype=np.float64)
    sq_sums = np.zeros(4, dtype=np.float64)
    
    for start in range(0, num_steps, chunk_size):
        end = min(start + chunk_size, num_steps)
        chunk = bharati_data[start:end] # Loads only this chunk into RAM
        sums += chunk.sum(axis=(0, 2, 3))
        sq_sums += (chunk ** 2).sum(axis=(0, 2, 3))
        
    bharati_means = sums / total_pixels
    bharati_stds = np.sqrt((sq_sums / total_pixels) - (bharati_means ** 2))
    
    print("Bharati Stats:")
    for idx, var in enumerate(bharati_vars):
        print(f"  {var}: Mean = {bharati_means[idx]:.4f}, Std = {bharati_stds[idx]:.4f}")
        
    # Normalize in-place in chunks (uses almost zero RAM)
    print("Normalizing Bharati dataset in-place...")
    for start in range(0, num_steps, chunk_size):
        end = min(start + chunk_size, num_steps)
        chunk = bharati_data[start:end]
        for v_idx in range(4):
            chunk[:, v_idx] = (chunk[:, v_idx] - bharati_means[v_idx]) / bharati_stds[v_idx]
        bharati_data.flush() # Flush changes to disk
        
    # Close memory-mapped file
    del bharati_data
    gc.collect()
    print("Bharati dataset saved.")
    
    # 4. Preprocess MAITRI Station Region (using Memory-Mapped files)
    print("\nProcessing MAITRI Station Dataset (using Memory-Mapped files)...")
    maitri_vars = ["t2m", "u10", "v10", "z"]
    out_maitri_path = base_dir / "era5_maitri.npy"
    
    print(f"Pre-allocating memory-mapped file for Maitri: {out_maitri_path.name}")
    maitri_data = np.lib.format.open_memmap(
        str(out_maitri_path),
        dtype=np.float32,
        mode="w+",
        shape=(num_steps, 4, 21, 101)
    )
    
    print("Extracting variables in chunks...")
    for start in range(0, num_steps, chunk_size):
        end = min(start + chunk_size, num_steps)
        print(f"  Maitri: Extracting steps {start} to {end}...")
        
        # Open dataset for this chunk only
        ds = xr.open_dataset(str(new_grib_path), engine="cfgrib")
        
        # Slice chunk and spatial region
        ds_chunk = ds.isel(time=slice(start, end))
        ds_maitri_chunk = ds_chunk.sel(latitude=slice(-68.0, -73.0), longitude=slice(0.0, 25.0))
        
        # Load values directly into the memory-mapped file
        for v_idx, v in enumerate(maitri_vars):
            maitri_data[start:end, v_idx] = ds_maitri_chunk[v].values
            
        ds.close()
        del ds_chunk
        del ds_maitri_chunk
        del ds
        gc.collect()
        
    # Compute stats for normalization in a memory-efficient way (chunked)
    print("Computing normalization statistics in chunks...")
    total_pixels_m = num_steps * 21 * 101
    sums_m = np.zeros(4, dtype=np.float64)
    sq_sums_m = np.zeros(4, dtype=np.float64)
    
    for start in range(0, num_steps, chunk_size):
        end = min(start + chunk_size, num_steps)
        chunk = maitri_data[start:end]
        sums_m += chunk.sum(axis=(0, 2, 3))
        sq_sums_m += (chunk ** 2).sum(axis=(0, 2, 3))
        
    maitri_means = sums_m / total_pixels_m
    maitri_stds = np.sqrt((sq_sums_m / total_pixels_m) - (maitri_means ** 2))
    
    print("Maitri Stats:")
    for idx, var in enumerate(maitri_vars):
        print(f"  {var}: Mean = {maitri_means[idx]:.4f}, Std = {maitri_stds[idx]:.4f}")
        
    # Normalize in-place in chunks
    print("Normalizing Maitri dataset in-place...")
    for start in range(0, num_steps, chunk_size):
        end = min(start + chunk_size, num_steps)
        chunk = maitri_data[start:end]
        for v_idx in range(4):
            chunk[:, v_idx] = (chunk[:, v_idx] - maitri_means[v_idx]) / maitri_stds[v_idx]
        maitri_data.flush()
        
    # Close memory-mapped file
    del maitri_data
    gc.collect()
    print("Maitri dataset saved.")
    
    print("\nPreprocessing completed successfully for both stations!")

if __name__ == "__main__":
    preprocess_all()
