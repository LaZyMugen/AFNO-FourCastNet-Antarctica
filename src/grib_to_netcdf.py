import os
from pathlib import Path
import numpy as np
import xarray as xr
import netCDF4 as nc
import gc
import time

def convert_grib_to_netcdf():
    base_dir = Path("D:/AFNO-FourCastNet-Antarctica")
    raw_dir = base_dir / "data" / "raw"
    grib_path = raw_dir / "era5_antarctica_2016_2025.grib"
    nc_path = raw_dir / "era5_antarctica_2016_2025.nc"
    
    if not grib_path.exists():
        raise FileNotFoundError(f"GRIB file not found at {grib_path}")
        
    print("Opening GRIB file to initialize NetCDF4 structure...")
    ds_grib = xr.open_dataset(str(grib_path), engine="cfgrib")
    num_steps = int(ds_grib.sizes["time"])
    latitudes = ds_grib.latitude.values
    longitudes = ds_grib.longitude.values
    variables = list(ds_grib.data_vars)
    
    print(f"Dimensions: time={num_steps}, latitude={len(latitudes)}, longitude={len(longitudes)}")
    print(f"Variables to convert: {variables}")
    
    # Delete old NC file if it exists
    if nc_path.exists():
        nc_path.unlink()
        print("Removed existing NetCDF file.")
        
    # Create NetCDF4 File
    print(f"Creating NetCDF4 file: {nc_path.name}...")
    f = nc.Dataset(str(nc_path), 'w', format='NETCDF4')
    
    # Create dimensions
    f.createDimension('time', None)  # Unlimited dimension
    f.createDimension('latitude', len(latitudes))
    f.createDimension('longitude', len(longitudes))
    
    # Create variables
    lat_var = f.createVariable('latitude', 'f4', ('latitude',))
    lon_var = f.createVariable('longitude', 'f4', ('longitude',))
    
    # Write coordinates
    lat_var[:] = latitudes
    lon_var[:] = longitudes
    
    # Create compressed data variables
    nc_vars = {}
    for var in variables:
        print(f"  Setting up compressed variable: {var}")
        nc_vars[var] = f.createVariable(
            var, 
            'f4', 
            ('time', 'latitude', 'longitude'), 
            zlib=True, 
            complevel=4,
            fill_value=np.nan
        )
        
    ds_grib.close()
    del ds_grib
    gc.collect()
    
    # Process and write in small throttled chunks
    chunk_size = 500
    print("\nStarting chunked conversion...")
    for start in range(0, num_steps, chunk_size):
        end = min(start + chunk_size, num_steps)
        print(f"  Processing chunk {start} to {end}...")
        
        # Load GRIB chunk
        ds_grib = xr.open_dataset(str(grib_path), engine="cfgrib")
        ds_chunk = ds_grib.isel(time=slice(start, end)).load()
        
        # Write variables
        for var in variables:
            nc_vars[var][start:end, :, :] = ds_chunk[var].values
            
        ds_grib.close()
        f.sync()  # Sync changes to disk safely
        
        del ds_grib
        del ds_chunk
        gc.collect()
        
        # Throttling: Let SSD queue clear
        time.sleep(0.5)
        
    f.close()
    print("\nConversion successfully completed!")
    print("Pausing for 5 seconds to ensure final disk write is flushed...")
    time.sleep(5)
    print(f"Final NetCDF file size: {nc_path.stat().st_size / (1024**3):.2f} GB")

if __name__ == "__main__":
    convert_grib_to_netcdf()
