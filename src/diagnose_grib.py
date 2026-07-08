import xarray as xr
from pathlib import Path
import gc

def diagnose():
    grib_path = Path("D:/AFNO-FourCastNet-Antarctica/data/raw/era5_antarctica_2016_2025.grib")
    print("Opening GRIB file...")
    ds = xr.open_dataset(str(grib_path), engine="cfgrib")
    num_steps = ds.dims["time"]
    print(f"Total time steps: {num_steps}")
    
    # Try reading step-by-step
    print("Testing reading step-by-step to locate the error...")
    for step in range(num_steps):
        if step % 500 == 0:
            print(f"Testing step {step}...")
        try:
            # Try to load a single time step for all variables
            x = ds.isel(time=step).load()
        except Exception as e:
            print(f"\n❌ FAILED at step {step}!")
            print(f"Error: {type(e).__name__} - {e}")
            break
    else:
        print("\n✅ Successfully read all steps!")

if __name__ == "__main__":
    diagnose()
