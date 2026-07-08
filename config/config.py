# config/config.py

# Set to 'bharati' or 'maitri'
STATION = 'bharati'  # Switch this to 'maitri' to run for Maitri station

# Common parameters
IN_STEPS = 8
OUT_STEPS = 4
TIME_INTERVAL_HOURS = 6

INPUT_HOURS = IN_STEPS * TIME_INTERVAL_HOURS
OUTPUT_HOURS = OUT_STEPS * TIME_INTERVAL_HOURS

PATCH_SIZE = 4
EMBED_DIM = 128
NUM_BLOCKS = 6
MLP_RATIO = 4

BATCH_SIZE = 8  # Set to 8 for GPU training
LEARNING_RATE = 1e-4
EPOCHS = 30     # Reset to 30 epochs since GPU (RTX 3050) is now enabled!

SAVE_FIGURES = True

# Station specific parameters
if STATION == 'bharati':
    DATA_FILE = "era5_processed.npy"
    # Variables: [u10, v10, t2m, msl]
    T2M_IDX = 2
    U10_IDX = 0
    V10_IDX = 1
    MSL_IDX = 3
    # Station coordinates & grid mapping
    STATION_LAT = -69.01
    STATION_LON = 76.19
    GRID_LAT_IDX = 36
    GRID_LON_IDX = 105
elif STATION == 'maitri':
    DATA_FILE = "era5_maitri.npy"
    # Variables: [t, u, v, z]
    T2M_IDX = 0
    U10_IDX = 1
    V10_IDX = 2
    MSL_IDX = 3  # Geopotential 'z' is at index 3 in Maitri
    # Station coordinates & grid mapping
    STATION_LAT = -70.76
    STATION_LON = 11.73
    GRID_LAT_IDX = 11
    GRID_LON_IDX = 47