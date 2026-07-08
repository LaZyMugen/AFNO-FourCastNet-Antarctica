# 🌍 MAITRI Data Preprocessing Guide

Complete guide to convert GRIB files to normalized numpy arrays for FourCastNet training.

---

## 📋 Quick Overview

### What This Does

```
GRIB Files (from CDN)
    ↓
Read 4 variables (T, U, V, Z)
    ↓
Stack into channels
    ↓
Compute mean/std
    ↓
Normalize
    ↓
Save as .npy files
    ↓
Ready for FourCastNet training
```

### What You Need

- GRIB files downloaded from CDN (placed in `data/raw/`)
- Python with `xarray` and `cfgrib` installed
- ~20-30 GB disk space (raw + processed)
- ~30-60 minutes processing time

---

## 📁 Directory Structure

Create this structure before preprocessing:

```
AFNO-FourCastNet-Antarctica/
│
├── data/
│   ├── raw/                          ← Your GRIB files go here
│   │   ├── maitri_2016.grib
│   │   ├── maitri_2017.grib
│   │   ├── maitri_2018.grib
│   │   ├── maitri_2019.grib
│   │   ├── maitri_2020.grib
│   │   └── maitri_2021.grib
│   │
│   └── processed/                    ← Output files generated here
│       ├── era5_maitri.npy          (main data)
│       ├── mean.npy                 (normalization mean)
│       └── std.npy                  (normalization std)
│
├── preprocessing_maitry.py           (the script)
├── src/
│   ├── train.py
│   ├── model.py
│   └── dataset.py
└── ...
```

### Create Directories

```bash
mkdir -p data/raw
mkdir -p data/processed
```

---

## 🚀 Step-by-Step Guide

### Step 1: Download GRIB Files

Download all GRIB files from your CDN and place in `data/raw/`:

```bash
# Example structure after download:
data/
└── raw/
    ├── maitri_2016.grib    (~2-3 GB each)
    ├── maitri_2017.grib
    ├── maitri_2018.grib
    ├── maitri_2019.grib
    ├── maitri_2020.grib
    └── maitri_2021.grib
```

**Total size:** ~15-18 GB

### Step 2: Verify GRIB Files

Check files are readable:

```bash
# Windows
dir data\raw\

# macOS/Linux
ls -lh data/raw/
```

Should show all `.grib` files with correct sizes.

### Step 3: Install Required Packages

Make sure you have `cfgrib` (GRIB reader):

```bash
# Activate virtual environment first!
pip install cfgrib xarray

# Or add to requirements.txt and reinstall
pip install -r requirements.txt
```

### Step 4: Run Preprocessing

```bash
python preprocessing_maitry.py
```

### Step 5: Monitor Output

You'll see detailed progress:

```
======================================================================
🌍 FourCastNet MAITRI Data Preprocessing Pipeline
======================================================================

[Step 1/6] Finding GRIB files...
✓ Found 6 GRIB files:
    - maitri_2016.grib
    - maitri_2017.grib
    - maitri_2018.grib
    - maitri_2019.grib
    - maitri_2020.grib
    - maitri_2021.grib

[Step 2/6] Loading and extracting variables...
📖 Loading: maitri_2016.grib
   File loaded. Available variables: ['t', 'u', 'v', 'z', ...]
   ✓ Extracted 't' (shape: (8760, 120, 200))
   ✓ Extracted 'u' (shape: (8760, 120, 200))
   ✓ Extracted 'v' (shape: (8760, 120, 200))
   ✓ Extracted 'z' (shape: (8760, 120, 200))

[Step 3/6] Stacking variables into channels...
📚 Stacking variables into channels...
   File 1: Stacked shape (8760, 4, 120, 200)
   File 2: Stacked shape (8760, 4, 120, 200)
   ...
   ✓ Total concatenated shape: (52560, 4, 120, 200)

[Step 4/6] Validating data...
🔍 Validating data...
   Data range: [-50.5234, 128.3456]
   Data mean: 23.4567
   Data std: 15.6789
   ✓ Data validation passed

[Step 5/6] Computing normalization statistics...
📊 Computing normalization statistics...
   Channel means: [280.34 5.23 -2.15 50234.5]
   Channel stds: [12.45 8.34 7.92 1234.6]
   ✓ Statistics computed

[Step 6/6] Normalizing data...
🔧 Normalizing data...
   Normalized range: [-4.2342, 3.8923]
   Normalized mean (should be ~0): -0.000021
   Normalized std (should be ~1): 1.000001
   ✓ Data normalized

[Step 7/7] Saving processed files...
💾 Saving files...
   ✓ Data saved: data/processed/era5_maitri.npy
     Size: 8.24 GB
   ✓ Mean saved: data/processed/mean.npy
     Shape: (4,)
   ✓ Std saved: data/processed/std.npy
     Shape: (4,)

======================================================================
✅ PREPROCESSING COMPLETE
======================================================================
```

---

## 🔍 Understanding Each Step

### Step 1: Find GRIB Files

**What:** Locates all `.grib` files in `data/raw/`

**Why:** Automatic file discovery so you don't have to hardcode filenames

**Error if:** No `.grib` files found
```
FileNotFoundError: No GRIB files found in data/raw/
Expected: data/raw/*.grib
```

**Fix:** Make sure GRIB files are in the right folder with `.grib` extension

---

### Step 2: Extract Variables

**What:** Reads each GRIB file and extracts 4 weather variables:

| Variable | Full Name | Unit | Range |
|----------|-----------|------|-------|
| **T** | Temperature (2m) | Kelvin (K) | 250-310 K |
| **U** | U-wind (10m) | m/s | -20 to +20 |
| **V** | V-wind (10m) | m/s | -20 to +20 |
| **Z** | Geopotential Height | m²/s² | 45000-55000 |

**Why 4 variables?**
- Different scales → normalization needed
- Core weather variables
- Enough complexity for meaningful predictions

**Input shape per variable:** `(time, lat, lon)`
- Example: `(8760, 120, 200)` = 1 year × 120×200 spatial grid

**Error handling:** If a variable is missing, warning printed but processing continues

---

### Step 3: Stack Into Channels

**Before (separate arrays):**
```
Temperature: (52560, 120, 200)
U-wind:      (52560, 120, 200)
V-wind:      (52560, 120, 200)
Geopotential:(52560, 120, 200)
```

**After (4-channel array):**
```
Data: (52560, 4, 120, 200)
      time, channels, height, width
```

**Why this format?**
- Standard for deep learning (like RGB images: height, width, 3 channels)
- Compatible with convolutional neural networks
- FourCastNet expects this format

---

### Step 4: Validate Data

**Checks:**
- ✓ No NaN (missing) values
- ✓ No infinite values
- ✓ Reasonable ranges

**Output example:**
```
Data range: [-50.5234, 128.3456]
Data mean: 23.4567
Data std: 15.6789
```

**Why validate?**
- Catches corrupted files early
- Prevents silent errors in training
- Confirms data integrity

---

### Step 5: Compute Statistics

**Formula:**
```
mean = data.mean(axis=(0, 2, 3))
std  = data.std(axis=(0, 2, 3))
```

**Translation:**
- Average over: time (0), latitude (2), longitude (3)
- Keep separate: channels (1)
- Result: One mean & std value per channel

**Example output:**
```
Channel means: [280.34  5.23  -2.15  50234.5]
               [  T    U     V      Z      ]
               
Channel stds:  [12.45  8.34  7.92  1234.6]
```

**Why per-channel?**
- Each variable has different natural scale
- T: 250-310 K (small range)
- Z: 45000-55000 m²/s² (huge range)
- Separate statistics treat each fairly

**Shape result:** `(4,)` - one value per channel

---

### Step 6: Normalize Data

**Formula:**
```
normalized = (data - mean) / (std + epsilon)

epsilon = 1e-6 (prevents division by zero)
```

**Broadcasting example:**
```
Data shape:        (52560, 4, 120, 200)  time × channels × lat × lon
Mean reshaped:     (1, 4, 1, 1)          broadcast to match
Normalized shape:  (52560, 4, 120, 200)
```

**Result:**
- Mean ≈ 0.0
- Std ≈ 1.0
- Range ≈ [-5, +5]

**Why normalize?**
- Neural networks train faster with normalized data
- Prevents exploding/vanishing gradients
- Fair treatment of different variable scales

**Check in output:**
```
Normalized mean (should be ~0): -0.000021  ✓ Good!
Normalized std (should be ~1):  1.000001   ✓ Good!
```

---

### Step 7: Save Files

Three files saved to `data/processed/`:

**1. era5_maitri.npy** (Main data)
```
Shape:  (52560, 4, 120, 200)
Size:   ~8 GB
Format: Float32
```

**2. mean.npy** (Normalization mean)
```
Shape:  (4,)
Data:   [280.34  5.23  -2.15  50234.5]
```

**3. std.npy** (Normalization std)
```
Shape:  (4,)
Data:   [12.45  8.34  7.92  1234.6]
```

**Why save separately?**
- Data loaded into memory for training
- Mean/Std used by `ERA5Dataset` to denormalize predictions
- Can verify statistics without loading full dataset

---

## 📊 Data Shapes & Sizes

### Before Processing

```
6 GRIB files × ~3 GB each = ~18 GB raw data
```

### After Processing

```
era5_maitri.npy:  (52560, 4, 120, 200) × 4 bytes = ~8.2 GB
mean.npy:         (4,) × 4 bytes = negligible
std.npy:          (4,) × 4 bytes = negligible
```

### Breakdown

```
52560 timesteps = 6 years × 365.25 days × 24 hours / 6-hour intervals
4 channels = Temperature, U-wind, V-wind, Geopotential
120 × 200 = Spatial grid resolution (varies by data source)
```

---

## 🔧 Using Processed Data for Training

### Update train.py

Change the data loading line:

**Before:**
```python
data_path = base_dir / "era5_processed.npy"
```

**After:**
```python
data_path = base_dir / "data" / "processed" / "era5_maitri.npy"
```

And update normalization loading:

```python
means_path = data_dir / "processed" / "mean.npy"
stds_path = data_dir / "processed" / "std.npy"
```

### Start Training

```bash
cd src
python train.py
```

The dataset will:
1. Load era5_maitri.npy (all data)
2. Load mean.npy & std.npy (statistics)
3. Create sliding windows (8 timesteps in, 4 out)
4. Normalize using loaded statistics
5. Feed to FourCastNet

---

## ⚠️ Troubleshooting

### "FileNotFoundError: No GRIB files found"

**Problem:** GRIB files not in correct location

**Fix:**
```bash
# Verify files exist
ls -lh data/raw/

# Files must have .grib extension
# Rename if needed (e.g., maitri_2016 → maitri_2016.grib)
```

### "ModuleNotFoundError: No module named 'cfgrib'"

**Problem:** cfgrib not installed

**Fix:**
```bash
pip install cfgrib xarray
# On some systems may need: conda install cfgrib
```

### "MemoryError"

**Problem:** File too large for RAM

**Solution:** Process one file at a time and concatenate manually
```python
# In preprocessing_maitry.py, process one file:
for grib_file in grib_files[:1]:  # Process first file only
    # ... then manually combine
```

### "Variable not found in file"

**Problem:** Variable names in GRIB don't match expected names

**Solution:** Check available variables:
```python
import xarray as xr
ds = xr.open_dataset("data/raw/maitri_2016.grib", engine="cfgrib")
print(list(ds.data_vars))
```

Update `VARIABLES` list in preprocessing_maitry.py

### Processing takes too long

**Expected time:** 30-60 minutes for 6 files
- Loading: ~5 min per file
- Stacking: ~5 min total
- Normalization: ~5 min total
- Saving: ~10 min total

**If much slower:** Check disk I/O, close other apps

---

## 📈 Monitoring Progress

### Check Current Output

While preprocessing runs (another terminal):
```bash
# See file size growing
ls -lh data/processed/

# See memory usage
top  # macOS/Linux
tasklist  # Windows
```

### Estimate Time Remaining

If on file 3 of 6 after 15 minutes:
```
Time per file: ~15/3 = 5 min
Remaining files: 3
Estimated total: ~15 + 15 = 30 min
```

---

## ✅ Verification

After preprocessing completes:

### 1. Check Files Exist

```bash
ls -lh data/processed/
```

Output should show:
```
-rw-r--r--  8.2G  era5_maitri.npy
-rw-r--r--   32B  mean.npy
-rw-r--r--   32B  std.npy
```

### 2. Verify Data Shape

```python
import numpy as np

data = np.load('data/processed/era5_maitri.npy', mmap_mode='r')
mean = np.load('data/processed/mean.npy')
std = np.load('data/processed/std.npy')

print(f"Data shape: {data.shape}")      # (52560, 4, 120, 200)
print(f"Mean: {mean}")                   # [280.34  5.23 -2.15 50234.5]
print(f"Std: {std}")                     # [12.45  8.34  7.92 1234.6]
```

### 3. Load Into Dataset

```python
from src.dataset import ERA5Dataset

dataset = ERA5Dataset(
    data,
    in_steps=8,
    out_steps=4,
    means=mean,
    stds=std,
    normalize=True
)

print(f"Total samples: {len(dataset)}")  # Should be ~52548
```

### 4. Check Sample

```python
x, y = dataset[0]
print(f"Input shape: {x.shape}")         # (8, 4, 120, 200)
print(f"Output shape: {y.shape}")        # (4, 4, 120, 200)
print(f"Input normalized? {x.min():.2f} to {x.max():.2f}")  # ~-5 to +5
```

---

## 🎯 Next Steps

After preprocessing completes successfully:

1. ✓ Verify files in `data/processed/`
2. ✓ Update `train.py` data paths
3. ✓ Run training:
   ```bash
   cd src
   python train.py
   ```
4. ✓ Monitor training progress in console
5. ✓ View results in `figures/` folder

---

## 📚 Reference

### GRIB Format

- **GRIB:** GRIdded Binary format
- **Use:** Standard for weather data
- **Tool:** `cfgrib` (Python interface)

### Weather Variables

- **2m Temperature (T):** Surface air temperature
- **10m U-wind (U):** Eastward wind component
- **10m V-wind (V):** Northward wind component  
- **Geopotential (Z):** Vertical pressure level height

### Normalization

Per-channel z-score normalization:
```
z = (x - μ) / σ

Where:
  x = original value
  μ = channel mean
  σ = channel standard deviation
  z = normalized value (mean=0, std=1)
```

---

**Happy preprocessing! 🌍📊**
