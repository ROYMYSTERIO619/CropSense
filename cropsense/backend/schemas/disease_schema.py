from pydantic import BaseModel
from typing import List


class Prediction(BaseModel):
    """Single prediction entry with label and probability."""
    label: str
    probability: float


class DiseaseResponse(BaseModel):
    """Full disease detection response returned by the API."""
    crop: str
    disease: str
    is_healthy: bool
    confidence: float
    severity: str  # MILD | MODERATE | SEVERE | HEALTHY
    predictions: List[Prediction]
    description: str
    treatment: List[str]
    prevention: List[str]
    analyzed_at: str  # ISO timestamp
