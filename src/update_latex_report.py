# src/update_latex_report.py
from pathlib import Path

def generate_tex():
    tex_path = Path("D:/AFNO-FourCastNet-Antarctica/docs/final_report.tex")
    
    content = r"""\documentclass[12pt,titlepage,a4paper]{report}
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

% Adjust geometries to standard thesis formatting
\geometry{top=1in, bottom=1in, left=1.2in, right=1in}

\definecolor{codegreen}{rgb}{0,0.6,0}
\definecolor{codegray}{rgb}{0.5,0.5,0.5}
\definecolor{codepurple}{rgb}{0.58,0,0.82}
\definecolor{backcolour}{rgb}{0.95,0.95,0.92}

\lstdefinestyle{mystyle}{
    backgroundcolor=\color{backcolour},   
    commentstyle=\color{codegreen},
    keywordstyle=\color{magenta},
    numberstyle=\tiny\color{codegray},
    stringstyle=\color{codepurple},
    basicstyle=\ttfamily\footnotesize,
    breakatwhitespace=false,         
    breaklines=true,                 
    captionpos=b,                    
    keepspaces=true,                 
    numbers=left,                    
    numbersep=5pt,                  
    showspaces=false,                
    showstringspaces=false,
    showtabs=false,                  
    tabsize=2
}
\lstset{style=mystyle}

\begin{document}

% ==========================================
% PAGE 1: TITLE PAGE (Tightened spacing to prevent overflow)
% ==========================================
\begin{titlepage}
\begin{center}
    \vspace*{0.5cm}
    \textbf{\large REPORT} \\
    \vspace{0.2cm}
    \textbf{\large ON} \\
    \vspace{0.2cm}
    \textbf{\Large AFNO-BASED FOURCASTNET MODEL FOR ANTARCTIC WEATHER FORECASTING} \\
    
    \vspace{1.5cm}
    BY \\
    \vspace{0.8cm}
    
    \begin{tabular}{lll}
        \textbf{Name of the student:} & \textbf{ID No.:} & \textbf{Discipline:} \\
        Shaswat Sahoo & 2024A7PS0152H & B.E. in CSE \\
    \end{tabular}
    
    \vspace{1.8cm}
    \textbf{Prepared in fulfillment of the \\ Practice School -- I} \\
    
    \vspace{0.8cm}
    AT \\
    \vspace{0.5cm}
    \textbf{National Centre for Polar and Ocean Research (NCPOR), Goa} \\
    \textbf{A Practice School -- I \\ Station of} \\
    
    \vspace{0.6cm}
    \includegraphics[width=2.2cm]{midsem_images/page1_img1.png} \\
    \vspace{0.8cm}
    
    \textbf{BIRLA INSTITUTE OF TECHNOLOGY \& SCIENCE, PILANI} \\
    \vspace{0.3cm}
    \textbf{July, 2026}
\end{center}
\end{titlepage}

% ==========================================
% PAGE 2: STATION DETAILS & METADATA
% ==========================================
\clearpage
\thispagestyle{empty}
\begin{center}
    \textbf{\large BIRLA INSTITUTE OF TECHNOLOGY \& SCIENCE, PILANI} \\
    \textbf{Practice School Division}
\end{center}

\vspace{0.5cm}

\noindent
\begin{tabular}{|p{5.2cm}|p{10cm}|}
    \hline
    \textbf{Station} & National Centre for Polar and Ocean Research, Goa \\ \hline
    \textbf{Duration} & May 2026 -- July 2026 \\ \hline
    \textbf{Date of start} & 25th May 2026 \\ \hline
    \textbf{Date of submission} & 18th July 2026 \\ \hline
    \textbf{Title of the project:} & AFNO-Based FourCastNet Model \\ \hline
    \textbf{ID No.(s), Name(s) and Disciplines:} & 2024A7PS0152H, Shaswat Sahoo, B.E. CSE \\ \hline
    \textbf{Name(s) and Designation(s) of expert(s):} & Prof. VS Samy, Scientist, NCPOR \\ \hline
    \textbf{Name(s) of PS faculty member(s):} & Prof. Hemant Rathore \\ \hline
    \textbf{Key words:} & FourCastNet, AFNO, Antarctic, ERA5, Deep Learning, Weather Forecasting, Bias Correction \\ \hline
    \textbf{Project area(s):} & Numerical Weather Prediction, Deep Learning, Polar Meteorology \\ \hline
    \textbf{Abstract:} & Lightweight AFNO-based FourCastNet model for regional Antarctic weather forecasting at Maitri and Bharati stations. ERA5 reanalysis data (2016--2026) is used with a 48h input window to produce 24h forecasts at 6-hourly resolution. Post-processing bias correction using Ridge Regression achieves an out-of-sample temperature $R^2$ of 0.918 for Maitri. \\ \hline
\end{tabular}

\vspace{1.5cm}

\noindent
\begin{tabular}{cc}
    \makebox[7cm]{\hrulefill} & \makebox[7cm]{\hrulefill} \\
    Signature of the student(s) & Signature of the PS faculty member(s) \\
    Date: & Date:
\end{tabular}

% ==========================================
% PAGE 3: ACKNOWLEDGEMENTS
% ==========================================
\clearpage
\begin{center}
    \textbf{\Large Acknowledgements}
\end{center}
\vspace{0.5cm}

\noindent
I would like to express my sincere gratitude to the National Centre for Polar and Ocean Research (NCPOR), Goa, for providing me with the opportunity to undertake this Practice School internship in such a stimulating and scientifically rich environment. The experience of working on Antarctic weather forecasting has been both intellectually enriching and personally rewarding.

I am deeply grateful to my expert mentor at NCPOR, Prof. VS Samy, for their invaluable guidance, patient explanations, and continuous encouragement throughout the project. Their domain expertise in polar meteorology and numerical weather prediction provided indispensable direction to this work.

I also thank the Practice School faculty member, Prof. Hemant Rathore, for their academic oversight and constructive feedback during the course of this internship.

I acknowledge the European Centre for Medium-Range Weather Forecasts (ECMWF) and the Copernicus Climate Data Store (CDS) for making the ERA5 reanalysis dataset publicly available, which formed the backbone of this project. I also thank the developers of the original FourCastNet framework whose open-source contributions made this regional adaptation possible.

Finally, I thank BITS Pilani, Hyderabad Campus, and the Practice School Division for designing the PS-I programme, which bridges academic learning with real-world scientific challenges.

\vspace{2.5cm}
\noindent
\textbf{Signature of the student}

% ==========================================
% TABLES OF CONTENTS & FIGURES & TABLES
% ==========================================
\clearpage
\tableofcontents
\listoffigures
\listoftables

% ==========================================
% CHAPTER 1: INTRODUCTION
% ==========================================
\chapter{Introduction}
Weather forecasting in polar regions presents unique scientific and operational challenges. The Antarctic continent, characterised by extreme cold, strong katabatic winds, and limited observational infrastructure, remains one of the most data-sparse regions on Earth. Accurate meteorological prediction over Antarctica is critical for the safety of research personnel, logistics planning of polar expeditions, and understanding of global climate systems.

Traditional Numerical Weather Prediction (NWP) systems such as ECMWF's Integrated Forecasting System (IFS) rely on physics-based dynamical models that are computationally intensive and struggle to represent fine-scale polar phenomena. In recent years, data-driven deep learning models have emerged as powerful alternatives, demonstrating skill comparable to or exceeding operational NWP systems at a fraction of the computational cost [14].

FourCastNet (Fourier Forecasting Neural Network), developed by Pathak et al. (2022) at NVIDIA, represents a landmark in this direction. It employs the Adaptive Fourier Neural Operator (AFNO) as its core computational block, enabling efficient modelling of global atmospheric dynamics by operating in the Fourier frequency domain. FourCastNet demonstrated competitive skill against ECMWF's IFS on global forecasting benchmarks while being orders of magnitude faster at inference.

This project adapts the FourCastNet philosophy to a regional Antarctic context. A lightweight AFNO-based model is trained on ERA5 reanalysis data over the Antarctic domain, with special attention to two permanent Indian research stations operated by NCPOR: Maitri (Schirmacher Oasis) and Bharati (Larsemann Hills).

\section{Objectives}
The primary objectives of this project are:
\begin{enumerate}
    \item To acquire, preprocess, and structure ERA5 reanalysis data over the regional Antarctic domains for deep learning-based training.
    \item To implement a lightweight, resolution-flexible AFNO-based FourCastNet architecture.
    \item To train the model to produce 24-hour forecasts from a 48-hour input history at 6-hourly resolution.
    \item To design a thermal-safe CPU-only training pipeline that runs reliably on local computing hardware.
    \item To develop a post-processing bias correction layer using Ridge Regression and cyclical time features to correct systematic temperature and wind speed forecast biases.
    \item To evaluate forecast quality through diagnostic visualizations and validation dashboards on out-of-sample data.
\end{enumerate}

\section{Organisation of the Report}
Chapter 2 provides a literature review of relevant work in data-driven weather forecasting and neural operators. Chapter 3 describes the dataset and preprocessing methodology. Chapter 4 presents the model architecture in detail. Chapter 5 covers training configuration and post-midsem modifications. Chapters 6 and 7 cover the validation results and bias correction for Maitri station. Chapter 8 summarizes the pipeline for Bharati station. Chapter 9 presents a head-to-head comparison of FourCastNet with other major models. Chapter 10 compiles all visual dashboards and validation figures in a comprehensive catalog. Chapters 11 and 12 detail conclusions, future work, and recommendations.

% ==========================================
% CHAPTER 2: LITERATURE REVIEW
% ==========================================
\chapter{Literature Review}
\section{Data-Driven Weather Prediction}
The application of deep learning to weather forecasting has a long history, but the emergence of global-scale transformer-based models marks a qualitative shift. Weyn et al. (2020) demonstrated the viability of convolutional neural networks for medium-range forecasting on a cubed-sphere grid [19], while Rasp and Thuerey (2021) showed that purely data-driven models could begin to approach NWP skill levels [16].

Pangu-Weather [2], developed by Huawei, employs a 3D Earth Transformer architecture to achieve superior 10-day forecast accuracy compared to ECMWF's operational model. GraphCast [11], developed by Google DeepMind, uses a graph neural network over a multi-scale icosahedral mesh and achieves state-of-the-art skill on 1,380 forecast targets. Aurora [4] further pushes the boundary with a large foundation model approach. These works collectively establish that data-driven models can serve as viable operational forecasting tools.

\section{Fourier Neural Operators and FourCastNet}
Neural Operators represent a paradigm for learning mappings between function spaces, enabling resolution-independent generalisation. The Fourier Neural Operator (FNO) proposed by Li et al. (2021) applies spectral convolutions in the Fourier domain to learn PDE solution operators efficiently [12]. The Adaptive Fourier Neural Operator (AFNO), introduced by Guibas et al. (2021), extends this to vision transformer-style architectures [18] with learned Fourier mixing [5].

FourCastNet [14] integrates AFNO blocks into an end-to-end autoregressive forecasting architecture trained on ERA5. It demonstrated a 45,000$\times$ speedup over ECMWF IFS at inference while matching forecast skill at 2-week lead times for many variables. Its open-source release made regional adaptation projects such as the present one feasible.

\section{Antarctic Meteorological Modelling}
Antarctic weather forecasting has historically relied on global NWP output supplemented by regional atmospheric models such as the Polar WRF [3, 17] and AMPS (Antarctic Mesoscale Prediction System) [15]. These systems, while physically principled, are computationally expensive and require regular updates to boundary conditions from global models.

The limited observational density over Antarctica -- few radiosonde stations, sparse surface networks, and challenging satellite retrieval -- makes data assimilation difficult. Deep learning models trained on reanalysis data offer a promising alternative for regional deployment, particularly for research stations such as Maitri and Bharati operated by NCPOR.

% ==========================================
% CHAPTER 3: DATASET AND PREPROCESSING
% ==========================================
\chapter{Dataset and Preprocessing}
\section{ERA5 Reanalysis Data}
The ERA5 reanalysis dataset, produced by the European Centre for Medium-Range Weather Forecasts (ECMWF), serves as the primary data source for this project. ERA5 provides global atmospheric data at $0.25^\circ$ horizontal resolution with hourly temporal resolution, assimilating observations from satellites, radiosondes, surface stations, and aircraft through a state-of-the-art 4D-Var data assimilation system [8].

\section{Maitri vs Bharati Stations data}
Data was retrieved from the Copernicus Climate Data Store (CDS) for both station domains:
\begin{itemize}
    \item \textbf{Maitri Bounding Box:} Latitude $68^\circ$S to $73^\circ$S, Longitude $0^\circ$E to $20^\circ$E ($21 \times 81$ grid points).
    \item \textbf{Bharati Bounding Box:} Latitude $60^\circ$S to $89.75^\circ$S, Longitude $50^\circ$E to $99.75^\circ$E ($120 \times 200$ grid points).
\end{itemize}

\begin{table}[H]
\centering
\begin{tabular}{lll}
    \toprule
    \textbf{Parameter} & \textbf{Maitri Station} & \textbf{Bharati Station} \\
    \midrule
    Temporal Coverage & Jan 2017 -- Jun 2026 (9.5 years) & Jan 2016 -- Dec 2025 (10 years) \\
    Time Steps & 13,860 (6-hourly intervals) & 14,612 (6-hourly intervals) \\
    Grid Size & $21 \times 81$ & $120 \times 200$ \\
    Variables & $u10, v10, t2m, z$ & $u10, v10, t2m, msl$ \\
    Processed Size & 495 MB & 5.61 GB \\
    \bottomrule
\end{tabular}
\caption{ERA5 files details for Maitri and Bharati regional domains.}
\label{tab:era_datasets}
\end{table}

\section{Variables}
Four atmospheric variables were extracted, chosen to represent the primary surface-level meteorological state:
\begin{table}[H]
\centering
\begin{tabular}{ccl}
    \toprule
    \textbf{Index} & \textbf{Variable} & \textbf{Description} \\
    \midrule
    0 & u10 & 10 m zonal wind component ($m\ s^{-1}$) \\
    1 & v10 & 10 m meridional wind component ($m\ s^{-1}$) \\
    2 & t2m & 2 m air temperature ($K$) \\
    3 & msl / z & Mean sea level pressure ($Pa$) / Geopotential ($m^2\ s^{-2}$) \\
    \bottomrule
\end{tabular}
\caption{ERA5 variables used for model training and evaluation.}
\label{tab:variables}
\end{table}

\section{Dataset Shape and Temporal Structure}
After extraction and merging, the raw dataset shapes prior to padding are:
\begin{align}
    \mathbf{X}_{\text{maitri}} &\in \mathbb{R}^{T \times V \times H \times W} = \mathbb{R}^{13860 \times 4 \times 21 \times 81} \\
    \mathbf{X}_{\text{bharati}} &\in \mathbb{R}^{T \times V \times H \times W} = \mathbb{R}^{14612 \times 4 \times 120 \times 200}
\end{align}

\section{Forecasting Configuration}
The model is configured for multi-step autoregressive forecasting with parameters:
\begin{equation}
    I = 8, \quad O = 4, \quad \Delta t = 6\text{ h}
\end{equation}
corresponding to an input window of $8 \times 6 = 48$ hours and a forecast horizon of $4 \times 6 = 24$ hours. The learned mapping is:
\begin{equation}
    f_\theta : \mathbf{X}_{t-I+1:t} \mapsto \hat{\mathbf{X}}_{t+1:t+O}
\end{equation}
where $f_\theta$ denotes the AFNO-based FourCastNet model with parameters $\theta$.

\section{Normalization}
Standard z-score normalization (zero mean, unit variance per variable) is applied across the datasets to ensure equal contributions during training:
\begin{equation}
    X_{\text{norm}} = \frac{X - \mu}{\sigma}
\end{equation}
The computed stats before normalization were verified as:
\begin{itemize}
    \item \textbf{Maitri:} $t2m$ ($\mu=256.58$K, $\sigma=11.44$K), $u10$ ($\mu=-5.22$m/s, $\sigma=5.48$m/s).
    \item \textbf{Bharati:} $t2m$ ($\mu=262.81$K, $\sigma=8.16$K), $msl$ ($\mu=98920.4$Pa, $\sigma=1019.4$Pa).
\end{itemize}

% ==========================================
% CHAPTER 4: MODEL ARCHITECTURE
% ==========================================
\chapter{Model Architecture}
The regional AFNO-based FourCastNet model processing pipeline is structured as follows:
\begin{equation}
    \text{ERA5 Input } (T_{\text{in}} \times V \times H \times W) \xrightarrow{\text{Patch Embed}} \text{Tokens} \xrightarrow{\text{Add Pos Embed}} \text{AFNO Blocks (}\times 6\text{)} \xrightarrow{\text{Patch Recovery}} \hat{\mathbf{X}}_{t+1:t+O}
\end{equation}

\section{Patch Embedding}
The patch embedding module divides the input weather field into non-overlapping spatial patches of size $P \times P$ using a 2D convolutional projection layer:
\begin{equation}
    \mathbf{z} = \text{Conv2D}(\mathbf{x}; \text{kernel}=P, \text{stride}=P, C_{\text{out}}=d)
\end{equation}
where $P=4$ and $d=128$.

\section{Adaptive Fourier Neural Operator (AFNO) Block}
The AFNO block is the core computational unit of FourCastNet. Each AFNO block processes a spatial feature map $\mathbf{z} \in \mathbb{R}^{H' \times W' \times d}$ through:
\begin{enumerate}
    \item Fourier Transform: $\hat{\mathbf{z}} = \mathcal{F}(\mathbf{z})$
    \item Frequency-domain mixing: $\hat{\mathbf{z}}' = \sigma(\mathbf{W}_2 \cdot \sigma(\mathbf{W}_1 \cdot \hat{\mathbf{z}}))$, where $\sigma = \text{GELU}$
    \item Inverse Fourier Transform: $\mathbf{z}' = \mathcal{F}^{-1}(\hat{\mathbf{z}}')$
    \item Residual connection: $\mathbf{z}'' = \mathbf{z} + \mathbf{z}'$
\end{enumerate}
The full block follows the pre-norm structure:
\begin{equation}
    \mathbf{z}_{\ell+1} = \mathbf{z}_\ell + \text{MLP}(\text{LN}(\mathbf{z}_\ell + \text{AFNO}(\text{LN}(\mathbf{z}_\ell))))
\end{equation}
where $\text{LN}$ denotes Layer Normalisation, and the MLP uses expansion ratio $r=4$. A total of $N=6$ AFNO blocks are stacked sequentially.

\section{Patch Recovery and Dynamic Grid Support}
Patch recovery inverts the patch embedding using a transposed 2D convolution:
\begin{equation}
    \hat{\mathbf{x}} = \text{ConvTranspose2D}(\mathbf{z}; \text{kernel}=P, \text{stride}=P, C_{\text{out}}=V \cdot O)
\end{equation}
Output is reshaped to $\hat{\mathbf{X}} \in \mathbb{R}^{B \times O \times V \times H \times W}$. All modules are refactored to automatically infer spatial dimensions from input data. Combined with automatic padding, this enables deployment on the Maitri regional grid ($21 \times 81$) and Bharati regional grid ($120 \times 200$) without modifying model code.

% ==========================================
% CHAPTER 5: METHODOLOGY AND TRAINING (DETAILED)
% ==========================================
\chapter{Methodology and Training}
\section{Training Configuration \& Optimization Strategy}
Training is governed by a centralized configuration file that coordinates parameters across both the Maitri and Bharati station models. The hyperparameters selected represent a balance between computational limitations and convergence speed on regional polar grids. Rather than using a fixed learning rate which can lead to oscillations in the loss landscape, we employ a Cosine Annealing learning rate scheduler:
\begin{equation}
    \eta_t = \eta_{\text{min}} + \frac{1}{2}(\eta_{\text{max}} - \eta_{\text{min}})\left(1 + \cos\left(\frac{T_{\text{cur}}}{T_{\text{max}}}\pi\right)\right)
\end{equation}
where $\eta_{\text{max}} = 10^{-4}$, $\eta_{\text{min}} = 10^{-6}$, and $T_{\text{max}} = 30$ epochs. This strategy allows for large initial steps to quickly map global spatial patterns, followed by fine-grained optimization at later stages. The Adam optimizer is utilized with $\beta_1 = 0.9$ and $\beta_2 = 0.999$, accompanied by a minor weight decay of $10^{-5}$ to prevent parameter drift. Mean Squared Error (MSE) serves as the objective loss function:
\begin{equation}
    \mathcal{L}(\theta) = \frac{1}{B \cdot O \cdot V \cdot H \cdot W} \sum_{b,o,v,h,w} \left( \hat{X}_{(b,o,v,h,w)} - X_{(b,o,v,h,w)} \right)^2
\end{equation}
This directly penalizes large errors, aligning the training loss with standard meteorological Root Mean Squared Error (RMSE) validation metrics.

\begin{table}[H]
\centering
\begin{tabular}{ll}
    \toprule
    \textbf{Hyperparameter} & \textbf{Value} \\
    \midrule
    Batch size & 8 \\
    Initial Learning rate & $10^{-4}$ (Cosine Annealing to $10^{-6}$) \\
    Optimiser & Adam ($\beta_1=0.9$, $\beta_2=0.999$) \\
    Loss function & Mean Squared Error (MSE) \\
    Total Epochs & 30 (with Early Stopping patience of 10 epochs) \\
    Train/validation split & 80\% / 20\% (Split by date range to prevent leakage) \\
    \bottomrule
\end{tabular}
\caption{Detailed training hyperparameters.}
\label{tab:train_hyper_detail}
\end{table}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.6\textwidth]{figures/maitri/training_history_maitri.png}
    \caption{Maitri Training and Validation Loss Convergence history over 30 epochs.}
    \label{fig:text_maitri_loss}
\end{figure}

\section{Post-Midsem Modifications \& Technical Improvements}
Several modifications were implemented to transition the initial prototype into an operationally viable model:
\begin{itemize}
    \item \textbf{Expanded Temporal Data Coverage:} The Maitri station training set was expanded from 5 years to 9.5 years (2017–2026), increasing the number of active training steps from 8,768 to 13,860, which significantly improved seasonal generalizability.
    \item \textbf{In-place Normalization Verification:} Checks were added to verify that the dataset normalization achieves a Mean $\approx 0$ and Std $\approx 1$ before files are mapped into memory.
    \item \textbf{GPU/CPU Coexistence and Safety Locks:} To manage local workstation GPU thermal constraints, the training code was refactored to run on CPU with single-threaded locks (forcing \texttt{OMP\_NUM\_THREADS=1} and \texttt{MKL\_NUM\_THREADS=1}) and a 3-second cooling break between epochs, keeping core temperatures below $68^\circ$C.
    \item \textbf{Directory Isolation:} Output paths were updated to write checkpoints and diagnostic plots to station-specific subfolders (`checkpoints/maitri/` vs `checkpoints/bharati/`), preventing overlapping runs from overwriting results.
\end{itemize}

\section{Autoregressive Rollout Details}
To produce a 24-hour forecast from a 48-hour lookback, the model uses an autoregressive rollout loop. The model generates predictions in 6-hour increments. For lead times beyond $t+6$, the model feeds its own predictions back into the input sequence for subsequent steps. While this enables long-term forecasting, it introduces error propagation, where small inaccuracies at $t+6$ are amplified in later steps. Minimizing this error accumulation is a key focus of the model design.

% ==========================================
% CHAPTER 6: RESULTS - MAITRI STATION (DETAILED)
% ==========================================
\chapter{Results - Maitri Station}
\section{Training Convergence \& Convergence Analysis}
The Maitri model was trained on the expanded 9.5-year dataset for 30 epochs. The training loss decreased steadily from $0.1794$ (Epoch 1) to $0.1264$ (Epoch 30). The validation loss converged to \textbf{0.1448} by Epoch 20 and stabilized, indicating that the model successfully learned regional atmospheric dynamics. The training curve (located in Chapter 10, Figure 10.1) demonstrates stable convergence, with a small generalization gap that confirms the model is not overfitting.

\section{Temperature and Wind Speed Forecast Inferences}
Out-of-sample evaluations on the 2025–2026 test set show varying performance between variables:
\begin{itemize}
    \item \textbf{2m Temperature (t2m):} The model achieves a strong linear correlation, with points in the scatter plot (Figure 10.2) clustering tightly along the diagonal. The raw model underpredicted extreme cold temperatures below $245$ K due to spatial smoothing, which was corrected by the post-processing bias correction layer.
\end{itemize}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.65\textwidth]{figures/maitri/dashboards/dashboard_temp_scatter_maitri.png}
    \caption{Maitri 2m Temperature Scatter - Raw vs Bias-Corrected.}
    \label{fig:text_maitri_temp}
\end{figure}

\begin{itemize}
    \item \textbf{10m Wind Speed (u10, v10):} Wind speed prediction exhibits larger variance than temperature due to local katabatic wind shear over the Schirmacher Oasis. The raw model tended to underestimate storm-level wind speeds ($>15$ m/s), which was partially corrected by the bias correction layer, improving the $R^2$ to $0.6861$.
\end{itemize}

\section{Severe Weather Meteorogram Inferences}
We evaluated the model during a severe winter storm at Maitri. The meteorogram (Figure 10.4) shows that the model successfully forecast a rapid temperature drop from $265$ K to $242$ K and a wind speed spike from $6$ m/s to $28$ m/s, demonstrating its capability to capture high-impact storm developments in the region.

\begin{figure}[H]
    \centering
    \includegraphics[width=0.7\textwidth]{figures/maitri/dashboards/dashboard_storm_meteorogram_maitri.png}
    \caption{72-Hour Storm Event Meteorogram at Maitri.}
    \label{fig:text_maitri_storm}
\end{figure}

\section{Monthly Climatological Drift Analysis}
The climatological drift analysis (Figure 10.5) over a 12-month period reveals that the model's predictions gradually smooth out extreme high-frequency variations over longer lead times. This is a common characteristic of models trained with mean squared error (MSE) loss, which optimizes for the mean state. While the model remains stable, this smoothing effect reduces the variance of forecasts at longer horizons.

% ==========================================
% CHAPTER 7: BIAS CORRECTION POST-PROCESSING (DETAILED)
% ==========================================
\chapter{Bias Correction Post-Processing}
\section{Theoretical Formulation}
Raw deep learning weather models often exhibit systematic biases due to grid discretization and spatial smoothing. To address this, we implemented a post-processing bias correction layer using Ridge Regression. The model uses L2 regularization to prevent overfitting on the cyclical features:
\begin{equation}
    \min_{\mathbf{w}} \|\mathbf{y} - \mathbf{\Phi}\mathbf{w}\|_2^2 + \alpha \|\mathbf{w}\|_2^2
\end{equation}
where $\mathbf{y}$ represents the target observations, $\mathbf{\Phi}$ is the feature matrix, and $\alpha = 1.0$ is the regularization parameter. 

The feature space $\mathbf{\Phi}$ includes:
\begin{enumerate}
    \item The raw model prediction value ($\hat{x}$).
    \item Diurnal cyclical features: sine and cosine transforms of the hour-of-day ($h \in [0, 23]$):
    \begin{equation}
        \phi_{h,s} = \sin\left(\frac{2\pi h}{24}\right), \quad \phi_{h,c} = \cos\left(\frac{2\pi h}{24}\right)
    \end{equation}
    \item Seasonal cyclical features: sine and cosine transforms of the day-of-year ($d \in [1, 365]$):
    \begin{equation}
        \phi_{d,s} = \sin\left(\frac{2\pi d}{365}\right), \quad \phi_{d,c} = \cos\left(\frac{2\pi d}{365}\right)
    \end{equation}
\end{enumerate}
This formulation helps the model correct systematic biases linked to daily solar heating and seasonal temperature cycles.

\section{Maitri and Bharati Improvement Metrics}
The bias correction layer was evaluated on out-of-sample data for both stations:
\begin{table}[H]
\centering
\begin{tabular}{lcccc}
    \toprule
    \textbf{Station \& Variable} & \textbf{Raw $R^2$} & \textbf{Corrected $R^2$} & \textbf{Raw MAE} & \textbf{Corrected MAE} \\
    \midrule
    Maitri Temperature & 0.9165 & 0.9177 & 1.12 K & 1.08 K \\
    Maitri Wind Speed & 0.6677 & 0.6861 & 1.86 m/s & 1.64 m/s \\
    Bharati Temperature & 0.8845 & 0.8892 & 1.34 K & 1.28 K \\
    Bharati Wind Speed & 0.6120 & 0.6312 & 2.10 m/s & 1.92 m/s \\
    \bottomrule
\end{tabular}
\caption{Bias Correction validation results (Out-of-Sample test set).}
\label{tab:bias_correction_comparative}
\end{table}

The post-processing layer improved the $R^2$ scores and reduced the mean absolute error (MAE) for both variables across both stations, with the largest relative improvements observed in wind speed predictions.

\begin{figure}[H]
    \centering
    \includegraphics[width=0.65\textwidth]{figures/maitri/dashboards/dashboard_wind_scatter_maitri.png}
    \caption{Maitri 10m Wind Speed Scatter - Raw vs Bias-Corrected.}
    \label{fig:text_maitri_wind}
\end{figure}

% ==========================================
% CHAPTER 8: RESULTS - BHARATI STATION (DETAILED)
% ==========================================
\chapter{Results - Bharati Station}
\section{Spatial Domain and Topographical Complexity}
The Bharati station model operates on a larger domain ($120 \times 200 = 24,000$ grid points) compared to Maitri's grid ($21 \times 81 = 1,701$ points). This larger area covers the Amery Ice Shelf and the complex topography of the Larsemann Hills, requiring the model to represent both marine boundary layers and high-altitude polar plateau regimes.

\section{Convergence and Loss Profile}
The Bharati model was trained on CPU with single-threaded locks. The training loss converged steadily, starting at $0.6542$ and decreasing to $0.1865$ by Epoch 30 (Figure 10.6). The validation loss tracked the training loss closely, confirming the stability of the AFNO architecture on the larger spatial domain.

\section{Bharati Forecast Inferences}
\begin{itemize}
    \item \textbf{Temperature Scatter (Figure 10.7):} The model matches observations across the $235$ K to $280$ K range. The lower temperature range ($<240$ K) exhibits slightly higher variance, likely due to localized katabatic flows over the coastal slopes.
    \item \textbf{Wind Speed Scatter (Figure 10.8):} Wind speed predictions show larger errors during extreme events ($>18$ m/s) due to localized wind acceleration over the coastal topography.
    \item \textbf{Storm Meteorogram (Figure 10.9):} The model successfully tracked a severe coastal storm, capturing the rapid wind speed variations and corresponding temperature changes.
\end{itemize}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.65\textwidth]{figures/bharati/dashboards/dashboard2_temp_scatter_bharati.png}
    \caption{Bharati 2m Temperature Scatter - Raw vs Bias-Corrected.}
    \label{fig:text_bharati_temp}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.7\textwidth]{figures/bharati/dashboards/dashboard_storm_meteorogram_bharati.png}
    \caption{72-Hour Storm Event Meteorogram at Bharati.}
    \label{fig:text_bharati_storm}
\end{figure}

% ==========================================
% CHAPTER 9: COMPARATIVE ANALYSIS (EXPANDED TO 2 PAGES)
% ==========================================
\chapter{Comparative Analysis}
This chapter provides a comparative analysis of three leading deep learning architectures for weather forecasting: FourCastNet (AFNO), GraphCast (GNN), and Pangu-Weather (3D Swin Transformer). We evaluate these models across computational requirements, forecast stability, and suitability for regional polar forecasting.

\section{Architectural and Mathematical Paradigm Differences}
\begin{itemize}
    \item \textbf{FourCastNet (Adaptive Fourier Neural Operators):} Operates in the frequency domain using 2D FFTs. This enables global spatial mixing at $\mathcal{O}(M \log M)$ complexity, making the model computationally efficient but susceptible to distortions near the poles due to flat grid projections.
    \item \textbf{GraphCast (Graph Neural Networks):} Uses message-passing over a multi-scale icosahedral grid, resolving spatial distortion issues at the expense of higher VRAM usage during training.
    \item \textbf{Pangu-Weather (3D Swin Transformers):} Integrates a hierarchical window-based attention mechanism, using 3D representations to improve vertical level predictions.
\end{itemize}

\section{Computational Footprint \& Operational Trade-offs}
For regional research operations, hardware efficiency is a key consideration. FourCastNet requires significantly less VRAM (6-16 GB) compared to GraphCast and Pangu-Weather (32+ GB), making it feasible to train on standard workstations. Additionally, FourCastNet achieves an inference latency of under 2 seconds, compared to Pangu-Weather (5 seconds) and GraphCast (30 seconds).

\section{Ensemble Scalability \& Operational Risk Assessment}
The computational efficiency of FourCastNet enables large-scale ensemble forecasting. Generating 1,000+ forecast members to compute probability distributions is feasible with FourCastNet, which is critical for assessing weather risks for Antarctic logistics and transport. In contrast, the higher computational cost of GraphCast limits typical ensembles to around 100 members.

\section{Physical Consistency \& Conservation Laws}
All three models are purely data-driven and do not enforce mass, momentum, or energy conservation laws during the forward pass. This can lead to unphysical results over long forecast horizons, highlighting the need for post-processing layers or hybrid modeling approaches.

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
    \textbf{Polar Spatial Distortion} & High (Flat 2D FFT mapping) & Low (Icosahedral mesh) & Moderate \\
    \textbf{Autoregressive Stability} & High (Stable to 3 days) & Very High (Stable to 10 days) & High (Stable to 7 days) \\
    \textbf{Physical Conservation} & None & None & None \\
    \textbf{Open-Source Availability} & High (NVIDIA Modulus) & High (DeepMind Core) & Medium (Weights only) \\
    \bottomrule
\end{tabular}
}
\caption{Comparison of major deep learning weather forecasting architectures.}
\label{tab:model_comparison_expanded}
\end{table}

\section{Forecast Performance in Polar Environments}
The flat 2D projection used in FourCastNet's FFT calculations introduces distortions near the geographic poles. GraphCast's spherical grid handles polar coordinates more effectively. However, for regional forecasting over specific station domains, FourCastNet's local efficiency remains a key advantage.

% ==========================================
% CHAPTER 10: METEOROLOGICAL VISUALIZATION AND PERFORMANCE CATALOG (NEW)
% ==========================================
\chapter{Meteorological Visualization and Performance Catalog}
This chapter compiles all diagnostic figures, training convergence curves, validation dashboards, and forecast comparison plots generated for the Maitri and Bharati stations.

\section{Maitri Station Diagnostic Plots}
\begin{figure}[H]
    \centering
    \includegraphics[width=0.75\textwidth]{figures/maitri/training_history_maitri.png}
    \caption{Maitri Training convergence history over 30 epochs.}
    \label{fig:cat_maitri_loss}
\end{figure}
\begin{figure}[H]
    \centering
    \includegraphics[width=0.85\textwidth]{figures/maitri/dashboards/dashboard_temp_scatter_maitri.png}
    \caption{Maitri 2m Temperature validation scatter plot (Raw vs Corrected).}
    \label{fig:cat_maitri_temp}
\end{figure}
\begin{figure}[H]
    \centering
    \includegraphics[width=0.85\textwidth]{figures/maitri/dashboards/dashboard_wind_scatter_maitri.png}
    \caption{Maitri 10m Wind Speed validation scatter plot (Raw vs Corrected).}
    \label{fig:cat_maitri_wind}
\end{figure}
\begin{figure}[H]
    \centering
    \includegraphics[width=0.85\textwidth]{figures/maitri/dashboards/dashboard_storm_meteorogram_maitri.png}
    \caption{Maitri 72-Hour Storm Event validation meteorogram.}
    \label{fig:cat_maitri_storm}
\end{figure}
\begin{figure}[H]
    \centering
    \includegraphics[width=0.85\textwidth]{figures/maitri/dashboards/dashboard_climatology_drift_maitri.png}
    \caption{Maitri monthly climatology and forecast drift analysis.}
    \label{fig:cat_maitri_drift}
\end{figure}

\clearpage
\section{Bharati Station Diagnostic Plots}
\begin{figure}[H]
    \centering
    \includegraphics[width=0.75\textwidth]{figures/bharati/training_history_bharati.png}
    \caption{Bharati Training convergence history over 30 epochs.}
    \label{fig:cat_bharati_loss}
\end{figure}
\begin{figure}[H]
    \centering
    \includegraphics[width=0.85\textwidth]{figures/bharati/dashboards/dashboard2_temp_scatter_bharati.png}
    \caption{Bharati 2m Temperature validation scatter plot (Raw vs Corrected).}
    \label{fig:cat_bharati_temp}
\end{figure}
\begin{figure}[H]
    \centering
    \includegraphics[width=0.85\textwidth]{figures/bharati/dashboards/dashboard_wind_scatter_bharati.png}
    \caption{Bharati 10m Wind Speed validation scatter plot (Raw vs Corrected).}
    \label{fig:cat_bharati_wind}
\end{figure}
\begin{figure}[H]
    \centering
    \includegraphics[width=0.85\textwidth]{figures/bharati/dashboards/dashboard_storm_meteorogram_bharati.png}
    \caption{Bharati 72-Hour Storm Event validation meteorogram.}
    \label{fig:cat_bharati_storm}
\end{figure}
\begin{figure}[H]
    \centering
    \includegraphics[width=0.85\textwidth]{figures/bharati/dashboards/dashboard_climatology_drift_bharati.png}
    \caption{Bharati monthly climatology and forecast drift analysis.}
    \label{fig:cat_bharati_drift}
\end{figure}

\clearpage
\section{Sample Epoch and Running Average Performance Comparisons}
\begin{figure}[H]
    \centering
    \includegraphics[width=0.85\textwidth]{figures/maitri/epoch_020/t2m_timeseries_maitri.png}
    \caption{Maitri Sample Epoch 20 Temperature Timeseries Plot.}
    \label{fig:cat_sample_epoch}
\end{figure}
\begin{figure}[H]
    \centering
    \includegraphics[width=0.95\textwidth]{figures/antarctic_running_average.png}
    \caption{Antarctic Temperature Forecasts -- 30-Day Running Average (2021 In-Sample).}
    \label{fig:cat_running_average}
\end{figure}

% ==========================================
% CHAPTER 11: CONCLUSIONS AND FUTURE WORK
% ==========================================
\chapter{Conclusions and Future Work}
\section{Conclusions}
This project demonstrated the feasibility of adapting the FourCastNet AFNO-based architecture to regional Antarctic weather forecasting:
\begin{enumerate}
    \item Built a unified ERA5 preprocessing pipeline for Maitri and Bharati stations, expanding to a 9.5-year dataset.
    \item Configured a dynamic, resolution-flexible AFNO model requiring only ~1.73M parameters.
    \item Established a thermal-safe CPU-only training pipeline for hardware-constrained execution.
    \item Implemented post-processing Ridge Regression bias correction, improving wind speed prediction $R^2$ by 2.76\%.
    \item Created validation dashboards showing excellent out-of-sample temperature prediction ($R^2 = 0.918$).
\end{enumerate}

\section{Future Work}
Several future steps are identified:
\begin{itemize}
    \item \textbf{Station-wise observational validation:} Validate against in-situ station observations from Maitri and Bharati.
    \item \textbf{Spherical Harmonics:} Replace flat 2D FFTs with Spherical Harmonics to mitigate polar boundary distortion.
    \item \textbf{Extended variables:} Integrate cloud water, precipitation, and sea-ice concentration variables.
    \item \textbf{Rollout training:} Train using multi-step loss to minimize autoregressive drift.
\end{itemize}

% ==========================================
% CHAPTER 12: RECOMMENDATIONS
% ==========================================
\chapter{Recommendations}
\begin{enumerate}
    \item \textbf{Establish a dedicated ERA5 archive:} A curated, continuously updated regional archive for Antarctica should be maintained at NCPOR.
    \item \textbf{Invest in GPU-enabled HPC capacity:} Access to multi-GPU nodes will enable scale-up to full FourCastNet parameter counts (45-75M).
    \item \textbf{Prioritise digitisation of records:} Ensure historical in-situ station records from Maitri and Bharati are digitized for validation.
    \item \textbf{Probabilistic extensions:} Target probabilistic forecast outputs via diffusion models or ensemble generation.
\end{enumerate}

% ==========================================
% BIBLIOGRAPHY
% ==========================================
\begin{thebibliography}{99}
\bibitem{ba2016} Ba, J. L., Kiros, J. R., \& Hinton, G. E. (2016). Layer normalization. \textit{NeurIPS Workshop}.
\bibitem{bi2023} Bi, K., Xie, L., Zhang, H., et al. (2023). Accurate weather forecasting with 3D neural networks. \textit{Nature}, 619, 533-538.
\bibitem{bromwich2013} Bromwich, D. H., et al. (2013). Development and testing of Polar WRF. \textit{J. Geophys. Res. Atmos.}, 118(6), 2463-2484.
\bibitem{chen2024} Chen, K., et al. (2024). Aurora: A foundation model of the atmosphere. \textit{arXiv:2405.13063}.
\bibitem{guibas2021} Guibas, J., et al. (2021). Adaptive Fourier neural operators. \textit{ICLR}.
\bibitem{harris2020} Harris, C. R., et al. (2020). Array programming with NumPy. \textit{Nature}, 585, 357-362.
\bibitem{he2016} He, K., et al. (2016). Deep residual learning for image recognition. \textit{CVPR}.
\bibitem{hersbach2020} Hersbach, H., et al. (2020). The ERA5 global reanalysis. \textit{Q. J. R. Meteorol. Soc.}, 146(730), 1999-2049.
\bibitem{hunter2007} Hunter, J. D. (2007). Matplotlib: A 2D graphics environment. \textit{Comput. Sci. Eng.}, 9(3), 90-95.
\bibitem{kingma2014} Kingma, D. P., \& Ba, J. (2014). Adam: A method for stochastic optimization. \textit{arXiv:1412.6980}.
\bibitem{lam2023} Lam, R., et al. (2023). Learning weather forecasting. \textit{Science}, 382(6677), 1416-1421.
\bibitem{li2021} Li, Z., et al. (2021). Fourier neural operator for parametric PDEs. \textit{ICLR}.
\bibitem{paszke2019} Paszke, A., et al. (2019). PyTorch: An imperative style, high-performance deep learning library. \textit{NeurIPS}.
\bibitem{pathak2022} Pathak, J., et al. (2022). FourCastNet: A global weather model. \textit{arXiv:2202.11214}.
\bibitem{powers2012} Powers, J. G., et al. (2012). The Antarctic mesoscale prediction system (AMPS). \textit{Bull. Amer. Meteor. Soc.}, 93(10), 1545-1563.
\bibitem{rasp2021} Rasp, S., \& Thuerey, N. (2021). Data-driven weather prediction with a resnet. \textit{JAMES}, 13(2).
\bibitem{tastula2012} Tastula, E. M., \& Andreas, E. L. (2012). Evaluation of Polar WRF. \textit{Monthly Weather Review}, 140(10), 3258-3273.
\bibitem{vaswani2017} Vaswani, A., et al. (2017). Attention is all you need. \textit{NeurIPS}.
\bibitem{weyn2020} Weyn, J. A., et al. (2020). Improving data-driven weather prediction. \textit{JAMES}, 12(9).
\bibitem{whitaker2023} Whitaker, J., et al. (2023). netCDF4 python interface.
\end{thebibliography}

% ==========================================
% APPENDICES
% ==========================================
\appendix
\chapter{Fourier Transform in Neural Operators}
The Discrete Fourier Transform (DFT) of a 2D spatial field $\mathbf{u} \in \mathbb{R}^{H \times W}$ is defined as:
\begin{equation}
    \hat{u}(k_1, k_2) = \sum_{n_1=0}^{H-1} \sum_{n_2=0}^{W-1} u(n_1, n_2) \cdot e^{-2\pi i\left( \frac{k_1 n_1}{H} + \frac{k_2 n_2}{W} \right)}
\end{equation}
The inverse DFT recovers the spatial field:
\begin{equation}
    u(n_1, n_2) = \frac{1}{HW} \sum_{k_1=0}^{H-1} \sum_{k_2=0}^{W-1} \hat{u}(k_1, k_2) \cdot e^{2\pi i\left( \frac{k_1 n_1}{H} + \frac{k_2 n_2}{W} \right)}
\end{equation}
In the AFNO block, the learned weight matrices $\mathbf{W}_1$ and $\mathbf{W}_2$ operate on complex-valued Fourier coefficients $\hat{\mathbf{z}}$. This allows the network to learn global spatial correlations at $\mathcal{O}(HW \log HW)$ computational cost rather than the $\mathcal{O}((HW)^2)$ cost of full self-attention.

\chapter{ERA5 CDS API Retrieval Script}
The following Python script was used to retrieve ERA5 data from the Copernicus Climate Data Store:
\begin{lstlisting}[language=Python]
import cdsapi

c = cdsapi.Client()

for year in range(2016, 2027):
    c.retrieve(
        'reanalysis-era5-single-levels',
        {
            'product_type': 'reanalysis',
            'variable': [
                '10m_u_component_of_wind',
                '10m_v_component_of_wind',
                '2m_temperature',
                'mean_sea_level_pressure',
            ],
            'year': str(year),
            'month': [f'{m:02d}' for m in range(1, 13)],
            'day': [f'{d:02d}' for d in range(1, 32)],
            'time': ['00:00', '06:00', '12:00', '18:00'],
            'area': [-60, 50, -89.75, 99.75],  # Regional domain box
            'format': 'grib',
        },
        f'era5_antarctica_{year}.grib'
    )
\end{lstlisting}

\end{document}
"""
    
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"LaTex source compiled and written to: {tex_path}")

if __name__ == "__main__":
    generate_tex()
