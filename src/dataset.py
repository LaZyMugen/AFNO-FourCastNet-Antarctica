import torch
from torch.utils.data import Dataset

class ERA5Dataset(Dataset):

    def __init__(
        self,
        data,
        in_steps=8,
        out_steps=4
    ):
        self.data = data
        self.in_steps = in_steps
        self.out_steps = out_steps

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
        ]

        y = self.data[
            idx+self.in_steps:
            idx+self.in_steps+self.out_steps
        ]

        return (
            torch.from_numpy(x),
            torch.from_numpy(y)
        )