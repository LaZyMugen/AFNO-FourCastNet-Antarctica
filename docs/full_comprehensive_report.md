# Comprehensive Technical Report: Regional Antarctic Weather Forecasting Using AFNO-FourCastNet Deep Learning Architecture

**Project Title:** Regional Adaptation of AFNO-Based FourCastNet for Permanent Indian Antarctic Research Stations (Maitri & Bharati)  
**Author:** Shaswat Sahoo (BITS Pilani, ID: 2024A7PS0152H)  
**Expert Mentor:** VS Samy (Scientist, NCPOR Goa)  
**Academic Guide:** Prof. Hemant Rathore (BITS Pilani)  
**Host Institution:** National Centre for Polar and Ocean Research (NCPOR), Goa  
**Date of Submission:** July 18, 2026  

---

## Document Metadata & Structure (LaTeX Blueprint Settings)
```latex
\documentclass[12pt,titlepage,a4paper,openany]{report}
\usepackage[utf8]{inputenc}
\usepackage{amsmath, amssymb, amsfonts}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{geometry}
\usepackage{hyperref}
\usepackage{listings}
\usepackage{xcolor}
\usepackage{array}
\usepackage{float}
\usepackage{caption}
\usepackage{subcaption}
\usepackage{tikz}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\geometry{top=1in, bottom=1in, left=1.2in, right=1in}
```

---

## Abstract
Traditional Numerical Weather Prediction (NWP) systems present high computational footprints and struggle to resolve polar-specific boundary layer processes due to sub-grid parameterization limitations. This report details the regional adaptation of the Adaptive Fourier Neural Operator (AFNO)-based FourCastNet architecture for permanent Indian Antarctic stations at Maitri ($70.76^\circ$S, $11.73^\circ$E) and Bharati ($69.01^\circ$S, $76.19^\circ$E). Utilizing ECMWF ERA5 reanalysis data spanning 2016–2026, we train a lightweight, grid-agnostic Fourier Vision Transformer that ingests a 48-hour atmospheric lookback window at 6-hourly intervals to output 24-hour autoregressive forecasts. 

Key challenges resolved include mitigating hardware thermal shutdowns on consumer laptops via single-threaded CPU locks and inter-epoch cooling breaks, optimizing memory-mapped GRIB preprocessing to bypass NetCDF C-library memory leaks, and applying in-place z-score normalization on a 5.61 GB Bharati dataset to resolve initial loss explosions ($>625\times 10^6$). 

To counter systematic forecast drift, a post-processing Ridge Regression model with cyclical temporal encoding (sine/cosine transforms of day-of-year and hour-of-day) was integrated. This bias correction layer improved out-of-sample 10m wind speed predictions by $+2.76\%$ ($R^2 = 0.686$) and 2m temperature predictions to $R^2 = 0.918$ at Maitri. A comparative analysis against GraphCast and Pangu-Weather underscores the trade-offs in regional polar meteorology, demonstrating that AFNO offers unmatched inference latency ($<2$ seconds) and local parameter efficiency ($~1.73$M weights), making it highly suitable for regional polar deployments.

---

# Chapter 1: Introduction to AI-Based Weather Forecasting and FourCastNet

## 1.1 The Paradigm Shift: NWP vs. Deep Learning
For over half a century, Numerical Weather Prediction (NWP) has served as the backbone of meteorology. NWP models, such as the European Centre for Medium-Range Weather Forecasts (ECMWF) Integrated Forecasting System (IFS) or the Global Forecast System (GFS), rely on discretization of the Navier-Stokes equations, thermodynamic equations, and mass conservation laws:

\[
\frac{\partial \mathbf{u}}{\partial t} + (\mathbf{u} \cdot \nabla)\mathbf{u} = -\frac{1}{\rho}\nabla p + \nu \nabla^2 \mathbf{u} + \mathbf{g}
\]

While physically consistent, these systems suffer from key structural limitations:
1. **Computational Complexity:** Solving highly coupled, non-linear partial differential equations (PDEs) at global scale requires massive High-Performance Computing (HPC) clusters, consuming millions of core-hours daily.
2. **Sub-Grid Parameterization Errors:** Physical processes operating below the grid scale (e.g., boundary layer turbulence, cloud microphysics, radiative transfer) must be parameterized. In polar regions, these parameterizations often perform poorly due to the scarcity of in-situ observational constraints.
3. **Data Assimilation Latency:** Incorporating real-time observations through 4D-Var data assimilation requires iterative optimization sweeps that delay forecast generation.

In contrast, data-driven deep learning models treat weather forecasting as a spatio-temporal autoregressive sequence-to-sequence problem, learning the mapping:

\[
f_\theta : \mathbf{X}_{t-I+1:t} \mapsto \mathbf{X}_{t+1:t+O}
\]

directly from multi-decadal historical reanalysis datasets. Once trained, these neural networks bypass iterative numerical solvers, completing a global forecast inference pass in seconds on a single GPU.

## 1.2 Adaptive Fourier Neural Operators (AFNO)
The Adaptive Fourier Neural Operator (AFNO), introduced by Guibas et al. (2021), forms the architectural core of FourCastNet. Standard spatial token mixing in Vision Transformers (ViTs) via self-attention exhibits quadratic computational and memory complexity, $\mathcal{O}(M^2)$ where $M$ is the number of tokens:

\[
\text{Attention}(\mathbf{Q}, \mathbf{K}, \mathbf{V}) = \text{softmax}\left(\frac{\mathbf{Q}\mathbf{K}^T}{\sqrt{d_k}}\right)\mathbf{V}
\]

For high-resolution meteorological fields (e.g., $0.25^\circ$ grid over global coordinate space), this quadratic scaling makes full-attention Transformers computationally prohibitive. 

AFNO circumvents this by performing token mixing in the frequency domain using the Discrete Fourier Transform (DFT), reducing spatial mixing complexity to $\mathcal{O}(M \log M)$. This is achieved by utilizing the convolution theorem, which states that spatial convolution is equivalent to element-wise multiplication in the frequency domain. 

The step-by-step mathematical operation within a 2D AFNO layer is defined as:
1. **Fourier Transform:** Convert the spatial feature map $\mathbf{z} \in \mathbb{R}^{H \times W \times d}$ into its complex spectral representation $\hat{\mathbf{z}} \in \mathbb{C}^{H \times \lfloor \frac{W}{2} \rfloor + 1 \times d}$ along the spatial dimensions:
   \[
   \hat{\mathbf{z}} = \mathcal{F}_{2D}(\mathbf{z})
   \]
2. **Spectral Domain Channel Mixing:** Apply a complex-valued linear projection to the spectral components. To limit parameter bloat and avoid overfitting, the channels are mixed using a block-diagonal weight matrix structure. Complex weights $\mathbf{W}^{(1)}, \mathbf{W}^{(2)}$ and complex bias vectors $\mathbf{b}^{(1)}, \mathbf{b}^{(2)}$ are learned to map frequency coefficients:
   \[
   \hat{\mathbf{z}}' = \text{GELU}\left(\mathbf{W}^{(1)} \hat{\mathbf{z}} + \mathbf{b}^{(1)}\right)
   \]
   \[
   \hat{\mathbf{z}}'' = \mathbf{W}^{(2)} \hat{\mathbf{z}}' + \mathbf{b}^{(2)}
   \]
3. **Inverse Fourier Transform:** Project the mixed spectral representations back to the spatial domain:
   \[
   \mathbf{z}' = \mathcal{F}^{-1}_{2D}(\hat{\mathbf{z}}'')
   \]
4. **Spatial Residual Connection:** Add the spatial input mapping to the output of the spectral operation:
   \[
   \mathbf{z}_{\text{out}} = \mathbf{z} + \mathbf{z}'
   \]

By operating in the frequency domain, the model performs global spatial mixing—where every point in the output grid can receive information from every point in the input grid—in a single layer. This global receptive field is crucial for tracking fast-moving meteorological fronts and large-scale atmospheric waves.

---

# Chapter 2: Computational and Operational Infrastructure Setup

## 2.1 Hardware Specifications & Runtime Configurations
The model development and evaluation pipeline was deployed on a local workstation environment with the following physical and software specifications:
* **CPU:** Intel Core i7-12700H (14 Cores, 20 Threads, Max Turbo Frequency 4.70 GHz)
* **GPU:** NVIDIA GeForce RTX 3050 Laptop GPU (4 GB GDDR6 Dedicated VRAM)
* **System Memory:** 16 GB DDR4 RAM
* **Operating System:** Windows 11 Home 64-bit (PowerShell 7.x Shell Environment)
* **Python Environment:** Python 3.12.3 (pip virtual environment wrapper `.venv`)
* **Core Libraries:** PyTorch 2.3.1, NumPy 1.26.4, SciPy 1.13.1, Matplotlib 3.8.4, Joblib 1.4.2, scikit-learn 1.4.2

## 2.2 Operational Challenges & Mitigation Strategies

### Challenge 2.2.1: GPU Overheating and System Instability
During initial training runs using the dedicated CUDA backend (`device = torch.device("cuda")`), the workstation experienced thermal throttling. The sustained compute load associated with spatial FFT operations across 30 epochs pushed the GPU core temperature above $92^\circ$C, trigger-happy thermal limits, resulting in random kernel panics and physical system shutdowns.

* **Mitigation Strategy:** The pipeline was refactored to run exclusively on the CPU. To maintain system responsiveness and prevent overheating, multi-threaded CPU parallelization was locked using environmental overrides. A 3-second sleep window was added at the end of each epoch to allow the physical processor cores to cool.
  ```python
  import os
  import torch
  import time

  # Lock multi-threading libraries to single thread to prevent CPU core saturation
  os.environ["OMP_NUM_THREADS"] = "1"
  os.environ["MKL_NUM_THREADS"] = "1"
  torch.set_num_threads(1)

  # Inside the training loop
  for epoch in range(EPOCHS):
      train_loss = train_epoch(model, train_loader, optimizer, criterion)
      val_loss = validate_epoch(model, val_loader, criterion)
      
      # Cooling break
      print("Epoch complete. Initiating thermal cooling pause...")
      time.sleep(3)
  ```
  This implementation kept CPU temperatures below $68^\circ$C, maintaining system stability over long training schedules.

### Challenge 2.2.2: Memory Leakage during NetCDF File Processing
The initial dataset pipeline loaded five separate annual NetCDF files (`era5_antarctica_2021.nc` through `era5_antarctica_2025.nc`) using the `netCDF4` and `cfgrib` C-bindings. Due to persistent memory leaks within the underlying NetCDF HDF5 file pointers, sequential slice loading during batch assembly caused RAM usage to grow, resulting in "Out of Memory" (OOM) terminal termination.

* **Mitigation Strategy:** The processing pipeline was converted to import directly from a pre-cropped, unified binary GRIB file. The data was compiled into a single `.npy` file using memory-mapped array creation (`mmap_mode='r'`), which bypasses loading the entire dataset into physical RAM:
  ```python
  import numpy as np

  # Read data via memory mapping (mmap_mode='r')
  # This acts as a virtual array pointer, reading slices directly from disk on-demand
  data = np.load("D:/AFNO-FourCastNet-Antarctica/era5_maitri.npy", mmap_mode="r")
  ```

### Challenge 2.2.3: NVIDIA GeForce Experience Overlay Process Termination
A non-obvious crash occurred during the preprocessing of the Maitri dataset. The python process was terminated by the OS with exit code `0xC0000005` (Access Violation). Diagnostic tracing identified a conflict between PyTorch’s internal C++ allocations and the hook injection utilized by the NVIDIA GeForce Experience In-Game Overlay (`nvspcap64.dll`). Disabling the overlay solved the conflict and stabilized the local execution process.

---

# Chapter 3: Dataset Preparation and Normalization Mechanics

## 3.1 Regional Boundaries & Station Mapping
Instead of predicting global grids, this project isolates regional grids centered around India's permanent research stations. This reduces the spatial dimensions, making local training feasible.

### Maitri Station Grid
* **Latitude Range:** $68.00^\circ$S to $73.00^\circ$S  
* **Longitude Range:** $0.00^\circ$E to $20.00^\circ$E  
* **Grid Resolution:** $0.25^\circ \times 0.25^\circ$  
* **Raw Matrix Size:** $21 \times 81$ grid points  
* **Station Coordinate Map:** Grid indices `(11, 47)` correspond to latitude $-70.76$ and longitude $11.73$.

### Bharati Station Grid
* **Latitude Range:** $60.00^\circ$S to $89.75^\circ$S  
* **Longitude Range:** $50.00^\circ$E to $99.75^\circ$E  
* **Grid Resolution:** $0.25^\circ \times 0.25^\circ$  
* **Raw Matrix Size:** $120 \times 200$ grid points  
* **Station Coordinate Map:** Grid indices `(36, 105)` correspond to latitude $-69.01$ and longitude $76.19$.

```
Maitri Grid: 21 x 81 points (1,701 cells total)
[  68.00S, 0.00E ]---------------------[  68.00S, 20.00E ]
|                                                        |
|                 * Maitri (11, 47)                      |
|                                                        |
[  73.00S, 0.00E ]---------------------[  73.00S, 20.00E ]

Bharati Grid: 120 x 200 points (24,000 cells total)
[  60.00S, 50.00E ]--------------------[  60.00S, 99.75E ]
|                                                        |
|                 * Bharati (36, 105)                    |
|                                                        |
[  89.75S, 50.00E ]--------------------[  89.75S, 99.75E ]
```

## 3.2 The Normalization Issue: Diagnosis and Resolution
A major challenge emerged during the initial setup of the Bharati pipeline. The training loss on the first batch was printed as:
`Epoch 0, Batch 0: Loss = 625,184,896.00`

This loss explosion was traced to a dataset anomaly. The data arrays for Bharati had been converted directly from GRIB fields without proper normalization. The variables in the dataset were:
1. **$u10$ & $v10$ Wind Components:** Measured in meters per second ($m/s$), with a standard range of $[-30.0, 30.0]$.
2. **$t2m$ Temp Variable:** Stored in Kelvin ($K$), with values around $230.0$ to $280.0$.
3. **$msl$ Mean Sea Level Pressure:** Stored in Pascals ($Pa$), with raw values around $95,000.0$ to $104,000.0$.

When calculating the Mean Squared Error (MSE) loss, the large values of the pressure field ($msl \approx 10^5$) dominated the gradients. The squared errors for pressure reached $10^9$ to $10^{10}$, causing gradient explosion and model divergence.

To resolve this, we calculated the global mean ($\mu_v$) and standard deviation ($\sigma_v$) for each variable $v$ across the entire temporal domain of the dataset, and applied z-score normalization:

\[
\hat{X}_{t, v, y, x} = \frac{X_{t, v, y, x} - \mu_v}{\sigma_v}
\]

### Statistics for Dataset Normalization
* **Maitri Dataset ($era5\_maitri.npy$):**
  * $t2m$: $\mu = 256.5790$ K, $\sigma = 11.4395$ K
  * $u10$: $\mu = -5.2171$ m/s, $\sigma = 5.4809$ m/s
  * $v10$: $\mu = 2.9326$ m/s, $\sigma = 3.7038$ m/s
  * $z$ (Geopotential): $\mu = 920.4201$, $\sigma = 244.3820$
* **Bharati Dataset ($era5\_processed.npy$):**
  * $u10$: $\mu = -1.8267$ m/s, $\sigma = 5.7533$ m/s
  * $v10$: $\mu = 0.9996$ m/s, $\sigma = 4.8879$ m/s
  * $t2m$: $\mu = 262.8091$ K, $\sigma = 8.1633$ K
  * $msl$: $\mu = 98920.4$ Pa, $\sigma = 1019.4$ Pa

Applying these statistics transformed all inputs into a zero-mean, unit-variance distribution. The loss on Epoch 0, Batch 0 dropped to **0.6865**, verifying successful normalization.

---

# Chapter 4: Architectural Customization and Dynamic Grid Adaptation

## 4.1 Modular Layout & Token Flow
The custom FourCastNet implementation uses a modular layout. It divides 2D fields into patch tokens, processes them using a series of AFNO blocks, and reconstructs the output grid via transposed convolutions:

```
[ Input Patch: B x (T*C) x H x W ]
              │
              ▼
    [ PatchEmbed Layer ] ──> Conv2D(kernel=4, stride=4, Cout=128)
              │
              ▼
    [ Shape Flattening ] ──> Reshape to (B, N_patches, 128)
              │
              ▼
  [ Add Positional Embed ] ──> Learnable Parameter E_pos (Dynamic slice)
              │
              ▼
┌───────────────────────────┐
│     [ AFNO Blocks x 6 ]   │ ──> Stacked frequency mixing stages
└───────────────────────────┘
              │
              ▼
    [ PatchRecovery Layer ] ──> ConvTranspose2D(kernel=4, stride=4, Cout=16)
              │
              ▼
[ Reshape to Output Grid: B x O x V x H x W ]
```

## 4.2 Positional Embeddings for Flexible Grids
In standard vision transformer models, the size of the learned positional embedding parameter is fixed to match a specific input image size:

```python
# Fixed size instantiation (ViT Style)
self.pos_embed = nn.Parameter(torch.zeros(1, fixed_number_of_patches, embed_dim))
```

This configuration restricts the model to a single grid resolution. If the input dimensions change, the spatial patch count shifts, causing dimension mismatch errors.

To solve this, we implemented **dynamic positional slicing**. We initialize a large positional embedding array (`max_patches=5000`) and slice it during the forward pass to match the patch count of the incoming batch:

```python
class PositionalEmbedding(nn.Module):
    def __init__(self, max_patches=5000, embed_dim=128):
        super().__init__()
        # Initialize a large embedding array
        self.pos_embed = nn.Parameter(torch.zeros(1, max_patches, embed_dim))

    def forward(self, x):
        # Dynamically determine the patch count N of the current batch
        N = x.shape[1]
        # Slice the positional embedding parameter to match N
        return x + self.pos_embed[:, :N]
```

This implementation allows the model to process Maitri's grid ($21 \times 81 \rightarrow N = 5 \times 20 = 100$ patches) and Bharati's grid ($120 \times 200 \rightarrow N = 30 \times 50 = 1500$ patches) using the same code, simplifying deployment across different stations.

---

# Chapter 5: Results and Analytical Inferences - Maitri Station

## 5.1 Training Convergence Analysis
The Maitri base model was trained for 30 epochs. As illustrated in the training log plots, both the training and validation loss decreased steadily, showing smooth convergence:

* **Epoch 1:** Train Loss = $0.1794$, Validation Loss = $0.1612$
* **Epoch 10:** Train Loss = $0.1412$, Validation Loss = $0.1495$
* **Epoch 20:** Train Loss = $0.1310$, Validation Loss = $0.1458$
* **Epoch 30:** Train Loss = $0.1264$, Validation Loss = $0.1448$

The small gap between training and validation loss confirms the model's stability and resistance to overfitting on the regional dataset.

```
Loss (MSE)
  0.20 ┼──────────────────────────────
       │  \   --- Training Loss
  0.18 ┼───\──────────────────────────
       │    \   --- Validation Loss
  0.16 ┼─────\─_ ─────────────────────
       │        \___
  0.14 ┼────────────\_______________
       │                            
  0.12 ┼──────────────────────────────
       └─┬────┬────┬────┬────┬────┬─── Epochs
         0    5    10   15   20   25  30
```

## 5.2 Meteorological Evaluation Dashboards

### 5.2.1 Temperature Forecast Validation (`dashboard_temp_scatter_maitri.png`)
The temperature scatter plot compares raw and bias-corrected model forecasts against ERA5 observations:
* **Raw Model Output:** Shows a strong linear correlation along the diagonal ($y = x$), but exhibits a cold bias at lower temperatures. Below $245$ K, the model overestimates the temperature by $2.5$ to $4.0$ K.
* **Bias-Corrected Output:** The Ridge Regression correction layer resolved the cold bias, aligning the scatter points with the diagonal and improving the coefficient of determination to $R^2 = 0.9177$.

### 5.2.2 Wind Speed Forecast Validation (`dashboard_wind_scatter_maitri.png`)
Wind speed prediction is generally more challenging than temperature due to wind's high spatial variability and non-linear boundary interactions:
* **Raw Model Output:** Shows a tendency to underestimate high wind speeds, underpredicting storm winds above $15$ m/s. The raw $R^2$ score was $0.6677$.
* **Bias-Corrected Output:** The post-processing layer partially corrected the underestimation, improving the R-squared score to $0.6861$ ($+2.76\%$ improvement) and reducing the mean absolute error (MAE) from $1.86$ m/s to $1.64$ m/s.

### 5.2.3 Severe Weather Event Tracking (`dashboard_storm_meteorogram_maitri.png`)
To assess the model's operational utility, we evaluated its performance during a severe winter storm at Maitri station:
* **Temperature Evolution:** The model tracked a rapid temperature drop from $265$ K to $242$ K over 48 hours, with the forecast curve matching the ground truth observations.
* **Wind Speed Evolution:** The model captured a sudden wind spike from $6$ m/s to $28$ m/s, demonstrating its capability to forecast high-impact storm events in the Antarctic region.

```
72-Hour Storm Event Timeline (Maitri Grid Cell)
Wind Speed (m/s)
   30 ┼                                      * (Truth: 28m/s)
      │                                     / \
   20 ┼                                    /   \  -- Forecast
      │                                   /     \ -- Truth
   10 ┼      *                           /       \
      │     / \                         /         \
    0 ┼────*───*───────────────────────*───────────*──
     t=0      12      24      36      48      60     72 (Hours)
```

### 5.2.4 Monthly Climatological Drift (`dashboard_climatology_drift_maitri.png`)
Evaluating the model's multi-month predictions revealed an expected behavior:
* Autoregressive models tend to smooth out high-frequency spatial gradients over time. This spectral smoothing causes the forecast range to compress, leading to underestimation of extreme values. This effect is visible in the climatological drift plot as a gradual narrowing of the prediction variance over longer lead times.

---

# Chapter 6: Results and Analytical Inferences - Bharati Station

## 6.1 Spatial and Computational Scale
Applying the model to Bharati station increased the dataset size and spatial grid points:
* **Grid Scale:** Bharati’s grid ($120 \times 200 = 24,000$ points) represents a **$14.1\times$ increase** in spatial complexity compared to Maitri’s grid ($21 \times 81 = 1,701$ points).
* **Data Volume:** The raw processed file size increased from $495$ MB to $5.61$ GB.
* **Convergence Behavior:** The validation loss started at $0.6542$ and decreased to $0.1865$ by epoch 30, showing stable convergence on the larger domain.

## 6.2 Visual Analysis of Bharati Dashboards

### 6.2.1 Temperature Scatter Analysis (`dashboard2_temp_scatter_bharati.png`)
* The scatter plot confirms high forecast fidelity across a temperature range of $235$ K to $280$ K. The points cluster along the diagonal, with minimal dispersion at the warm end. The lower temperature range ($<240$ K) shows slightly higher spread, likely due to cold-air drainage flows over the steeper slopes of the Bharati grid.

### 6.2.2 Wind Speed Scatter Analysis (`dashboard_wind_scatter_bharati.png`)
* The wind speed scatter plot shows a wider spread compared to temperature, reflecting the wind regime of the Larsemann Hills. Katabatic wind acceleration over the ice sheet edge creates strong localized wind shears that are challenging to resolve on a $0.25^\circ$ grid. The model performs well up to $18$ m/s but shows larger errors during extreme wind events.

### 6.2.3 Climatology & Drift Analysis (`dashboard5a_seasonal_climatology_bharati.png`)
* The climatology analysis shows seasonal temperature variations:
  * **Antarctic Summer (Dec–Feb):** Mean surface temperatures range between $268$ K and $273$ K.
  * **Antarctic Winter (Jun–Aug):** Mean temperatures drop to $242$ K to $248$ K.
  * The model captures these seasonal transitions and matches the observed pressure patterns of the Southern Ocean storm track.

---

# Chapter 7: Bias Correction Post-Processing Framework

## 7.1 Ridge Regression formulation
To improve forecast accuracy, we implemented a post-processing bias correction layer using Ridge Regression. The model uses L2 regularization to prevent overfitting:

\[
\min_{\mathbf{w}} \|\mathbf{y} - \mathbf{\Phi}\mathbf{w}\|_2^2 + \alpha \|\mathbf{w}\|_2^2
\]

where $\mathbf{y}$ is the target ground truth variable, $\mathbf{\Phi}$ is the feature matrix, and $\alpha = 1.0$ is the regularization hyperparameter.

The feature space $\mathbf{\Phi}$ includes:
1. **Raw Model Prediction:** The uncorrected forecast value ($\hat{x}$).
2. **Cyclical Hour Mapping:** Sine and cosine transformations of the hour-of-day ($h \in [0, 23]$):
   \[
   \phi_{h, s} = \sin\left(\frac{2\pi h}{24}\right), \quad \phi_{h, c} = \cos\left(\frac{2\pi h}{24}\right)
   \]
3. **Cyclical Day Mapping:** Sine and cosine transformations of the day-of-year ($d \in [1, 365]$):
   \[
   \phi_{d, s} = \sin\left(\frac{2\pi d}{365}\right), \quad \phi_{d, c} = \cos\left(\frac{2\pi d}{365}\right)
   \]

Combining these temporal coordinates helps the model correct systematic biases linked to daily solar cycles and seasonal temperature variations.

## 7.2 Validation Scores (Out-of-Sample Test Set)
The bias correction model was trained on the 2017–2024 period and evaluated on the out-of-sample 2025–2026 test set:

\begin{table}[H]
\centering
\begin{tabular}{lcccc}
    \toprule
    \textbf{Station \& Variable} & \textbf{Raw $R^2$} & \textbf{Corrected $R^2$} & \textbf{Raw MAE} & \textbf{Corrected MAE} \\
    \midrule
    \textbf{Maitri Temp ($t2m$)} & 0.9165 & 0.9177 & 1.12 K & 1.08 K \\
    \textbf{Maitri Wind Speed} & 0.6677 & 0.6861 & 1.86 m/s & 1.64 m/s \\
    \textbf{Bharati Temp ($t2m$)} & 0.8845 & 0.8892 & 1.34 K & 1.28 K \\
    \textbf{Bharati Wind Speed} & 0.6120 & 0.6312 & 2.10 m/s & 1.92 m/s \\
    \bottomrule
\end{tabular}
\caption{Bias Correction validation results (Out-of-Sample test set).}
\label{tab:bias_correction_results}
\end{table}

The post-processing layer consistently improved the $R^2$ scores and reduced the mean absolute error (MAE) for both variables across both stations.

---

# Chapter 8: Deep Comparison of Global AI Models

Evaluating deep learning architectures for regional weather forecasting involves key trade-offs between model parameter scale, memory requirements, and inference speed:

\begin{table}[H]
\centering
\resizebox{\textwidth}{!}{
\begin{tabular}{llll}
    \toprule
    \textbf{Evaluation Dimension} & \textbf{FourCastNet (AFNO)} & \textbf{GraphCast (GNN)} & \textbf{Pangu-Weather (Swin)} \\
    \midrule
    \textbf{Core Block} & Adaptive Fourier Operators & Graph Neural Network & 3D Swin Transformer \\
    \textbf{Computational Cost} & $\mathcal{O}(M \log M)$ (Fourier Mixing) & $\mathcal{O}(V + E)$ (Message-Passing) & $\mathcal{O}(M^2)$ (Windowed Attention) \\
    \textbf{Model Parameter Size} & $\sim 1.73$ Million (Lightweight) & $\sim 35$ Million (Standard) & $\sim 64$ Million (Heavy) \\
    \textbf{Training VRAM Required} & \textbf{6-16 GB} & 32+ GB & 32+ GB \\
    \textbf{Inference Latency} & \textbf{< 2 seconds} & $\sim 30$ seconds & $\sim 5$ seconds \\
    \textbf{Polar Spatial Distortion} & High (Flat 2D FFT mapping) & Low (Icosahedral mesh) & Moderate (Hierarchical windows) \\
    \textbf{Autoregressive Stability} & High (Stable to 3 days) & Very High (Stable to 10 days) & High (Stable to 7 days) \\
    \textbf{Physics Conservation} & None & None & None \\
    \textbf{Open-Source Availability} & High (NVIDIA Modulus) & High (DeepMind Core) & Medium (Weights only) \\
    \bottomrule
\end{tabular}
}
\caption{Architectural comparison of deep learning weather models.}
\label{tab:architectural_comparison}
\end{table}

### Key Inferences from Model Comparison
1. **FourCastNet (AFNO):** Highly efficient, with low parameter counts ($\sim 1.7M$ for regional grids) and fast inference. However, flat 2D FFTs introduce distortions near the geographic poles.
2. **GraphCast (GNN):** Well-suited for global dynamics due to its spherical graph structure, but features high memory requirements and slower training.
3. **Pangu-Weather:** Leverages 3D representations to improve vertical level predictions, but requires substantial VRAM and hardware resources.

---

# Chapter 9: Project Conclusion, Technical Blueprints, and Recommendations

## 9.1 Summary of Technical Work
This project adapted the AFNO-FourCastNet architecture for regional forecasting at Maitri and Bharati stations:
1. **Data Pipeline:** Preprocessed and normalized GRIB datasets spanning 10 years for both stations.
2. **Dynamic Grid Architecture:** Added dynamic positional slicing to support varying grid dimensions ($21 \times 81$ and $120 \times 200$) without structural modification.
3. **Workstation Optimization:** Implemented single-threaded execution locks and inter-epoch cooling breaks to prevent laptop overheating.
4. **Bias Correction:** Trained a post-processing Ridge Regression model with cyclical temporal encoding, improving temperature $R^2$ to $0.918$ at Maitri.
5. **Dashboard Diagnostics:** Created an automated validation suite to monitor training history, scatter convergence, severe storm tracking, and climatological drift.

## 9.2 Recommendations for NCPOR Goa
1. **Establish a Regional Data Archive:** Maintain a pre-cropped, normalized regional ERA5 archive at NCPOR to support model training without repeated CDS downloads.
2. **Deploy on GPU Infrastructure:** Running on dedicated multi-GPU nodes would allow scaling from the $1.7$M regional model to full-scale configurations ($45\text{M}$ to $75\text{M}$ parameters) and extending the training dataset.
3. **In-situ Validation:** Integrate real-time observations from Maitri and Bharati stations to validate forecasts against local weather measurements.
4. **Spherical Harmonics Integration:** Transition from flat 2D FFTs to Spherical Harmonic Transforms to reduce polar boundary distortions.

---

## References
1. Jimmy Lei Ba, Jamie Ryan Kiros, and Geoffrey E Hinton. Layer normalization. *NeurIPS*, 2016.
2. Kaifeng Bi, Lingxi Xie, et al. Accurate medium-range global weather forecasting with 3D neural networks. *Nature*, 619:533-538, 2023.
3. David H Bromwich, et al. Development and testing of Polar WRF: 2. Arctic ocean. *J. Geophys. Res. Atmos.*, 118(6):2463-2484, 2013.
4. Kristopher Chen, et al. Aurora: A foundation model of the atmosphere. *arXiv:2405.13063*, 2024.
5. John Guibas, Morteza Mardani, et al. Adaptive Fourier neural operators. *ICLR*, 2022.
6. Charles R Harris, et al. Array programming with NumPy. *Nature*, 585(7825):357-362, 2020.
7. Kaiming He, Xiangyu Zhang, et al. Deep residual learning for image recognition. *CVPR*, 2016.
8. Hans Hersbach, et al. The ERA5 global reanalysis. *Q. J. R. Meteorol. Soc.*, 146(730):1999-2049, 2020.
9. John D Hunter. Matplotlib: A 2D graphics environment. *Comput. Sci. Eng.*, 9(3):90-95, 2007.
10. Diederik P Kingma and Jimmy Ba. Adam: A method for stochastic optimization. *arXiv:1412.6980*, 2014.
11. Remi Lam, et al. Learning skillful medium-range global weather forecasting. *Science*, 382(6677):1416-1421, 2023.
12. Zongyi Li, et al. Fourier neural operator for parametric PDEs. *ICLR*, 2021.
13. Adam Paszke, et al. PyTorch: An imperative style, high-performance deep learning library. *NeurIPS*, 2019.
14. Jaideep Pathak, et al. FourCastNet: A global data-driven weather model using adaptive Fourier neural operators. *arXiv:2202.11214*, 2022.
15. Jordan G Powers, et al. The Antarctic mesoscale prediction system (AMPS). *Bull. Amer. Meteor. Soc.*, 93(10):1545-1563, 2012.
16. Stephan Rasp and Nils Thuerey. Data-driven weather prediction with a resnet. *JAMES*, 13(2), 2021.
17. Esa-Matti Tastula, et al. Evaluation of Polar WRF. *Monthly Weather Review*, 140(10):3258-3273, 2012.
18. Ashish Vaswani, et al. Attention is all you need. *NeurIPS*, 2017.
19. Jonathan A Weyn, et al. Improving data-driven weather prediction using deep CNNs on a cubed sphere. *JAMES*, 12(9), 2020.
20. Jeff Whitaker et al. netCDF4 python interface, 2023.
