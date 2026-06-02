# FourCastNet Setup and Usage Guide

## Overview
This guide explains how to run training and inference with the FourCastNet model.

## Prerequisites

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Prepare Data
You need to have `era5_processed.npy` in the project root directory. The expected shape is `(7304, 4, 120, 200)` representing:
- 7304 time steps
- 4 variables
- 120x200 spatial resolution

### 3. Normalization Statistics
Place `means.npy` and `stds.npy` in the `data/` folder for data normalization during training and inference.

These should have shape `(4, 120, 200)` to match the 4 variables and spatial dimensions.

## File Structure
```
AFNO-FourCastNet-Antarctica/
├── src/
│   ├── model.py          # FourCastNet model architecture
│   ├── dataset.py        # ERA5Dataset with normalization support
│   ├── train.py          # Training script
│   └── inference.py      # Inference script
├── data/
│   ├── means.npy         # Normalization statistics
│   └── stds.npy
├── checkpoints/
│   └── best_model.pth    # Trained model weights
├── figures/              # Output visualization directory
└── requirements.txt
```

## Usage

### Option 1: Run Training

From the `src/` directory:

```bash
cd src
python train.py
```

**What happens:**
1. Loads `era5_processed.npy` data (7304 samples, 4 variables, 120x200 spatial)
2. Normalizes data using `means.npy` and `stds.npy`
3. Splits data: 80% train, 20% validation
4. Creates DataLoaders with batch size 16
5. Trains FourCastNet for up to 100 epochs
6. Saves the best model to `checkpoints/best_model.pth`
7. Uses early stopping (patience=10 epochs)

**Training Parameters:**
- Batch size: 16
- Learning rate: 1e-3 (with cosine annealing)
- Input steps: 8 time steps
- Output steps: 4 time steps (forecast)
- Model depth: 6 AFNO blocks
- Embedding dimension: 128

### Option 2: Run Inference

From the `src/` directory:

```bash
cd src
python inference.py
```

**What happens:**
1. Loads the trained model from `checkpoints/best_model.pth`
2. Normalizes input data
3. Performs inference on the first sample
4. Generates visualization comparing:
   - Ground truth
   - Model prediction
   - Difference (error)
5. Saves visualization to `figures/demo_forecast.png`

## Key Fixes Applied

### 1. **model.py**
- Fixed indentation issue with `AFNO2D` class (was nested incorrectly in `PositionalEmbedding`)
- All model components are now properly structured

### 2. **dataset.py**
- Added normalization support via `means` and `stds` parameters
- Added proper dtype conversion to float32
- Added epsilon term in normalization to avoid division by zero

### 3. **train.py**
- Complete training pipeline from scratch
- Proper path handling using `pathlib.Path`
- Train/validation split with DataLoader
- Gradient clipping for stability
- Learning rate scheduling (Cosine Annealing)
- Best model checkpointing
- Early stopping mechanism
- Progress logging

### 4. **inference.py**
- Fixed relative path issues
- Proper error handling for missing files
- Normalization support
- Enhanced visualization with colorbars
- Proper file path resolution

## Expected Output

### Training Output:
```
Device: cpu
Dataset Shape: (7304, 4, 120, 200)
Loaded normalization statistics
Means shape: (4, 120, 200), Stds shape: (4, 120, 200)
Total Samples: 7292
Train samples: 5833, Val samples: 1459
Train batches: 365, Val batches: 92
Model created
Total parameters: XX,XXX,XXX

Epoch 0, Batch 0/365, Loss: X.XXXXXX
Epoch 0, Batch 10/365, Loss: X.XXXXXX
...
Epoch 0: Train Loss: X.XXXXXX, Val Loss: X.XXXXXX, LR: X.XXe-03
Model saved to checkpoints/best_model.pth
```

### Inference Output:
```
Device: cpu
Dataset Shape: (7304, 4, 120, 200)
Loaded normalization statistics
Samples: 7292
Model Loaded
Prediction Shape: (4, 4, 120, 200)
Forecast saved to: figures/demo_forecast.png
```

## Troubleshooting

### FileNotFoundError: Data file not found
- Ensure `era5_processed.npy` exists in the project root
- Check file path: `d:/AFNO-FourCastNet-Antarctica/era5_processed.npy`

### FileNotFoundError: Model file not found during inference
- Train the model first using `python train.py`
- Ensure `checkpoints/best_model.pth` exists

### Memory Issues
- Reduce batch size in `train.py` (line ~77): `batch_size=8` or `4`
- Use GPU if available for faster training

### Slow Training
- GPU acceleration: Ensure PyTorch is installed with CUDA support
- Check: `torch.cuda.is_available()` in Python

## Model Architecture Details

**FourCastNet** consists of:
1. **Patch Embedding**: Converts 8 input time steps × 4 variables (32 channels) into patches
2. **Positional Embedding**: Adds learnable positional information
3. **AFNO Blocks** (6 layers): Applies Adaptive Fourier Neural Operators
   - Fourier transform in spatial domain
   - Linear transformation in frequency space
   - Inverse Fourier transform
   - MLP layer
4. **Patch Recovery**: Reconstructs 4 output time steps with 4 variables each

**Input**: `(batch, 8, 4, 120, 200)` - 8 historical time steps
**Output**: `(batch, 4, 4, 120, 200)` - 4 forecast time steps

## Contact & Support
For issues or questions, refer to the repository documentation or research papers on FourCastNet.
