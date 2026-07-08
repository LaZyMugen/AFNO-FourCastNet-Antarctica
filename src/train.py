import os
# Limit CPU resources to prevent thermal overheating
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
import time

# Force single-threaded CPU execution
torch.set_num_threads(1)

from model import FourCastNet
from dataset import ERA5Dataset
from config.config import *

# Setup device
device = torch.device("cpu")

print("Device:", device)

# Setup paths
base_dir = Path(__file__).parent.parent
data_dir = base_dir / "data"
checkpoint_dir = base_dir / "checkpoints" / STATION
checkpoint_dir.mkdir(parents=True, exist_ok=True)

data_path = base_dir / DATA_FILE
if not data_path.exists():
    raise FileNotFoundError(
        f"Data file not found: {data_path}\n"
        f"Please provide the data file in the project root"
    )

data = np.load(
    str(data_path),
    mmap_mode="r"
)

print("Dataset Shape:", data.shape)
print(f"Grid Resolution: {data.shape[2]} x {data.shape[3]}")
print(f"Variables: {data.shape[1]}")

_, _, IMG_H, IMG_W = data.shape

pad_h = (
    PATCH_SIZE -
    IMG_H % PATCH_SIZE
) % PATCH_SIZE

pad_w = (
    PATCH_SIZE -
    IMG_W % PATCH_SIZE
) % PATCH_SIZE

if pad_h > 0 or pad_w > 0:
    print(f"Padding dataset: H +{pad_h}, W +{pad_w}")
    data = np.pad(
        data,
        (
            (0, 0),
            (0, 0),
            (0, pad_h),
            (0, pad_w)
        ),
        mode="edge"
    )

print("Padded Shape:", data.shape)

# Create dataset and dataloader
# Note: The numpy files are already pre-normalized. We pass means=None, stds=None
# and set normalize=False to avoid double-normalization during training.
dataset = ERA5Dataset(
    data,
    in_steps=IN_STEPS,
    out_steps=OUT_STEPS,
    means=None,
    stds=None,
    normalize=False
)

print("Total Samples:", len(dataset))

# Split into train/val
train_size = int(0.8 * len(dataset))
val_size = len(dataset) - train_size

train_dataset, val_dataset = torch.utils.data.random_split(
    dataset,
    [train_size, val_size]
)

train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True,
    num_workers=0,
    pin_memory=torch.cuda.is_available()
)

val_loader = DataLoader(
    val_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=0,
    pin_memory=torch.cuda.is_available()
)

print(f"Train samples: {len(train_dataset)}, Val samples: {len(val_dataset)}")
print(f"Train batches: {len(train_loader)}, Val batches: {len(val_loader)}")

# Create model
model = FourCastNet(
    embed_dim=EMBED_DIM,
    depth=NUM_BLOCKS,
    mlp_ratio=MLP_RATIO
).to(device)

print("Model created")
print(f"Total parameters: {sum(p.numel() for p in model.parameters()):,}")

# Loss and optimizer
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(
    model.parameters(),
    lr=LEARNING_RATE,
    weight_decay=1e-5
)

scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
    optimizer,
    T_max=EPOCHS,
    alignment=1e-6 if hasattr(torch.optim.lr_scheduler.CosineAnnealingLR, 'alignment') else None
) if hasattr(torch.optim.lr_scheduler.CosineAnnealingLR, 'T_max') else torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS, eta_min=1e-6)

# Training function
def train_epoch(epoch):
    model.train()
    total_loss = 0
    
    for batch_idx, (x, y) in enumerate(train_loader):
        x = x.to(device)
        y = y.to(device)
        
        optimizer.zero_grad()
        
        pred = model(x)
        loss = criterion(pred, y)
        
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        
        total_loss += loss.item()
        
        if batch_idx % 100 == 0:  # Print every 100 batches on GPU
            print(
                f"Epoch {epoch}, Batch {batch_idx}/{len(train_loader)}, "
                f"Loss: {loss.item():.6f}"
            )
    
    avg_loss = total_loss / len(train_loader)
    return avg_loss


# Validation function
def validate(epoch):
    model.eval()
    total_loss = 0
    
    with torch.no_grad():
        for x, y in val_loader:
            x = x.to(device)
            y = y.to(device)
            
            pred = model(x)
            loss = criterion(pred, y)
            
            total_loss += loss.item()
    
    avg_loss = total_loss / len(val_loader)
    return avg_loss


# Visualization function for forecast
def visualize_variable_forecast(
    epoch,
    variable_idx,
    variable_name,
    sample_idx=0
):
    model.eval()
    x, y = dataset[sample_idx]

    with torch.no_grad():
        pred = model(
            x.unsqueeze(0).to(device)
        )

    pred = pred.squeeze(0).cpu().numpy()
    y = y.numpy()

    truth = y[0, variable_idx]
    forecast = pred[0, variable_idx]

    fig, axes = plt.subplots(
        1,
        3,
        figsize=(15, 5)
    )

    axes[0].imshow(
        truth,
        origin="lower",
        cmap="viridis"
    )
    axes[0].set_title(f"{variable_name} Truth")
    plt.colorbar(axes[0].images[0], ax=axes[0])

    axes[1].imshow(
        forecast,
        origin="lower",
        cmap="viridis"
    )
    axes[1].set_title(f"{variable_name} Forecast")
    plt.colorbar(axes[1].images[0], ax=axes[1])

    error = forecast - truth

    axes[2].imshow(
        error,
        origin="lower",
        cmap="RdBu_r"
    )
    axes[2].set_title(f"{variable_name} Error")
    plt.colorbar(axes[2].images[0], ax=axes[2])

    epoch_folder = (
        base_dir /
        "figures" /
        STATION /
        f"epoch_{epoch:03d}"
    )
    epoch_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    save_path = (
        epoch_folder /
        f"{variable_name.lower()}_forecast_{STATION}.png"
    )

    plt.tight_layout()
    plt.savefig(
        save_path,
        dpi=150,
        bbox_inches='tight'
    )
    plt.close()

    return save_path


def visualize_maitri_timeseries(
    epoch,
    variable_idx,
    variable_name,
    sample_idx=0
):
    model.eval()
    x, y = dataset[sample_idx]

    with torch.no_grad():
        pred = model(
            x.unsqueeze(0).to(device)
        )

    pred = pred.squeeze(0).cpu().numpy()
    y = y.numpy()

    H = pred.shape[-2]
    W = pred.shape[-1]

    # Plot at the station's grid cell
    station_y = GRID_LAT_IDX
    station_x = GRID_LON_IDX

    # Clip indices to grid boundaries just in case
    station_y = min(max(0, station_y), H - 1)
    station_x = min(max(0, station_x), W - 1)

    truth_series = y[:, variable_idx, station_y, station_x]
    pred_series = pred[:, variable_idx, station_y, station_x]

    plt.figure(figsize=(8, 5))
    plt.plot(truth_series, marker="o", label="Truth")
    plt.plot(pred_series, marker="s", label="Forecast")

    plt.xlabel("Forecast Step")
    plt.ylabel(variable_name)
    plt.title(f"{STATION.capitalize()} {variable_name} Time Series")
    plt.legend()
    plt.grid(True)

    epoch_folder = (
        base_dir /
        "figures" /
        STATION /
        f"epoch_{epoch:03d}"
    )
    epoch_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    save_path = (
        epoch_folder /
        f"{variable_name.lower()}_timeseries_{STATION}.png"
    )

    plt.savefig(
        save_path,
        dpi=150,
        bbox_inches='tight'
    )
    plt.close()

    return save_path


# Training loop
num_epochs = EPOCHS
best_val_loss = float('inf')
patience = 10
patience_counter = 0

# Track training history
train_losses = []
val_losses = []
epoch_list = []

for epoch in range(num_epochs):
    train_loss = train_epoch(epoch)
    val_loss = validate(epoch)
    
    scheduler.step()
    
    # Store history
    train_losses.append(train_loss)
    val_losses.append(val_loss)
    epoch_list.append(epoch)
    
    print(
        f"\nEpoch {epoch}: "
        f"Train Loss: {train_loss:.6f}, "
        f"Val Loss: {val_loss:.6f}, "
        f"LR: {optimizer.param_groups[0]['lr']:.2e}"
    )
    
    # Generate and save forecast visualization every epoch
    visualize_variable_forecast(epoch, T2M_IDX, "T2M")
    visualize_variable_forecast(epoch, MSL_IDX, "MSL")
    visualize_maitri_timeseries(epoch, T2M_IDX, "T2M")
    visualize_maitri_timeseries(epoch, MSL_IDX, "MSL")

    print(f"Saved 4 diagnostic figures for epoch {epoch}")
    
    # Save best model
    if val_loss < best_val_loss:
        best_val_loss = val_loss
        patience_counter = 0
        
        best_model_path = checkpoint_dir / f"best_model_{STATION}.pth"
        torch.save(
            {
                "model_state_dict": model.state_dict(),
                "config": {
                    "in_steps": IN_STEPS,
                    "out_steps": OUT_STEPS,
                    "embed_dim": EMBED_DIM,
                    "num_blocks": NUM_BLOCKS,
                    "patch_size": PATCH_SIZE
                },
                "best_val_loss": best_val_loss
            },
            str(best_model_path)
        )
        print(f"Model saved to {best_model_path}")
    else:
        patience_counter += 1
        if patience_counter >= patience:
            print(f"Early stopping at epoch {epoch}")
            break
            
    # Cooling break to keep CPU temperatures low and laptop responsive
    print("Cooling break: sleeping for 3 seconds...")
    time.sleep(3)

print(f"\nTraining completed. Best val loss: {best_val_loss:.6f}")

# Plot and save training history
fig, ax = plt.subplots(figsize=(12, 6))

ax.plot(epoch_list, train_losses, 'b-o', label='Train Loss', linewidth=2.5, markersize=6)
ax.plot(epoch_list, val_losses, 'r-s', label='Validation Loss', linewidth=2.5, markersize=6)
ax.set_xlabel('Epoch', fontsize=13, fontweight='bold')
ax.set_ylabel('Loss (MSE)', fontsize=13, fontweight='bold')
ax.set_title(f'FourCastNet Training History ({STATION.capitalize()})', fontsize=15, fontweight='bold')
ax.legend(fontsize=12, loc='upper right')
ax.grid(True, alpha=0.4, linestyle='--')

# Save training history plot
train_history_path = base_dir / "figures" / STATION / f"training_history_{STATION}.png"
train_history_path.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(str(train_history_path), dpi=300, bbox_inches='tight')
print(f"\nTraining history plot saved to: {train_history_path}")
plt.close()