import torch
import torch.nn as nn

class PatchEmbed(nn.Module):

    def __init__(
        self,
        in_channels=32,
        embed_dim=128,
        patch_size=4
    ):
        super().__init__()

        self.proj = nn.Conv2d(
            in_channels,
            embed_dim,
            kernel_size=patch_size,
            stride=patch_size
        )

    def forward(self, x):

        x = self.proj(x)

        B,C,H,W = x.shape

        x = x.flatten(2)

        x = x.transpose(1,2)

        return x
    
  

class PositionalEmbedding(nn.Module):

    def __init__(
        self,
        num_patches=1500,
        embed_dim=128
    ):
        super().__init__()

        self.pos_embed = nn.Parameter(
            torch.zeros(
                1,
                num_patches,
                embed_dim
            )
        )

    def forward(self, x):

        return x + self.pos_embed


class AFNO2D(nn.Module):

    def __init__(
        self,
        embed_dim=128
    ):
        super().__init__()

        self.fc1 = nn.Linear(
            embed_dim,
            embed_dim
        )

        self.fc2 = nn.Linear(
            embed_dim,
            embed_dim
        )

        self.act = nn.GELU()

    def forward(self, x):

        B,N,C = x.shape

        H = 30
        W = 50

        x = x.reshape(
            B,
            H,
            W,
            C
        )

        x = x.permute(
            0,
            3,
            1,
            2
        )

        freq = torch.fft.rfft2(x)

        real = freq.real
        imag = freq.imag

        real = real.permute(
            0,2,3,1
        )

        imag = imag.permute(
            0,2,3,1
        )

        real = self.fc2(
            self.act(
                self.fc1(real)
            )
        )

        imag = self.fc2(
            self.act(
                self.fc1(imag)
            )
        )

        real = real.permute(
            0,3,1,2
        )

        imag = imag.permute(
            0,3,1,2
        )

        freq = torch.complex(
            real,
            imag
        )

        x = torch.fft.irfft2(
            freq,
            s=(H,W)
        )

        x = x.permute(
            0,
            2,
            3,
            1
        )

        x = x.reshape(
            B,
            N,
            C
        )

        return x
    


class MLP(nn.Module):

    def __init__(
        self,
        embed_dim=128,
        mlp_ratio=4
    ):
        super().__init__()

        hidden_dim = embed_dim * mlp_ratio

        self.fc1 = nn.Linear(
            embed_dim,
            hidden_dim
        )

        self.fc2 = nn.Linear(
            hidden_dim,
            embed_dim
        )

        self.act = nn.GELU()

    def forward(self, x):

        x = self.fc1(x)

        x = self.act(x)

        x = self.fc2(x)

        return x
    

class AFNOBlock(nn.Module):

    def __init__(
        self,
        embed_dim=128,
        mlp_ratio=4
    ):
        super().__init__()

        self.norm1 = nn.LayerNorm(
            embed_dim
        )

        self.afno = AFNO2D(
            embed_dim
        )

        self.norm2 = nn.LayerNorm(
            embed_dim
        )

        self.mlp = MLP(
            embed_dim,
            mlp_ratio
        )

    def forward(self, x):

        x = x + self.afno(
            self.norm1(x)
        )

        x = x + self.mlp(
            self.norm2(x)
        )

        return x
    

class PatchRecovery(nn.Module):

    def __init__(
        self,
        embed_dim=128,
        out_channels=16,
        patch_size=4
    ):
        super().__init__()

        self.out_channels = out_channels

        self.patch_size = patch_size

        self.proj = nn.ConvTranspose2d(
            embed_dim,
            out_channels,
            kernel_size=patch_size,
            stride=patch_size
        )

    def forward(self, x):

        B,N,C = x.shape

        x = x.transpose(
            1,
            2
        )

        x = x.reshape(
            B,
            C,
            30,
            50
        )

        x = self.proj(x)

        return x
    


class FourCastNet(nn.Module):

    def __init__(
        self,
        embed_dim=128,
        depth=6,
        mlp_ratio=4
    ):
        super().__init__()

        self.patch_embed = PatchEmbed(
            in_channels=32,
            embed_dim=embed_dim
        )

        self.pos_embed = PositionalEmbedding(
            1500,
            embed_dim
        )

        self.blocks = nn.ModuleList(
            [
                AFNOBlock(
                    embed_dim,
                    mlp_ratio
                )
                for _ in range(depth)
            ]
        )

        self.recovery = PatchRecovery(
            embed_dim,
            out_channels=16
        )

    def forward(self, x):

        B,T,C,H,W = x.shape

        x = x.reshape(
            B,
            T*C,
            H,
            W
        )

        x = self.patch_embed(x)

        x = self.pos_embed(x)

        for block in self.blocks:

            x = block(x)

        x = self.recovery(x)

        x = x.reshape(
            B,
            4,
            4,
            120,
            200
        )

        return x