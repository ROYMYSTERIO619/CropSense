import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from schemas.disease_schema import DiseaseResponse, Prediction
from utils.image_utils import preprocess_image, validate_image

logger = logging.getLogger("cropsense.disease")

router = APIRouter(prefix="/disease", tags=["Disease Detection"])

_data_dir = Path(__file__).resolve().parent.parent / "data"

# Load treatments database
with open(_data_dir / "treatments.json") as f:
    TREATMENTS = json.load(f)

# Load class names
with open(_data_dir / "disease_classes.json") as f:
    CLASS_NAMES = json.load(f)

# Max upload size: 10 MB
MAX_FILE_SIZE = 10 * 1024 * 1024


def _parse_class_name(raw: str) -> tuple[str, str]:
    """
    Parse raw class name into (crop, disease).
    Example: 'Tomato___Late_blight' -> ('Tomato', 'Late Blight')
    """
    parts = raw.split("___")
    crop = parts[0].replace("_", " ").strip()
    # Clean up crop names with special chars
    crop = crop.replace(",", ",").replace("(", "(").replace(")", ")")

    if len(parts) > 1:
        disease = parts[1].replace("_", " ").strip().title()
    else:
        disease = "Unknown"

    return crop, disease


def _lookup_treatment(crop: str, disease: str) -> dict:
    """Look up treatment info from treatments.json."""
    # Try exact key match first
    key = f"{crop} {disease}"
    if key in TREATMENTS:
        return TREATMENTS[key]

    # Try partial matches
    for t_key, t_val in TREATMENTS.items():
        if disease.lower() in t_key.lower() and crop.lower() in t_key.lower():
            return t_val

    # Fallback for healthy plants
    if "healthy" in disease.lower():
        return {
            "description": f"No disease detected. The {crop} plant appears healthy.",
            "treatment": [
                "No treatment required - plant is healthy.",
                "Continue regular maintenance and monitoring.",
            ],
            "prevention": [
                "Monitor plants regularly for early disease signs.",
                "Maintain proper irrigation and nutrition.",
            ],
        }

    # Generic fallback
    return {
        "description": f"{disease} detected on {crop}. Consult a local agricultural extension officer for specific treatment.",
        "treatment": [
            "Consult local agricultural extension officer.",
            "Isolate affected plants from healthy ones.",
            "Consider applying a broad-spectrum fungicide.",
        ],
        "prevention": [
            "Practice crop rotation.",
            "Use disease-resistant varieties.",
            "Maintain proper spacing for air circulation.",
        ],
    }


def _determine_severity(confidence: float, is_healthy: bool) -> str:
    """Determine disease severity based on confidence and health status."""
    if is_healthy:
        return "HEALTHY"
    if confidence > 90:
        return "SEVERE"
    elif confidence > 70:
        return "MODERATE"
    else:
        return "MILD"


def _get_detector():
    """Get the disease detector from the app state."""
    from main import disease_detector

    return disease_detector


@router.post(
    "/predict",
    response_model=DiseaseResponse,
    summary="Detect disease in a leaf image",
    description="Upload a leaf image to detect crop disease. Returns disease name, confidence, severity, treatment, and prevention. / पत्ती की तस्वीर अपलोड करें - रोग पहचान के लिए।",
)
async def predict_disease(
    file: UploadFile = File(..., description="Leaf image file (JPG/PNG, max 10MB)"),
    crop_type: str = Form(
        default=None,
        description="Optional crop type for filtering results",
    ),
):
    """Predict disease from an uploaded leaf image."""
    # Validate file size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail={
                "en": "File too large. Maximum size is 10MB.",
                "hi": "फ़ाइल बहुत बड़ी है। अधिकतम आकार 10MB है।",
            },
        )

    # Validate image format
    if not validate_image(contents):
        raise HTTPException(
            status_code=400,
            detail={
                "en": "Invalid image file. Please upload a JPG or PNG image.",
                "hi": "अमान्य छवि फ़ाइल। कृपया JPG या PNG छवि अपलोड करें।",
            },
        )

    # Preprocess
    preprocessed = preprocess_image(contents)

    # Run inference
    detector = _get_detector()
    result = detector.predict(preprocessed)

    # Parse disease name
    crop, disease = _parse_class_name(result["disease_raw"])
    is_healthy = "healthy" in result["disease_raw"].lower()

    # Severity
    severity = _determine_severity(result["confidence"], is_healthy)

    # Treatment lookup
    treatment_info = _lookup_treatment(crop, disease)

    # Build predictions list
    predictions = [
        Prediction(label=p["label"], probability=p["probability"])
        for p in result["top3"]
    ]

    logger.info(
        "Disease prediction: crop=%s disease=%s confidence=%.2f severity=%s",
        crop,
        disease,
        result["confidence"],
        severity,
    )

    return DiseaseResponse(
        crop=crop,
        disease=disease if not is_healthy else "None - Healthy",
        is_healthy=is_healthy,
        confidence=result["confidence"],
        severity=severity,
        predictions=predictions,
        description=treatment_info.get("description", ""),
        treatment=treatment_info.get("treatment", []),
        prevention=treatment_info.get("prevention", []),
        analyzed_at=datetime.now(timezone.utc).isoformat(),
    )


@router.get(
    "/classes",
    summary="Get all supported disease classes",
    description="Returns the list of all 41 supported disease/healthy class names.",
)
async def get_classes():
    """Return all supported disease class names."""
    return {
        "total_classes": len(CLASS_NAMES),
        "classes": CLASS_NAMES,
        "crops": sorted(
            set(name.split("___")[0].replace("_", " ") for name in CLASS_NAMES)
        ),
    }
