import torch

from torchmetrics.functional import accuracy
from lightning.pytorch import LightningModule
from torch import nn


class Digits(LightningModule):
    def __init__(self, optimizer_name: str, optimizer_hparams):
        super().__init__()
        self.save_hyperparameters()
        self.model = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding='same'),
            nn.ReLU(),
            nn.Conv2d(32, 32, kernel_size=3),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2),
            nn.Dropout(p=0.25),

            nn.Conv2d(32, 64, kernel_size=3, padding='same'),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2),
            nn.Dropout(p=0.25),

            nn.Conv2d(64, 128, kernel_size=3, padding='same'),
            nn.ReLU(),
            nn.Conv2d(128, 128, kernel_size=3),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2),
            nn.Dropout(p=0.25),

            nn.Flatten(),

            nn.Linear(128, 256),
            nn.ReLU(),
            nn.Dropout(p=0.5),
            nn.Linear(256, 10)
        )

    def forward(self, X):
        return self.model(X)

    def training_step(self, batch, batch_idx):
        X, y = batch
        y_pred = self(X)
        loss = nn.functional.cross_entropy(y_pred, y)
        acc = accuracy(y_pred, y, task='multiclass', num_classes=10)

        self.log("train_loss", loss, on_step=False, on_epoch=True)
        self.log("train_acc", acc*100.0, on_step=False, on_epoch=True)

        return loss

    def validation_step(self, batch, batch_idx):
        X, y = batch
        y_pred = self(X)
        loss = nn.functional.cross_entropy(y_pred, y)
        acc = accuracy(y_pred, y, task='multiclass', num_classes=10)

        self.log("val_loss", loss)
        self.log("val_acc", acc*100.0)

        return loss

    def test_step(self, batch, batch_idx):
        X, y = batch
        y_pred = self(X)
        loss = nn.functional.cross_entropy(y_pred, y)
        acc = accuracy(y_pred, y, task='multiclass', num_classes=10)

        self.log("test_loss", loss)
        self.log("test_acc", acc*100.0)

    def configure_optimizers(self):
        if self.hparams.optimizer_name == 'SGD':
            optimizer = torch.optim.SGD(
                self.parameters(), **self.hparams.optimizer_hparams)
        else:
            assert False, f'Unknown optimizer: "{self.hparams.optimizer_name}"'

        return optimizer
