import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

import numpy as np
import torch
import pandas as pd
import matplotlib.pyplot as plt
import joblib
import datetime
from tqdm import tqdm
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error

from model import FourCastNet
from dataset import ERA5Dataset
from config.config import *

# Setup device
device = torch.device("cpu")

# Setup paths
base_dir = Path(__file__).parent.parent
checkpoint_dir = base_dir / "checkpoints" / STATION
figures_dir = base_dir / "figures" / STATION / "dashboards"
figures_dir.mkdir(parents=True, exist_ok=True)

# Load data
data_path = base_dir / DATA_FILE
data = np.load(str(data_path), mmap_mode="r")

# Load model
model = FourCastNet().to(device)
model_path = checkpoint_dir / f"best_model_{STATION}.pth"
if not model_path.exists():
    model_path = checkpoint_dir / "best_model.pth"

checkpoint = torch.load(str(model_path), map_location=device)
if "model_state_dict" in checkpoint:
    model.load_state_dict(checkpoint["model_state_dict"])
else:
    model.load_state_dict(checkpoint)
model.eval()

# Load bias correctors
bias_corr_dir = checkpoint_dir / "bias_correction"
corr_t = joblib.load(bias_corr_dir / f"bias_corrector_t2m_{STATION}.pkl")
corr_w = joblib.load(bias_corr_dir / f"bias_corrector_wind_{STATION}.pkl")

# Define physical stats for denormalization
if STATION == 'bharati':
    TEMP_MEAN, TEMP_STD = 262.8091, 8.1633
    U_MEAN, U_STD = -1.8267, 5.7533
    V_MEAN, V_STD = 0.9996, 4.8879
else:
    # Maitri 10-year stats computed from new dataset
    TEMP_MEAN, TEMP_STD = 256.5790, 11.4395
    U_MEAN, U_STD = -5.2171, 5.4809
    V_MEAN, V_STD = 2.9326, 3.7038

# Helper to denormalize temperature
def denorm_temp(t_norm):
    return (t_norm * TEMP_STD + TEMP_MEAN) - 273.15  # Convert to Celsius

# Helper to denormalize wind speed
def denorm_wind(u_norm, v_norm):
    u = u_norm * U_STD + U_MEAN
    v = v_norm * V_STD + V_MEAN
    return np.hypot(u, v)

# Helper to compute time features
def get_time_features(idx, station):
    start_year = 2017 if station == 'maitri' else 2016
    start_date = datetime.datetime(start_year, 1, 1, 0, 0, 0)
    
    current_date = start_date + datetime.timedelta(hours=int(idx) * TIME_INTERVAL_HOURS)
    day_progress = current_date.hour / 24.0
    day_progress_sin = np.sin(2 * np.pi * day_progress)
    day_progress_cos = np.cos(2 * np.pi * day_progress)
    
    year_progress = current_date.timetuple().tm_yday / 366.0
    year_progress_sin = np.sin(2 * np.pi * year_progress)
    year_progress_cos = np.cos(2 * np.pi * year_progress)
    
    return {
        "lead_hours": 0,  # Will be set dynamically
        "day_progress_sin": day_progress_sin,
        "day_progress_cos": day_progress_cos,
        "year_progress_sin": year_progress_sin,
        "year_progress_cos": year_progress_cos,
        "date": current_date
    }

def get_index_for_date(year, month, day, hour, start_year):
    target_dt = datetime.datetime(year, month, day, hour)
    start_dt = datetime.datetime(start_year, 1, 1, 0, 0)
    delta = target_dt - start_dt
    return int(delta.total_seconds() / (3600 * TIME_INTERVAL_HOURS))

# Define test splits dynamically based on the station
start_year = 2017 if STATION == 'maitri' else 2016
if STATION == 'maitri':
    test_start = get_index_for_date(2025, 1, 1, 0, 2017)
    test_end = len(data)
else:
    test_start = get_index_for_date(2024, 1, 1, 0, 2016)
    test_end = len(data)

test_indices = np.arange(test_start, test_end - IN_STEPS - OUT_STEPS)
test_indices = test_indices[::4]  # Stride of 24 hours
test_years_str = "2025-2026" if STATION == 'maitri' else "2024-2025"

rows = []
print(f"Running out-of-sample evaluation ({len(test_indices)} samples)...")

for idx in tqdm(test_indices):
    x = data[idx : idx + IN_STEPS]
    y = data[idx + IN_STEPS : idx + IN_STEPS + OUT_STEPS]
    
    x_tensor = torch.from_numpy(x).unsqueeze(0).to(device)
    with torch.no_grad():
        pred = model(x_tensor).squeeze(0).cpu().numpy()
        
    y_st = y[:, :, GRID_LAT_IDX, GRID_LON_IDX]
    pred_st = pred[:, :, GRID_LAT_IDX, GRID_LON_IDX]
    
    for step_idx in range(OUT_STEPS):
        target_idx = idx + IN_STEPS + step_idx
        time_feats = get_time_features(target_idx, STATION)
        lead_hours = (step_idx + 1) * TIME_INTERVAL_HOURS
        
        # Denormalize raw predictions and truth
        true_t = denorm_temp(y_st[step_idx, T2M_IDX])
        raw_pred_t = denorm_temp(pred_st[step_idx, T2M_IDX])
        
        true_w = denorm_wind(y_st[step_idx, U10_IDX], y_st[step_idx, V10_IDX])
        raw_pred_w = denorm_wind(pred_st[step_idx, U10_IDX], pred_st[step_idx, V10_IDX])
        
        # Prepare features for correctors (correctors are trained in physical space now)
        feat_t = np.array([[lead_hours, time_feats["day_progress_sin"], time_feats["day_progress_cos"], 
                            time_feats["year_progress_sin"], time_feats["year_progress_cos"], raw_pred_t]])
        
        feat_w = np.array([[lead_hours, time_feats["day_progress_sin"], time_feats["day_progress_cos"], 
                            time_feats["year_progress_sin"], time_feats["year_progress_cos"], raw_pred_w]])
        
        # Apply correctors (outputs are already in physical space)
        corr_pred_t = corr_t.predict(feat_t)[0]
        corr_pred_w = max(0.0, corr_w.predict(feat_w)[0])
        
        row = {
            "date": time_feats["date"],
            "lead_hours": lead_hours,
            "true_t": true_t,
            "raw_pred_t": raw_pred_t,
            "corr_pred_t": corr_pred_t,
            "true_w": true_w,
            "raw_pred_w": raw_pred_w,
            "corr_pred_w": corr_pred_w
        }
        rows.append(row)

df = pd.DataFrame(rows)

# -------------------------------------------------------------------------
# DASHBOARD GENERATION
# -------------------------------------------------------------------------
plt.rcParams.update({
    'font.sans-serif': 'DejaVu Sans',
    'font.family': 'sans-serif',
    'axes.unicode_minus': False
})

# Color palette (Harmony)
COLOR_TRUTH = '#2C3E50'   # Deep Slate Blue
COLOR_RAW = '#BDC3C7'     # Cool Gray
COLOR_CORR = '#E74C3C'    # Vibrant Red/Coral

# --- DASHBOARD 2: TEMPERATURE SCATTER PLOT (1x2 Panel) ---
fig, axes = plt.subplots(1, 2, figsize=(16, 7.5))

# Calculate metrics
r2_raw_t = r2_score(df["true_t"], df["raw_pred_t"])
mae_raw_t = mean_absolute_error(df["true_t"], df["raw_pred_t"])
rmse_raw_t = root_mean_squared_error(df["true_t"], df["raw_pred_t"])

r2_corr_t = r2_score(df["true_t"], df["corr_pred_t"])
mae_corr_t = mean_absolute_error(df["true_t"], df["corr_pred_t"])
rmse_corr_t = root_mean_squared_error(df["true_t"], df["corr_pred_t"])

# Title banner
fig.suptitle(
    f"Dashboard 2: 2m Temperature Scatter & Calibration (Out-of-Sample Years: {test_years_str}) - {STATION.upper()} STATION\n"
    f"Raw Model: R² = {r2_raw_t:.3f} | MAE = {mae_raw_t:.2f}°C | RMSE = {rmse_raw_t:.2f}°C    "
    f"Corrected: R² = {r2_corr_t:.3f} | MAE = {mae_corr_t:.2f}°C | RMSE = {rmse_corr_t:.2f}°C",
    fontsize=14, fontweight='bold', color='#2C3E50', y=0.96
)

# Panel 1: Raw Model
axes[0].scatter(df["true_t"], df["raw_pred_t"], alpha=0.3, color=COLOR_RAW, label='Raw Forecast')
axes[0].plot([df["true_t"].min(), df["true_t"].max()], [df["true_t"].min(), df["true_t"].max()], color='#27AE60', linestyle='--', linewidth=2, label='Perfect Calibration (1:1)')
axes[0].set_xlabel("Observed Temperature (°C)", fontsize=11, fontweight='bold')
axes[0].set_ylabel("Forecasted Temperature (°C)", fontsize=11, fontweight='bold')
axes[0].set_title("Raw Model Forecast vs Observations", fontsize=12, fontweight='bold', pad=10)
axes[0].grid(True, alpha=0.3, linestyle='--')
axes[0].legend()

# Panel 2: Corrected Model
axes[1].scatter(df["true_t"], df["corr_pred_t"], alpha=0.3, color=COLOR_CORR, label='Bias-Corrected')
axes[1].plot([df["true_t"].min(), df["true_t"].max()], [df["true_t"].min(), df["true_t"].max()], color='#27AE60', linestyle='--', linewidth=2, label='Perfect Calibration (1:1)')
axes[1].set_xlabel("Observed Temperature (°C)", fontsize=11, fontweight='bold')
axes[1].set_ylabel("Corrected Temperature (°C)", fontsize=11, fontweight='bold')
axes[1].set_title("Bias-Corrected Forecast vs Observations", fontsize=12, fontweight='bold', pad=10)
axes[1].grid(True, alpha=0.3, linestyle='--')
axes[1].legend()

plt.tight_layout()
plt.savefig(figures_dir / f"dashboard_temp_scatter_{STATION}.png", dpi=300, bbox_inches='tight')
plt.close()

# --- DASHBOARD 3: WIND SPEED SCATTER PLOT (1x2 Panel) ---
fig, axes = plt.subplots(1, 2, figsize=(16, 7.5))

r2_raw_w = r2_score(df["true_w"], df["raw_pred_w"])
mae_raw_w = mean_absolute_error(df["true_w"], df["raw_pred_w"])
rmse_raw_w = root_mean_squared_error(df["true_w"], df["raw_pred_w"])

r2_corr_w = r2_score(df["true_w"], df["corr_pred_w"])
mae_corr_w = mean_absolute_error(df["true_w"], df["corr_pred_w"])
rmse_corr_w = root_mean_squared_error(df["true_w"], df["corr_pred_w"])

fig.suptitle(
    f"Dashboard 3: 10m Wind Speed Scatter & Calibration (Out-of-Sample Years: {test_years_str}) - {STATION.upper()} STATION\n"
    f"Raw Model: R² = {r2_raw_w:.3f} | MAE = {mae_raw_w:.2f} m/s | RMSE = {rmse_raw_w:.2f} m/s    "
    f"Corrected: R² = {r2_corr_w:.3f} | MAE = {mae_corr_w:.2f} m/s | RMSE = {rmse_corr_w:.2f} m/s",
    fontsize=14, fontweight='bold', color='#2C3E50', y=0.96
)

# Panel 1: Raw Model
axes[0].scatter(df["true_w"], df["raw_pred_w"], alpha=0.3, color=COLOR_RAW, label='Raw Forecast')
axes[0].plot([df["true_w"].min(), df["true_w"].max()], [df["true_w"].min(), df["true_w"].max()], color='#27AE60', linestyle='--', linewidth=2, label='Perfect Calibration (1:1)')
axes[0].set_xlabel("Observed Wind Speed (m/s)", fontsize=11, fontweight='bold')
axes[0].set_ylabel("Forecasted Wind Speed (m/s)", fontsize=11, fontweight='bold')
axes[0].set_title("Raw Model Forecast vs Observations", fontsize=12, fontweight='bold', pad=10)
axes[0].grid(True, alpha=0.3, linestyle='--')
axes[0].legend()

# Panel 2: Corrected Model
axes[1].scatter(df["true_w"], df["corr_pred_w"], alpha=0.3, color=COLOR_CORR, label='Bias-Corrected')
axes[1].plot([df["true_w"].min(), df["true_w"].max()], [df["true_w"].min(), df["true_w"].max()], color='#27AE60', linestyle='--', linewidth=2, label='Perfect Calibration (1:1)')
axes[1].set_xlabel("Observed Wind Speed (m/s)", fontsize=11, fontweight='bold')
axes[1].set_ylabel("Corrected Wind Speed (m/s)", fontsize=11, fontweight='bold')
axes[1].set_title("Bias-Corrected Forecast vs Observations", fontsize=12, fontweight='bold', pad=10)
axes[1].grid(True, alpha=0.3, linestyle='--')
axes[1].legend()

plt.tight_layout()
plt.savefig(figures_dir / f"dashboard_wind_scatter_{STATION}.png", dpi=300, bbox_inches='tight')
plt.close()

# --- DASHBOARD 4: 72-HOUR STORM METEOROGRAM (1x2 Panel) ---
# Find a high wind speed event in the test set
storm_onset_idx = df["true_w"].idxmax()
start_plot = max(0, storm_onset_idx - 12)
end_plot = min(len(df), storm_onset_idx + 12)
storm_df = df.iloc[start_plot:end_plot]

fig, axes = plt.subplots(2, 1, figsize=(15, 10), sharex=True)
fig.suptitle(f"Dashboard 4: 72-Hour Severe Weather Meteorogram (Out-of-Sample Years: {test_years_str}) - {STATION.upper()} STATION", fontsize=15, fontweight='bold', color='#2C3E50', y=0.96)

# Panel 1: Temperature
axes[0].plot(storm_df["date"], storm_df["true_t"], 'k-o', color=COLOR_TRUTH, label='Observed', linewidth=2.5, markersize=5)
axes[0].plot(storm_df["date"], storm_df["raw_pred_t"], 'k--s', color=COLOR_RAW, label='Raw Forecast', linewidth=2)
axes[0].plot(storm_df["date"], storm_df["corr_pred_t"], 'r-d', color=COLOR_CORR, label='Bias-Corrected', linewidth=2.5, markersize=5)
axes[0].set_ylabel("2m Temperature (°C)", fontsize=11, fontweight='bold')
axes[0].set_title("Temperature Forecast Progression During Storm Event", fontsize=12, fontweight='bold')
axes[0].grid(True, alpha=0.3, linestyle='--')
axes[0].legend()

# Panel 2: Wind Speed
axes[1].plot(storm_df["date"], storm_df["true_w"], 'k-o', color=COLOR_TRUTH, label='Observed', linewidth=2.5, markersize=5)
axes[1].plot(storm_df["date"], storm_df["raw_pred_w"], 'k--s', color=COLOR_RAW, label='Raw Forecast', linewidth=2)
axes[1].plot(storm_df["date"], storm_df["corr_pred_w"], 'r-d', color=COLOR_CORR, label='Bias-Corrected', linewidth=2.5, markersize=5)
axes[1].set_ylabel("10m Wind Speed (m/s)", fontsize=11, fontweight='bold')
axes[1].set_title("Wind Speed Forecast Progression During Storm Event", fontsize=12, fontweight='bold')
axes[1].grid(True, alpha=0.3, linestyle='--')
axes[1].legend()

plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig(figures_dir / f"dashboard_storm_meteorogram_{STATION}.png", dpi=300, bbox_inches='tight')
plt.close()

# --- DASHBOARD 5: MONTHLY CLIMATOLOGY (1x2 Panel) ---
df["month"] = df["date"].dt.month
monthly_stats = df.groupby("month").mean(numeric_only=True).reset_index()

fig, axes = plt.subplots(1, 2, figsize=(16, 7.5))
fig.suptitle(f"Dashboard 5: Monthly Climatological Drift Analysis (Out-of-Sample Years: {test_years_str}) - {STATION.upper()} STATION", fontsize=15, fontweight='bold', color='#2C3E50', y=0.96)

# Panel 1: Temperature
axes[0].plot(monthly_stats["month"], monthly_stats["true_t"], 'k-o', color=COLOR_TRUTH, label='Observed', linewidth=2.5)
axes[0].plot(monthly_stats["month"], monthly_stats["raw_pred_t"], 'k--s', color=COLOR_RAW, label='Raw Forecast', linewidth=2)
axes[0].plot(monthly_stats["month"], monthly_stats["corr_pred_t"], 'r-d', color=COLOR_CORR, label='Bias-Corrected', linewidth=2.5)
axes[0].set_xlabel("Month", fontsize=11, fontweight='bold')
axes[0].set_ylabel("Mean Temperature (°C)", fontsize=11, fontweight='bold')
axes[0].set_title("Monthly Mean Temperature Climatology", fontsize=12, fontweight='bold')
axes[0].set_xticks(range(1, 13))
axes[0].set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
axes[0].grid(True, alpha=0.3, linestyle='--')
axes[0].legend()

# Panel 2: Wind Speed
axes[1].plot(monthly_stats["month"], monthly_stats["true_w"], 'k-o', color=COLOR_TRUTH, label='Observed', linewidth=2.5)
axes[1].plot(monthly_stats["month"], monthly_stats["raw_pred_w"], 'k--s', color=COLOR_RAW, label='Raw Forecast', linewidth=2)
axes[1].plot(monthly_stats["month"], monthly_stats["corr_pred_w"], 'r-d', color=COLOR_CORR, label='Bias-Corrected', linewidth=2.5)
axes[1].set_xlabel("Month", fontsize=11, fontweight='bold')
axes[1].set_ylabel("Mean Wind Speed (m/s)", fontsize=11, fontweight='bold')
axes[1].set_title("Monthly Mean Wind Speed Climatology", fontsize=12, fontweight='bold')
axes[1].set_xticks(range(1, 13))
axes[1].set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
axes[1].grid(True, alpha=0.3, linestyle='--')
axes[1].legend()

plt.tight_layout()
plt.savefig(figures_dir / f"dashboard_climatology_drift_{STATION}.png", dpi=300, bbox_inches='tight')
plt.close()

print(f"\nAll 4 dashboards generated and saved to: {figures_dir}")
print(f"Validation Metrics ({STATION.capitalize()}):")
print(f"  2m Temp: Raw R² = {r2_raw_t:.3f} --> Corrected R² = {r2_corr_t:.3f}")
print(f"  10m Wind: Raw R² = {r2_raw_w:.3f} --> Corrected R² = {r2_corr_w:.3f}")
