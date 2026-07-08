import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

import numpy as np
import torch
import pandas as pd
import datetime
from tqdm import tqdm
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score, mean_absolute_error
import joblib

from model import FourCastNet
from dataset import ERA5Dataset
from config.config import *

# Setup device
device = torch.device("cpu")
print("Device:", device)

# Setup paths
base_dir = Path(__file__).parent.parent
checkpoint_dir = base_dir / "checkpoints" / STATION
bias_corr_dir = checkpoint_dir / "bias_correction"
bias_corr_dir.mkdir(parents=True, exist_ok=True)

# Load data
data_path = base_dir / DATA_FILE
data = np.load(str(data_path), mmap_mode="r")
print(f"Dataset: {DATA_FILE}, Shape: {data.shape}")

# Load base model
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

# Helper to denormalize temperature to Celsius
def denorm_temp(t_norm):
    return (t_norm * TEMP_STD + TEMP_MEAN) - 273.15

# Helper to denormalize wind speed to m/s
def denorm_wind(u_norm, v_norm):
    u = u_norm * U_STD + U_MEAN
    v = v_norm * V_STD + V_MEAN
    return np.hypot(u, v)

# Helper to compute time features
def get_time_features(idx, station):
    start_year = 2017 if station == 'maitri' else 2016
    start_date = datetime.datetime(start_year, 1, 1, 0, 0, 0)
    
    current_date = start_date + datetime.timedelta(hours=int(idx) * TIME_INTERVAL_HOURS)
    
    # Day progress
    day_progress = current_date.hour / 24.0
    day_progress_sin = np.sin(2 * np.pi * day_progress)
    day_progress_cos = np.cos(2 * np.pi * day_progress)
    
    # Year progress
    year_progress = current_date.timetuple().tm_yday / 366.0
    year_progress_sin = np.sin(2 * np.pi * year_progress)
    year_progress_cos = np.cos(2 * np.pi * year_progress)
    
    return {
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

# Define train/test splits dynamically based on the station
start_year = 2017 if STATION == 'maitri' else 2016
if STATION == 'maitri':
    # Train bias corrector on Year 2024 (indices for 2024)
    train_start = get_index_for_date(2024, 1, 1, 0, 2017)
    train_end = get_index_for_date(2025, 1, 1, 0, 2017)
    # Test on Years 2025-2026 (remaining indices)
    test_start = get_index_for_date(2025, 1, 1, 0, 2017)
    test_end = len(data)
else:
    # Train bias corrector on Year 2023 (indices for 2023)
    train_start = get_index_for_date(2023, 1, 1, 0, 2016)
    train_end = get_index_for_date(2024, 1, 1, 0, 2016)
    # Test on Years 2024-2025 (remaining indices)
    test_start = get_index_for_date(2024, 1, 1, 0, 2016)
    test_end = len(data)

train_indices = np.arange(train_start, train_end - IN_STEPS - OUT_STEPS)
test_indices = np.arange(test_start, test_end - IN_STEPS - OUT_STEPS)
train_indices = train_indices[::4]  # Stride of 24 hours
test_indices = test_indices[::4]

def collect_forecasts(indices, desc):
    rows = []
    print(f"Collecting forecasts for {desc} ({len(indices)} samples)...")
    
    for idx in tqdm(indices):
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
            
            # Denormalize directly to physical space before fitting the corrector
            true_t = denorm_temp(y_st[step_idx, T2M_IDX])
            pred_t = denorm_temp(pred_st[step_idx, T2M_IDX])
            
            true_w = denorm_wind(y_st[step_idx, U10_IDX], y_st[step_idx, V10_IDX])
            pred_w = denorm_wind(pred_st[step_idx, U10_IDX], pred_st[step_idx, V10_IDX])
            
            row = {
                "lead_hours": lead_hours,
                "day_progress_sin": time_feats["day_progress_sin"],
                "day_progress_cos": time_feats["day_progress_cos"],
                "year_progress_sin": time_feats["year_progress_sin"],
                "year_progress_cos": time_feats["year_progress_cos"],
                "true_t2m": true_t,
                "pred_t2m": pred_t,
                "true_wind": true_w,
                "pred_wind": pred_w
            }
            rows.append(row)
            
    return pd.DataFrame(rows)

train_df = collect_forecasts(train_indices, "Train Set")
test_df = collect_forecasts(test_indices, "Test Set")

# Train Bias Correctors
features = ["lead_hours", "day_progress_sin", "day_progress_cos", "year_progress_sin", "year_progress_cos"]
correctors = {}

# 1. Temperature Bias Corrector (in Celsius)
print("\n--- Training Temperature Bias Corrector (Celsius) ---")
X_train_t = train_df[features + ["pred_t2m"]].values
y_train_t = train_df["true_t2m"].values
X_test_t = test_df[features + ["pred_t2m"]].values
y_test_t = test_df["true_t2m"].values

base_r2_t = r2_score(y_test_t, X_test_t[:, -1])
print(f"Raw Model Temperature R2: {base_r2_t:.4f}")

corr_t = Ridge(alpha=1.0)
corr_t.fit(X_train_t, y_train_t)
pred_corr_t = corr_t.predict(X_test_t)

corr_r2_t = r2_score(y_test_t, pred_corr_t)
print(f"Bias-Corrected Temperature R2: {corr_r2_t:.4f}")
correctors["t2m"] = corr_t

# 2. Wind Speed Bias Corrector (in m/s)
print("\n--- Training Wind Speed Bias Corrector (m/s) ---")
X_train_w = train_df[features + ["pred_wind"]].values
y_train_w = train_df["true_wind"].values
X_test_w = test_df[features + ["pred_wind"]].values
y_test_w = test_df["true_wind"].values

base_r2_w = r2_score(y_test_w, X_test_w[:, -1])
print(f"Raw Model Wind Speed R2: {base_r2_w:.4f}")

corr_w = Ridge(alpha=1.0)
corr_w.fit(X_train_w, y_train_w)
pred_corr_w = corr_w.predict(X_test_w)

corr_r2_w = r2_score(y_test_w, pred_corr_w)
print(f"Bias-Corrected Wind Speed R2: {corr_r2_w:.4f}")
correctors["wind"] = corr_w

# Save correctors
for name, model in correctors.items():
    path = bias_corr_dir / f"bias_corrector_{name}_{STATION}.pkl"
    joblib.dump(model, path)
    print(f"Saved {name} corrector to {path}")

print("\nBias correction training complete!")
