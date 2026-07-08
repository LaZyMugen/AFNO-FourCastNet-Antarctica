# src/create_figures_package.py
import os
import shutil
from pathlib import Path

def create_package():
    base_dir = Path("D:/AFNO-FourCastNet-Antarctica")
    target_dir = base_dir / "docs" / "antarctic_weather_forecasting_figures"
    
    # Subdirectories
    maitri_dir = target_dir / "Maitri_Station"
    bharati_dir = target_dir / "Bharati_Station"
    comparative_dir = target_dir / "Comparative_Inferences"
    
    # Clean previous if exists
    if target_dir.exists():
        shutil.rmtree(target_dir)
        
    # Recreate structure
    maitri_dir.mkdir(parents=True, exist_ok=True)
    bharati_dir.mkdir(parents=True, exist_ok=True)
    comparative_dir.mkdir(parents=True, exist_ok=True)
    
    # Mapping of source -> destination
    files_map = {
        # Maitri
        base_dir / "figures" / "maitri" / "training_history_maitri.png": 
            maitri_dir / "Figure1_Maitri_Loss_History.png",
        base_dir / "figures" / "maitri" / "dashboards" / "dashboard_temp_scatter_maitri.png": 
            maitri_dir / "Figure2_Maitri_Temperature_Scatter.png",
        base_dir / "figures" / "maitri" / "dashboards" / "dashboard_wind_scatter_maitri.png": 
            maitri_dir / "Figure3_Maitri_Wind_Speed_Scatter.png",
        base_dir / "figures" / "maitri" / "dashboards" / "dashboard_storm_meteorogram_maitri.png": 
            maitri_dir / "Figure4_Maitri_Storm_Meteorogram.png",
        base_dir / "figures" / "maitri" / "dashboards" / "dashboard_climatology_drift_maitri.png": 
            maitri_dir / "Figure5_Maitri_Climatological_Drift.png",
            
        # Bharati
        base_dir / "figures" / "bharati" / "training_history_bharati.png": 
            bharati_dir / "Figure6_Bharati_Loss_History.png",
        base_dir / "figures" / "bharati" / "dashboards" / "dashboard2_temp_scatter_bharati.png": 
            bharati_dir / "Figure7_Bharati_Temperature_Scatter.png",
        base_dir / "figures" / "bharati" / "dashboards" / "dashboard_wind_scatter_bharati.png": 
            bharati_dir / "Figure8_Bharati_Wind_Speed_Scatter.png",
        base_dir / "figures" / "bharati" / "dashboards" / "dashboard_storm_meteorogram_bharati.png": 
            bharati_dir / "Figure9_Bharati_Storm_Meteorogram.png",
        base_dir / "figures" / "bharati" / "dashboards" / "dashboard_climatology_drift_bharati.png": 
            bharati_dir / "Figure10_Bharati_Climatological_Drift.png",
            
        # Comparative Inferences
        base_dir / "figures" / "maitri" / "epoch_020" / "t2m_timeseries_maitri.png": 
            comparative_dir / "Figure11_Sample_Epoch_T2M_Timeseries.png",
        base_dir / "figures" / "antarctic_running_average.png": 
            comparative_dir / "Figure12_30Day_Running_Average_Forecast_Comparison.png",
    }
    
    print("Copying and renaming high-res figures...")
    for src, dst in files_map.items():
        if src.exists():
            shutil.copy2(src, dst)
            print(f"Copied: {src.name} -> {dst.name}")
        else:
            print(f"Warning: Source file not found: {src}")
            
    # Create README.txt
    readme_content = """Antarctic Weather Forecasting - High-Resolution Figures Package
====================================================================
Student: Shaswat Sahoo (BITS Pilani)
Expert Mentor: Prof. VS Samy (NCPOR Goa)
Project: Regional Adaptation of AFNO-FourCastNet for Indian Antarctic Stations

This package contains the complete set of high-resolution figures generated 
during the regional weather forecasting project for Maitri and Bharati stations.

Folder Structure:
-----------------
1. /Maitri_Station/
   - Figure1_Maitri_Loss_History.png: MSE training and validation loss curves across 30 epochs.
   - Figure2_Maitri_Temperature_Scatter.png: Validation scatter plot comparing raw and bias-corrected 2m temperature forecasts.
   - Figure3_Maitri_Wind_Speed_Scatter.png: Validation scatter plot for 10m wind speed predictions.
   - Figure4_Maitri_Storm_Meteorogram.png: 72-hour timeseries tracking a severe storm event (temperature drop & wind speed spike).
   - Figure5_Maitri_Climatological_Drift.png: Climatological drift and auto-regressive smoothing analysis over a 12-month period.

2. /Bharati_Station/
   - Figure6_Bharati_Loss_History.png: MSE convergence curve on the larger 120x200 spatial domain.
   - Figure7_Bharati_Temperature_Scatter.png: Temperature scatter plot verifying forecast quality up to 280 K.
   - Figure8_Bharati_Wind_Speed_Scatter.png: Wind speed scatter plot for Larsemann Hills coastal wind shear.
   - Figure9_Bharati_Storm_Meteorogram.png: 72-hour timeseries tracking a severe coastal storm.
   - Figure10_Bharati_Climatological_Drift.png: Bharati monthly climatology and auto-regressive variance drift analysis.

3. /Comparative_Inferences/
   - Figure11_Sample_Epoch_T2M_Timeseries.png: Line plot showing actual vs. predicted temperature timeseries at Epoch 20.
   - Figure12_30Day_Running_Average_Forecast_Comparison.png: High-resolution running average comparison chart, comparing actual temperature, original global forecast, and our corrected forecast with seasonal shading.
"""
    
    with open(target_dir / "README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("README.txt created.")
    
    # Create ZIP archive
    zip_output = base_dir / "docs" / "antarctic_weather_forecasting_figures"
    print("Creating ZIP archive...")
    shutil.make_archive(str(zip_output), 'zip', str(target_dir))
    print(f"Structured figures package successfully zipped to {zip_output}.zip")

if __name__ == "__main__":
    create_package()
