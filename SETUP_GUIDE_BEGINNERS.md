# 🌍 FourCastNet Setup Guide for Beginners

Complete step-by-step guide to set up, train, and run weather forecasting on Antarctica data.

---

## 📋 Table of Contents

1. [What You Need](#what-you-need)
2. [Installation Guide](#installation-guide)
3. [Data Setup](#data-setup)
4. [Understanding Requirements](#understanding-requirements)
5. [Training Your Model](#training-your-model)
6. [How the Model Works](#how-the-model-works)
7. [Viewing Results](#viewing-results)
8. [Stopping Training](#stopping-training)
9. [Retraining the Model](#retraining-the-model)
10. [Troubleshooting](#troubleshooting)

---

## What You Need

Before you start, make sure you have:

- **Computer:** Windows, macOS, or Linux
- **Python:** Version 3.8 or higher (check: `python --version`)
- **Internet:** For downloading packages (~1-2 GB)
- **Disk Space:** At least 15 GB free
- **Time:** 30 minutes for setup + 10-30 minutes for training

**Check your Python version:**
```bash
python --version
# Should show: Python 3.8 or higher
```

---

## Installation Guide

### **Step 1: Download the Repository**

This contains all the code and configuration files you need.

```bash
# Copy this into your terminal/command prompt
git clone https://github.com/LaZyMugen/AFNO-FourCastNet-Antarctica.git
cd AFNO-FourCastNet-Antarctica
```

**What this does:**
- Downloads the entire project to your computer
- `cd` enters the project folder

### **Step 2: Create a Virtual Environment** ✅ (IMPORTANT!)

A virtual environment is like a separate workspace for this project. It keeps dependencies organized.

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

**How to know it worked:**
- You should see `(venv)` at the start of your command prompt/terminal
- Example: `(venv) C:\Users\YourName\AFNO-FourCastNet-Antarctica>`

### **Step 3: Install All Required Packages**

This command downloads and installs everything the project needs.

```bash
pip install -r requirements.txt
```

⏱️ **This will take 2-5 minutes** depending on your internet speed. You'll see text scrolling as packages download.

---

## Understanding Requirements

The `requirements.txt` file lists what gets downloaded. Here's what each package does:

### **Main Packages You're Installing:**

| Package | Size | Purpose |
|---------|------|---------|
| **torch** | 500 MB - 2 GB | The AI framework (the "brain" of the model) |
| **numpy** | 50-100 MB | Math library for working with data |
| **matplotlib** | 100-150 MB | Makes graphs and charts of results |
| **xarray** | 30-50 MB | Handles multi-dimensional data |
| **netCDF4** | 20-30 MB | Reads weather data files |
| **jupyter** | 200-300 MB | Interactive notebooks for experimenting |

### **Total Download: ~900 MB to 2.5 GB**

**Why is PyTorch so big?**
- It includes GPU acceleration libraries (NVIDIA CUDA, cuDNN)
- These are needed for fast training (if you have a GPU)
- If you DON'T have a GPU, it still downloads them but just won't use them

**What takes the longest?**
- **torch** (largest package)
- **jupyter** (many dependencies)

**To see what will be downloaded without installing:**
```bash
pip install --dry-run -r requirements.txt
```

---

## Data Setup

### **Download the ERA5 Dataset**

The dataset is too large to include in the repository, so you download it separately.

**Step 1: Open the Google Drive Link**

Click this link (or copy-paste into your browser):
```
https://drive.google.com/file/d/1sf2_rbjG--i7GF1tCkc6BCD4Chd35Ikm/view?usp=drive_link
```

**Step 2: Download the File**
- Click the **Download** button (arrow icon in top right)
- The file is named: `era5_processed.npy`
- File size: **~2.8 GB** (will take 5-15 minutes to download)

**Step 3: Place File in Project Root**

Move the downloaded file to your project folder:

```
AFNO-FourCastNet-Antarctica/
├── era5_processed.npy          ← Put the file HERE
├── data/
│   ├── means.npy               (already in repo)
│   └── stds.npy                (already in repo)
├── src/
├── checkpoints/
└── ...
```

**How to do this:**
1. Open File Explorer / Finder
2. Navigate to your project folder
3. Paste `era5_processed.npy` in the root folder

**Verify it's correct:**
```bash
# Run this in your terminal (in the project folder)
python verify_setup.py
```

You should see:
```
✓ All checks passed!
```

---

## Training Your Model

### **Step 1: Navigate to Source Code**

```bash
cd src
```

### **Step 2: Start Training**

```bash
python train.py
```

**You should see output like:**
```
Device: cpu
Dataset Shape: (7304, 4, 120, 200)
Loaded normalization statistics
Total Samples: 7292

Epoch 0: Train Loss: 0.123456, Val Loss: 0.125432
Epoch 1: Train Loss: 0.098765, Val Loss: 0.102345
Epoch 2: Train Loss: 0.087654, Val Loss: 0.091234
...
```

**What's happening:**
- **Device:** Shows if using CPU or GPU
- **Dataset Shape:** (7304 timesteps, 4 variables, 120×200 spatial grid)
- **Epoch:** One complete cycle through training data
- **Train Loss:** Error on training data (should decrease)
- **Val Loss:** Error on validation data (should decrease)

---

## How the Model Works

### **Simple Explanation** 🧠

The model learns to predict weather 24 hours into the future using:

**Input:** 48 hours of past weather data (8 timesteps × 6-hour intervals)
```
Past: [←48 hours of weather→]
```

**Output:** 24-hour weather forecast (4 timesteps × 6-hour intervals)
```
Future: [→24 hours forecast→]
```

### **Model Architecture**

```
Input Data (Temperature, U-wind, V-wind, Pressure)
    ↓
Split into patches
    ↓
Add positional info (where in space/time)
    ↓
6 Transformer blocks (learning patterns)
    ↓
Combine patches back together
    ↓
Output Forecast
```

### **How Loss Is Calculated** 📊

**Loss = How wrong the prediction is**

The model compares:
- **Predicted values:** What the model thinks the weather will be
- **Actual values:** What the weather really was

```
Loss = Average of (Prediction - Actual)²

Smaller loss = Better prediction
```

**Example:**
- Actual temperature: 10°C
- Predicted temperature: 12°C
- Error: 2°C
- Squared error: 4

The model tries to minimize this by adjusting its internal weights during training.

### **Training Loop Visualization**

```
For each epoch:
  1. Load batch of training data
  2. Feed through model → Get prediction
  3. Compare to actual → Calculate loss
  4. Adjust weights to reduce loss (backpropagation)
  5. Repeat for all batches
  
  Then:
  6. Validate on unseen data
  7. If validation loss improved → Save model
  8. If no improvement for 10 epochs → Stop
```

---

## Viewing Results

### **Where Are the Images?**

After training, visualizations are saved here:

```
figures/
├── training_history.png           ← Loss curves
├── demo_forecast.png              ← Final example
├── epoch_000/
│   └── forecast_comparison.png    ← Epoch 0 results
├── epoch_001/
│   └── forecast_comparison.png    ← Epoch 1 results
└── epoch_NNN/
    └── forecast_comparison.png    ← Last epoch results
```

### **What Each Image Shows**

**training_history.png:**
- Two lines: one for training loss, one for validation loss
- Should both go down over time
- Shows if model is learning

**forecast_comparison.png (per epoch):**
- Three columns showing 3 weather variables:
  - **Left (Truth):** Actual weather from dataset
  - **Middle (Prediction):** What model predicted
  - **Right (Error):** Difference between them
- Darker colors = larger errors
- Compare early epochs (high error) vs late epochs (low error)

### **How to View Images**

**Method 1: VS Code (Easiest)**
1. Open Explorer (Ctrl+Shift+E)
2. Navigate to `figures/` folder
3. Click any `.png` file to preview

**Method 2: File Explorer**
1. Open File Explorer / Finder
2. Go to project folder
3. Open `figures/` folder
4. Double-click image to view

**Method 3: Python Script**
```python
from PIL import Image
import matplotlib.pyplot as plt

img = Image.open('../figures/training_history.png')
plt.imshow(img)
plt.axis('off')
plt.show()
```

---

## Stopping Training

### **While Training Is Running**

Press **Ctrl+C** in your terminal:

```bash
Epoch 5: Train Loss: 0.045632, Val Loss: 0.048921
Epoch 6: Train Loss: 0.042187, Val Loss: 0.045123
^C  # ← Press Ctrl+C here to stop
KeyboardInterrupt
```

The model saves the best checkpoint automatically, so you won't lose progress.

### **After Stopping**

Your terminal will return to normal prompt:
```bash
(venv) C:\...\src>
```

The **best model is saved** in:
```
checkpoints/best_model.pth
```

---

## Retraining the Model

### **Scenario 1: Continue Training from Last Checkpoint**

If you want to keep improving the model:

```bash
# Just run train.py again
python train.py
```

**What happens:**
- Loads the best saved model
- Continues training from where it left off
- May improve further or stop early if no improvement

### **Scenario 2: Start Fresh (Train from Scratch)**

Delete the checkpoint and retrain:

```bash
# Delete old model
rm ../checkpoints/best_model.pth

# Or on Windows:
del ..\checkpoints\best_model.pth

# Then retrain
python train.py
```

**Why retrain?**
- Try different settings (batch_size, learning_rate)
- Better initialization
- Different random seed

### **Changing Training Settings**

Edit `train.py` to adjust:

```python
# Around line 10-20 in train.py:

epochs = 20              # How many times to go through data
batch_size = 16          # How many samples per batch
learning_rate = 1e-3     # How fast to learn
patience = 10            # Epochs without improvement before stopping
```

**Common adjustments:**

| Issue | Change |
|-------|--------|
| Training too slow | Increase `batch_size` to 32 |
| Out of memory | Decrease `batch_size` to 8 |
| Not learning | Decrease `learning_rate` to 5e-4 |
| Stops too early | Increase `patience` to 20 |

---

## Running Inference

### **Make Predictions on New Data**

After training, you can use the model to forecast:

```bash
cd src
python inference.py
```

**Output:**
```
Model Loaded
Prediction Shape: (4, 4, 120, 200)
Forecast saved to: figures/demo_forecast.png
```

**What this does:**
1. Loads the best trained model
2. Takes first sample from dataset
3. Predicts 24-hour forecast
4. Creates visualization comparing truth vs prediction

**Result:**
- Check `figures/demo_forecast.png` for the comparison

---

## Detailed Step-by-Step Walkthrough

### **Complete From-Scratch Setup (5 minutes)**

```bash
# 1. Clone project
git clone https://github.com/LaZyMugen/AFNO-FourCastNet-Antarctica.git
cd AFNO-FourCastNet-Antarctica

# 2. Create virtual environment
python -m venv venv

# 3. Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install packages (this takes 2-5 minutes)
pip install -r requirements.txt

# 5. Verify setup worked
python verify_setup.py
# Should see: ✓ All checks passed!
```

### **Download and Setup Data (15 minutes)**

1. Go to: https://drive.google.com/file/d/1sf2_rbjG--i7GF1tCkc6BCD4Chd35Ikm/view?usp=drive_link
2. Click **Download** button
3. Wait for `era5_processed.npy` (2.8 GB)
4. Move file to project root folder
5. Verify with `python verify_setup.py`

### **Train Model (10-30 minutes)**

```bash
cd src
python train.py

# You'll see:
# Epoch 0: Train Loss: X.XXX, Val Loss: X.XXX
# Epoch 1: Train Loss: X.XXX, Val Loss: X.XXX
# ... continues ...
```

### **View Results Immediately**

```bash
# While training, open in another terminal:
cd figures
# Look for epoch_000/forecast_comparison.png
```

### **Stop Training**

Press **Ctrl+C** in terminal (safe to do anytime)

### **Run Inference**

```bash
python inference.py
# Check figures/demo_forecast.png
```

---

## Troubleshooting

### **"ModuleNotFoundError: No module named 'torch'"**

**Problem:** Package not installed

**Solution:**
```bash
# Make sure virtual environment is activated
# You should see (venv) at start of prompt
python -m pip install torch numpy matplotlib xarray netCDF4 jupyter
```

### **"FileNotFoundError: era5_processed.npy"**

**Problem:** Dataset not in project root

**Solution:**
1. Download from: https://drive.google.com/file/d/1sf2_rbjG--i7GF1tCkc6BCD4Chd35Ikm/view?usp=drive_link
2. Make sure file is in: `AFNO-FourCastNet-Antarctica/era5_processed.npy`
3. Run `python verify_setup.py` to confirm

### **"CUDA out of memory"**

**Problem:** Your GPU doesn't have enough memory

**Solution:**
1. Edit `src/train.py`
2. Find: `batch_size = 16`
3. Change to: `batch_size = 8`

### **Training is very slow**

**Problem:** Using CPU instead of GPU

**Solution:**
- GPU training is automatic (if available)
- CPU training is slow but works fine
- To use GPU, install: `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118`

### **No images generated after training**

**Problem:** Matplotlib can't display (headless environment)

**Solution:**
- Images still save to `figures/` folder
- Open them manually in file explorer
- Or check the terminal output for file paths

### **"ConnectionError: Max retries exceeded"**

**Problem:** Internet connection issue during download

**Solution:**
```bash
# Try again (pip will resume)
pip install -r requirements.txt

# Or specify timeout
pip install --default-timeout=1000 -r requirements.txt
```

---

## Quick Reference

### **Common Commands**

```bash
# Activate virtual environment
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS/Linux

# Check setup
python verify_setup.py

# Train
cd src
python train.py

# Inference
python inference.py

# Exit virtual environment
deactivate
```

### **File Locations**

| Item | Location |
|------|----------|
| Project folder | `AFNO-FourCastNet-Antarctica/` |
| Python files | `src/` |
| Training data | `era5_processed.npy` (root) |
| Trained model | `checkpoints/best_model.pth` |
| Images | `figures/` |
| Logs | Console output |

### **Important Files**

| File | Purpose |
|------|---------|
| `train.py` | Training script |
| `inference.py` | Make predictions |
| `model.py` | Neural network definition |
| `dataset.py` | Data loading |
| `requirements.txt` | Package list |

---

## Getting Help

If something doesn't work:

1. **Check error message** in terminal
2. **Search troubleshooting section** above
3. **Run verification:**
   ```bash
   python verify_setup.py
   ```
4. **Check file locations** exist and are correct
5. **Restart terminal** and reactivate virtual environment

---

## Summary

✅ **You now know:**
- How to install everything
- What gets downloaded and why
- How to download the dataset
- How to train the model
- How loss is calculated
- Where results are saved
- How to stop and retrain
- Common troubleshooting

🚀 **Next steps:**
1. Clone the repository
2. Create virtual environment
3. Install requirements
4. Download ERA5 data
5. Run training
6. View results!

---

**Happy forecasting! 🌍📊**
