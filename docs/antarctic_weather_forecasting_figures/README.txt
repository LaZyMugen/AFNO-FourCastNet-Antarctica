Antarctic Weather Forecasting - High-Resolution Figures Package
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
