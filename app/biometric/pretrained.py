"""Generic pretrained feature extractor baseline; not a validated biometric model."""
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision.models import ResNet18_Weights, resnet18

from app.core.config import settings


class NoseprintEncoder:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        weights = ResNet18_Weights.DEFAULT
        backbone = resnet18(weights=weights)
        backbone.fc = nn.Identity()
        backbone.eval()
        self.model = backbone.to(self.device)
        self.preprocess = weights.transforms()

    @torch.inference_mode()
    def encode(self, image):
        tensor = self.preprocess(image.convert("RGB")).unsqueeze(0).to(self.device)
        vector = self.model(tensor)
        vector = F.normalize(vector, p=2, dim=1)
        return vector[0].cpu().numpy().astype("float32")


_encoder = None


def get_encoder() -> NoseprintEncoder:
    global _encoder
    if _encoder is None:
        _encoder = NoseprintEncoder()
    return _encoder
