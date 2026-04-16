import json
from pathlib import Path

_data_dir = Path(__file__).resolve().parent.parent / "data"

with open(_data_dir / "fertiliser_optima.json") as f:
    OPTIMA = json.load(f)


def get_fertiliser_recommendation(
    crop: str, N: float, P: float, K: float
) -> dict:
    """Calculate NPK top-up vs optimal and return recommendation."""
    opt = OPTIMA.get(
        crop,
        {"optimal_N": 100, "optimal_P": 50, "optimal_K": 60, "npk_ratio": "2:1:1"},
    )
    return {
        "recommended_N": max(0, round(opt["optimal_N"] - N, 1)),
        "recommended_P": max(0, round(opt["optimal_P"] - P, 1)),
        "recommended_K": max(0, round(opt["optimal_K"] - K, 1)),
        "npk_ratio": opt.get("npk_ratio", "2:1:1"),
        "note": _generate_note(crop, N, P, K, opt),
    }


def _generate_note(crop: str, N: float, P: float, K: float, opt: dict) -> str:
    """Generate a human-readable fertiliser note in English and Hindi."""
    deficits = []
    hindi_deficits = []

    if N < opt["optimal_N"] * 0.7:
        deficits.append("nitrogen-deficient")
        hindi_deficits.append("नाइट्रोजन की कमी")
    if P < opt["optimal_P"] * 0.7:
        deficits.append("phosphorus-deficient")
        hindi_deficits.append("फॉस्फोरस की कमी")
    if K < opt["optimal_K"] * 0.7:
        deficits.append("potassium-deficient")
        hindi_deficits.append("पोटेशियम की कमी")

    if not deficits:
        return (
            f"Soil nutrition is adequate for {crop}. "
            f"मिट्टी में {crop} के लिए पर्याप्त पोषण है।"
        )
    return (
        f"Soil appears {' and '.join(deficits)}. "
        f"Apply top-up fertiliser before next watering. "
        f"मिट्टी में {' और '.join(hindi_deficits)} है। "
        f"अगली सिंचाई से पहले उर्वरक डालें।"
    )
