import logging
from typing import List

from fastapi import APIRouter, HTTPException

from schemas.yield_schema import (
    FertiliserRecommendation,
    YieldInput,
    YieldResponse,
    YieldRange,
)
from utils.recommendations import get_fertiliser_recommendation

logger = logging.getLogger("cropsense.yield")

router = APIRouter(prefix="/yield", tags=["Yield Prediction"])

VALID_SEASONS = {"Kharif", "Rabi", "Zaid", "Whole Year"}
MAX_BATCH_SIZE = 10


def _get_predictor():
    """Get the yield predictor from the app state."""
    from main import yield_predictor

    return yield_predictor


def _validate_input(data: YieldInput) -> None:
    """Validate input ranges and categorical values with bilingual messages."""
    if data.season not in VALID_SEASONS:
        raise HTTPException(
            status_code=422,
            detail={
                "en": f"Invalid season '{data.season}'. Must be one of: {', '.join(sorted(VALID_SEASONS))}",
                "hi": f"अमान्य मौसम '{data.season}'। ये होना चाहिए: {', '.join(sorted(VALID_SEASONS))}",
            },
        )
    if data.area <= 0:
        raise HTTPException(
            status_code=422,
            detail={
                "en": "Area must be greater than 0 hectares.",
                "hi": "क्षेत्रफल 0 हेक्टेयर से अधिक होना चाहिए।",
            },
        )


def _predict_single(data: YieldInput) -> YieldResponse:
    """Run a single yield prediction and attach fertiliser recommendation."""
    _validate_input(data)

    predictor = _get_predictor()
    result = predictor.predict(data.model_dump())

    # Compute fertiliser recommendation
    fert_rec = get_fertiliser_recommendation(
        crop=data.crop,
        N=data.nitrogen,
        P=data.phosphorus,
        K=data.potassium,
    )

    logger.info(
        "Yield prediction: crop=%s state=%s predicted=%d rating=%s",
        data.crop,
        data.state,
        result["predicted_yield"],
        result["rating"],
    )

    return YieldResponse(
        predicted_yield=result["predicted_yield"],
        unit=result["unit"],
        range=YieldRange(low=result["range"]["low"], high=result["range"]["high"]),
        state_average=result["state_average"],
        pct_vs_avg=result["pct_vs_avg"],
        rating=result["rating"],
        total_production=result["total_production"],
        fertiliser_recommendation=FertiliserRecommendation(
            recommended_N=fert_rec["recommended_N"],
            recommended_P=fert_rec["recommended_P"],
            recommended_K=fert_rec["recommended_K"],
            npk_ratio=fert_rec["npk_ratio"],
            note=fert_rec["note"],
        ),
    )


@router.post(
    "/predict",
    response_model=YieldResponse,
    summary="Predict crop yield",
    description="Predict crop yield based on soil, climate, and agricultural inputs. Returns predicted yield, confidence range, state comparison, and fertiliser recommendations. / फसल उपज की भविष्यवाणी करें।",
)
async def predict_yield(data: YieldInput):
    """Predict yield for a single set of inputs."""
    return _predict_single(data)


@router.post(
    "/batch",
    response_model=List[YieldResponse],
    summary="Batch yield predictions",
    description=f"Run yield predictions for multiple inputs (max {MAX_BATCH_SIZE}). / एक साथ कई फसल उपज भविष्यवाणी करें।",
)
async def predict_yield_batch(data: List[YieldInput]):
    """Run predictions for a batch of inputs."""
    if len(data) > MAX_BATCH_SIZE:
        raise HTTPException(
            status_code=400,
            detail={
                "en": f"Batch size exceeds maximum of {MAX_BATCH_SIZE}.",
                "hi": f"बैच का आकार अधिकतम {MAX_BATCH_SIZE} से अधिक है।",
            },
        )
    if len(data) == 0:
        raise HTTPException(
            status_code=400,
            detail={
                "en": "Batch cannot be empty.",
                "hi": "बैच खाली नहीं हो सकता।",
            },
        )

    results = []
    for i, item in enumerate(data):
        try:
            results.append(_predict_single(item))
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "en": f"Error processing item {i + 1}: {str(e)}",
                    "hi": f"आइटम {i + 1} में त्रुटि: {str(e)}",
                },
            )

    return results
