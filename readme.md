# FourCastNet for Antarctica Weather Forecasting

## 🚀 Quick Start (Clone & Run)

### **1. Clone the Repository**
```bash
git clone https://github.com/LaZyMugen/AFNO-FourCastNet-Antarctica.git
cd AFNO-FourCastNet-Antarctica
```

### **2. Create Virtual Environment (Recommended)**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4. Download & Setup Data**

Download the ERA5 dataset from the Google Drive link below and place it in the project root:
https://drive.google.com/file/d/1sf2_rbjG--i7GF1tCkc6BCD4Chd35Ikm/view?usp=drive_link
**File placement:**
```
AFNO-FourCastNet-Antarctica/
├── era5_processed.npy          ← Download and place here (~2.8 GB)
├── data/
│   ├── means.npy               ← Already in repo
│   └── stds.npy                ← Already in repo
└── ...
```

### **5. Quick Verification**
```bash
python verify_setup.py
```
✓ Should show "All checks passed!"

### **6. Train the Model**
```bash
cd src
python train.py
```

**Expected output:**
```
Device: cpu
Dataset Shape: (7304, 4, 120, 200)
Loaded normalization statistics
Total Samples: 7292

Epoch 0: Train Loss: X.XXXXXX, Val Loss: X.XXXXXX
...
Training plot saved to: figures/training_history.png
```

**Results saved to:**
- ✓ `checkpoints/best_model.pth` - Best trained model
- ✓ `figures/epoch_000/` - Forecast visualizations per epoch
- ✓ `figures/training_history.png` - Loss curves

### **7. Run Inference**
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

## 📊 What Gets Generated?

After training, you'll find visualizations in `figures/`:

```
figures/
├── training_history.png           ← Train vs Val loss
├── demo_forecast.png              ← Final inference
├── epoch_000/
│   └── forecast_comparison.png    ← Truth | Prediction | Error
├── epoch_001/
│   └── forecast_comparison.png
└── ... (one folder per epoch)
```

## ⚠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| `FileNotFoundError: era5_processed.npy` | Download from Google Drive link below |
| `ModuleNotFoundError: torch` | Run `pip install -r requirements.txt` |
| Out of memory | Reduce `batch_size` from 16 to 8 in `src/train.py` |
| Slow training | Enable GPU via PyTorch CUDA |

## 📖 For Detailed Documentation

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for comprehensive information.

---

## Dataset

The processed ERA5 dataset is not included in this repository because of its size (~2.8 GB).

Download from the Google Drive link:

https://drive.google.com/file/d/1sf2_rbjG--i7GF1tCkc6BCD4Chd35Ikm/view?usp=drive_link

from the provided Google Drive link.

Place the file in the project root:

AFNO-FourCastNet-Antarctica/
│
├── era5_processed.npy
│
├── src/
├── data/
├── figures/
