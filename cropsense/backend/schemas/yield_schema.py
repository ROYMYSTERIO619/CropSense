from pydantic import BaseModel, Field
from typing import List, Optional


class YieldInput(BaseModel):
    """Input schema for yield prediction with validation ranges."""
    crop: str = Field(..., description="Crop name, e.g. Tomato, Rice, Wheat")
    state: str = Field(..., description="Indian state name, e.g. Maharashtra")
    season: str = Field(
        ..., description="Cropping season: Kharif, Rabi, or Zaid"
    )
    soil_type: str = Field(..., description="Soil type, e.g. Black, Red, Alluvial")
    irrigation_type: str = Field(
        ..., description="Irrigation method, e.g. Drip, Sprinkler, Flood"
    )
    soil_ph: float = Field(
        ..., ge=4.0, le=9.0,
        description="Soil pH value (4.0-9.0). मिट्टी का pH मान।"
    )
    nitrogen: float = Field(
        ..., ge=0, le=300,
        description="Nitrogen content in kg/ha (0-300). नाइट्रोजन (kg/ha)।"
    )
    phosphorus: float = Field(
        ..., ge=0, le=200,
        description="Phosphorus content in kg/ha (0-200). फॉस्फोरस (kg/ha)।"
    )
    potassium: float = Field(
        ..., ge=0, le=300,
        description="Potassium content in kg/ha (0-300). पोटेशियम (kg/ha)।"
    )
    rainfall: float = Field(
        ..., ge=0, le=5000,
        description="Annual rainfall in mm (0-5000). वार्षिक वर्षा (mm)।"
    )
    temperature: float = Field(
        ..., ge=-10, le=55,
        description="Average temperature in Celsius (-10 to 55). तापमान (°C)।"
    )
    fertiliser_used: float = Field(
        ..., ge=0, le=1000,
        description="Total fertiliser used in kg/ha (0-1000). उर्वरक (kg/ha)।"
    )
    pesticide_used: float = Field(
        ..., ge=0, le=100,
        description="Pesticide used in kg/ha (0-100). कीटनाशक (kg/ha)।"
    )
    area: float = Field(
        ..., gt=0, le=10000,
        description="Cultivation area in hectares (>0, <=10000). क्षेत्रफल (हेक्टेयर)।"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "crop": "Tomato",
                "state": "Maharashtra",
                "season": "Kharif",
                "soil_type": "Black",
                "irrigation_type": "Drip",
                "soil_ph": 6.5,
                "nitrogen": 80,
                "phosphorus": 40,
                "potassium": 60,
                "rainfall": 900,
                "temperature": 28,
                "fertiliser_used": 150,
                "pesticide_used": 1.5,
                "area": 2,
            }
        }


class YieldRange(BaseModel):
    """Confidence range for the predicted yield."""
    low: int
    high: int


class FertiliserRecommendation(BaseModel):
    """NPK top-up recommendation."""
    recommended_N: float
    recommended_P: float
    recommended_K: float
    npk_ratio: str
    note: str


class YieldResponse(BaseModel):
    """Full yield prediction response returned by the API."""
    predicted_yield: int
    unit: str
    range: YieldRange
    state_average: int
    pct_vs_avg: float
    rating: str  # EXCELLENT | GOOD | FAIR | POOR
    total_production: int
    fertiliser_recommendation: Optional[FertiliserRecommendation] = None
