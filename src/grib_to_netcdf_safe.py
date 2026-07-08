import os

# Limit CPU to 1 thread immediately to prevent thermal overload
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

from pathlib import Path
import numpy as np
import xarray as xr
import netCDF4 as nc
import gc
import time

def convert_grib_to_netcdf_safe():
    base_dir = Path("D:/AFNO-FourCastNet-Antarctica")
    raw_dir = base_dir / "data" / "raw"
    grib_path = raw_dir / "era5_antarctica_2016_2025.grib"
    nc_path = raw_dir / "era5_antarctica_2016_2025.nc"
    
    # 1. Delete any existing incompatible index files first
    print("Cleaning up old index files...")
    for idx_file in raw_dir.glob("*.idx"):
        try:
            idx_file.unlink()
            print(f"  Removed index file: {idx_file.name}")
        except Exception as e:
            print(f"  Warning: Could not remove {idx_file.name}: {e}")
            
    if not grib_path.exists():
        raise FileNotFoundError(f"GRIB file not found at {grib_path}")
        
    # Delete old NC file if it exists
    if nc_path.exists():
        try:
            nc_path.unlink()
            print("Removed existing NetCDF file.")
        except Exception as e:
            print(f"Warning: Could not remove old NetCDF file: {e}")
            
    print("\nOpening GRIB file to initialize NetCDF4 structure...")
    ds_grib = xr.open_dataset(str(grib_path), engine="cfgrib")
    num_steps = int(ds_grib.sizes["time"])
    latitudes = ds_grib.latitude.values
    longitudes = ds_grib.longitude.values
    variables = list(ds_grib.data_vars)
    
    print(f"Dimensions: time={num_steps}, latitude={len(latitudes)}, longitude={len(longitudes)}")
    print(f"Variables to convert: {variables}")
    
    # Create NetCDF4 File (Uncompressed to reduce CPU load and heat)
    print(f"Creating uncompressed NetCDF4 file: {nc_path.name}...")
    f = nc.Dataset(str(nc_path), 'w', format='NETCDF4')
    
    # Create dimensions
    f.createDimension('time', None)  # Unlimited dimension
    f.createDimension('latitude', len(latitudes))
    f.createDimension('longitude', len(longitudes))
    
    # Create coordinate variables
    lat_var = f.createVariable('latitude', 'f4', ('latitude',))
    lon_var = f.createVariable('longitude', 'f4', ('longitude',))
    
    # Write coordinates
    lat_var[:] = latitudes
    lon_var[:] = longitudes
    
    # Create data variables (zlib=False disables CPU compression, keeping CPU temperature cool)
    nc_vars = {}
    for var in variables:
        print(f"  Setting up uncompressed variable: {var}")
        nc_vars[var] = f.createVariable(
            var, 
            'f4', 
            ('time', 'latitude', 'longitude'), 
            zlib=False,  # Zero CPU compression load
            fill_value=np.nan
        )
        
    ds_grib.close()
    del ds_grib
    gc.collect()
    
    # Process and write in chunk sizes of 500
    chunk_size = 500
    print("\nStarting throttled and thermally-safe conversion...")
    for start in range(0, num_steps, chunk_size):
        end = min(start + chunk_size, num_steps)
        print(f"  Processing chunk {start} to {end}...")
        
        # Load GRIB chunk (runs on 1 CPU core)
        ds_grib = xr.open_dataset(str(grib_path), engine="cfgrib")
        ds_chunk = ds_grib.isel(time=slice(start, end)).load()
        
        # Write variables
        for var in variables:
            nc_vars[var][start:end, :, :] = ds_chunk[var].values
            
        ds_grib.close()
        f.sync()  # Flush chunk to disk
        
        del ds_grib
        del ds_chunk
        gc.collect()
        
        # Cooling break: Let CPU cool down and SSD clear cache
        print("  Cooldon break: pausing for 1.5 seconds...")
        time.sleep(1.5)
        
    f.close()
    print("\n🎉 Conversion successfully completed under safe thermal constraints!")
    print("Pausing for 5 seconds to let Windows complete final flush...")
    time.sleep(5)
    print(f"Final uncompressed NetCDF file size: {nc_path.stat().st_size / (1024**3):.2f} GB")

if __name__ == "__main__":
    convert_grib_to_netcdf_safe()
