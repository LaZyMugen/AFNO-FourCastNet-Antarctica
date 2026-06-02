import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import os
from pathlib import Path

from model import FourCastNet
from dataset import ERA5Dataset

# Setup device
device = torch.device(
    "cuda" if torch.cuda.is_available()
    else "cpu"
)

print("Device:", device)

# Setup paths
base_dir = Path(__file__).parent.parent
data_dir = base_dir / "data"
checkpoint_dir = base_dir / "checkpoints"
checkpoint_dir.mkdir(exist_ok=True)

# Load data
data_path = base_dir / "era5_processed.npy"
if not data_path.exists():
    raise FileNotFoundError(
        f"Data file not found: {data_path}\n"
        f"Please provide era5_processed.npy in the project root"
    )

data = np.load(
    str(data_path),
    mmap_mode="r"
)

print("Dataset Shape:", data.shape)

# Load normalization statistics
means_path = data_dir / "means.npy"
stds_path = data_dir / "stds.npy"

means = None
stds = None

if means_path.exists() and stds_path.exists():
    means = np.load(str(means_path))
    stds = np.load(str(stds_path))
    print("Loaded normalization statistics")
    print(f"Means shape: {means.shape}, Stds shape: {stds.shape}")
else:
    print("Warning: Normalization statistics not found")

# Create dataset and dataloader
dataset = ERA5Dataset(
    data,
    in_steps=8,
    out_steps=4,
    means=means,
    stds=stds,
    normalize=True
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
    batch_size=16,
    shuffle=True,
    num_workers=0,
    pin_memory=torch.cuda.is_available()
)

val_loader = DataLoader(
    val_dataset,
    batch_size=16,
    shuffle=False,
    num_workers=0,
    pin_memory=torch.cuda.is_available()
)

print(f"Train samples: {len(train_dataset)}, Val samples: {len(val_dataset)}")
print(f"Train batches: {len(train_loader)}, Val batches: {len(val_loader)}")

# Create model
model = FourCastNet(
    embed_dim=128,
    depth=6,
    mlp_ratio=4
).to(device)

print("Model created")
print(f"Total parameters: {sum(p.numel() for p in model.parameters()):,}")

# Loss and optimizer
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(
    model.parameters(),
    lr=1e-3,
    weight_decay=1e-5
)

scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
    optimizer,
    T_max=100,
    eta_min=1e-6
)

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
        
        if batch_idx % 10 == 0:
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
def visualize_forecast(epoch, sample_idx=0):
    """Generate and save forecast visualization for a sample"""
    model.eval()
    
    x, y = dataset[sample_idx]
    x_batch = x.unsqueeze(0).to(device)
    
    with torch.no_grad():
        pred = model(x_batch)
    
    pred = pred.squeeze(0).cpu().numpy()
    y = y.numpy() if isinstance(y, torch.Tensor) else y
    
    # Save 3 variables
    num_vars = min(3, pred.shape[1])
    
    fig, axes = plt.subplots(num_vars, 3, figsize=(15, 4 * num_vars))
    
    if num_vars == 1:
        axes = axes.reshape(1, -1)
    
    for var_idx in range(num_vars):
        # Ground truth
        axes[var_idx, 0].imshow(
            y[0, var_idx],
            origin="lower",
            cmap="viridis"
        )
        axes[var_idx, 0].set_title(f"Ground Truth - Var {var_idx}", fontsize=11, fontweight='bold')
        axes[var_idx, 0].colorbar = plt.colorbar(axes[var_idx, 0].images[0], ax=axes[var_idx, 0])
        
        # Prediction
        axes[var_idx, 1].imshow(
            pred[0, var_idx],
            origin="lower",
            cmap="viridis"
        )
        axes[var_idx, 1].set_title(f"Prediction - Var {var_idx}", fontsize=11, fontweight='bold')
        axes[var_idx, 1].colorbar = plt.colorbar(axes[var_idx, 1].images[0], ax=axes[var_idx, 1])
        
        # Error
        error = pred[0, var_idx] - y[0, var_idx]
        axes[var_idx, 2].imshow(
            error,
            origin="lower",
            cmap="RdBu_r"
        )
        axes[var_idx, 2].set_title(f"Error - Var {var_idx}", fontsize=11, fontweight='bold')
        axes[var_idx, 2].colorbar = plt.colorbar(axes[var_idx, 2].images[0], ax=axes[var_idx, 2])
    
    plt.suptitle(f'Epoch {epoch}: Forecast Comparison (First {num_vars} Variables)', 
                 fontsize=14, fontweight='bold', y=1.00)
    plt.tight_layout()
    
    # Save in epoch folder
    epoch_folder = base_dir / "figures" / f"epoch_{epoch:03d}"
    epoch_folder.mkdir(parents=True, exist_ok=True)
    
    save_path = epoch_folder / "forecast_comparison.png"
    plt.savefig(str(save_path), dpi=200, bbox_inches='tight')
    plt.close()
    
    return save_path


# Training loop
num_epochs = 20
best_val_loss = float('inf')
patience = 10
patience_counter = 0

# Track training history
train_losses = []
val_losses = []
epoch_list = []

import matplotlib.pyplot as plt

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
    try:
        forecast_path = visualize_forecast(epoch, sample_idx=0)
        print(f"Forecast graph saved to: {forecast_path}")
    except Exception as e:
        print(f"Warning: Could not save forecast visualization: {e}")
    
    # Save best model
    if val_loss < best_val_loss:
        best_val_loss = val_loss
        patience_counter = 0
        
        best_model_path = checkpoint_dir / "best_model.pth"
        torch.save(
            model.state_dict(),
            str(best_model_path)
        )
        print(f"Model saved to {best_model_path}")
    else:
        patience_counter += 1
        if patience_counter >= patience:
            print(f"Early stopping at epoch {epoch}")
            break

print(f"\nTraining completed. Best val loss: {best_val_loss:.6f}")

# Plot and save training history
fig, ax = plt.subplots(figsize=(12, 6))

ax.plot(epoch_list, train_losses, 'b-o', label='Train Loss', linewidth=2.5, markersize=6)
ax.plot(epoch_list, val_losses, 'r-s', label='Validation Loss', linewidth=2.5, markersize=6)
ax.set_xlabel('Epoch', fontsize=13, fontweight='bold')
ax.set_ylabel('Loss (MSE)', fontsize=13, fontweight='bold')
ax.set_title('FourCastNet Training History', fontsize=15, fontweight='bold')
ax.legend(fontsize=12, loc='upper right')
ax.grid(True, alpha=0.4, linestyle='--')

# Save training history plot
train_history_path = base_dir / "figures" / "training_history.png"
train_history_path.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(str(train_history_path), dpi=300, bbox_inches='tight')
print(f"\nTraining history plot saved to: {train_history_path}")

plt.show()