import numpy as np
import torch
from pathlib import Path

from model import FourCastNet
from dataset import ERA5Dataset

device = torch.device(
    "cuda" if torch.cuda.is_available()
    else "cpu"
)

print("Device:", device)

# Setup paths
base_dir = Path(__file__).parent.parent
data_dir = base_dir / "data"
checkpoint_dir = base_dir / "checkpoints"
figures_dir = base_dir / "figures"
figures_dir.mkdir(exist_ok=True)

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
else:
    print("Warning: Using non-normalized data")

dataset = ERA5Dataset(
    data,
    in_steps=8,
    out_steps=4,
    means=means,
    stds=stds,
    normalize=True
)

print("Samples:", len(dataset))

model = FourCastNet().to(device)

# Load model
model_path = checkpoint_dir / "best_model.pth"
if not model_path.exists():
    raise FileNotFoundError(
        f"Model file not found: {model_path}\n"
        f"Please train the model first using train.py"
    )

model.load_state_dict(
    torch.load(
        str(model_path),
        map_location=device
    )
)

model.eval()

print("Model Loaded")

# Get first sample
x, y = dataset[0]

x = x.unsqueeze(0).to(device)

with torch.no_grad():
    pred = model(x)

pred = pred.squeeze(0).cpu().numpy()

print("Prediction Shape:", pred.shape)

# Visualization
import matplotlib.pyplot as plt

step = 0
var = 2

fig, ax = plt.subplots(
    1,
    3,
    figsize=(15, 5)
)

ax[0].imshow(
    y[step, var],
    origin="lower",
    cmap="viridis"
)
ax[0].set_title("Ground Truth")
ax[0].colorbar = plt.colorbar(ax[0].images[0], ax=ax[0])

ax[1].imshow(
    pred[step, var],
    origin="lower",
    cmap="viridis"
)
ax[1].set_title("Prediction")
ax[1].colorbar = plt.colorbar(ax[1].images[0], ax=ax[1])

error = pred[step, var] - y[step, var]
ax[2].imshow(
    error,
    origin="lower",
    cmap="RdBu_r"
)
ax[2].set_title("Error")
ax[2].colorbar = plt.colorbar(ax[2].images[0], ax=ax[2])

plt.tight_layout()

output_path = figures_dir / "demo_forecast.png"
plt.savefig(
    str(output_path),
    dpi=300,
    bbox_inches="tight"
)

print(f"Forecast saved to: {output_path}")

plt.show()