import torch
import numpy as np
from torch.utils.data import Dataset

class ERA5Dataset(Dataset):

    def __init__(
        self,
        data,
        in_steps=8,
        out_steps=4,
        means=None,
        stds=None,
        normalize=True
    ):
        self.data = data
        self.in_steps = in_steps
        self.out_steps = out_steps
        self.normalize = normalize
        self.means = means
        self.stds = stds

    def __len__(self):

        return (
            len(self.data)
            - self.in_steps
            - self.out_steps
        )

    def __getitem__(self, idx):

        x = self.data[
            idx:
            idx+self.in_steps
        ].astype(np.float32)

        y = self.data[
            idx+self.in_steps:
            idx+self.in_steps+self.out_steps
        ].astype(np.float32)

        if self.normalize and self.means is not None and self.stds is not None:
            # Handle different shapes of means/stds
            means = self.means.copy()
            stds = self.stds.copy()
            
            # If means/stds are 1D (per-variable), reshape for broadcasting
            if means.ndim == 1:
                means = means[np.newaxis, :, np.newaxis, np.newaxis]
                stds = stds[np.newaxis, :, np.newaxis, np.newaxis]
            # If means/stds are 3D (per-spatial-location), add time dimension
            elif means.ndim == 3:
                means = means[np.newaxis, :, :, :]
                stds = stds[np.newaxis, :, :, :]
            
            x = (x - means) / (stds + 1e-6)
            y = (y - means) / (stds + 1e-6)

        return (
            torch.from_numpy(x),
            torch.from_numpy(y)
        )