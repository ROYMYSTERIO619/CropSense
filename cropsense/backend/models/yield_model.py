import numpy as np
import joblib
import json
from pathlib import Path


class YieldPredictor:
    """
    Stacking ensemble model for crop yield prediction.
    Uses RandomForest + GradientBoosting + XGBoost with Ridge meta-learner.
    """

    def __init__(self):
        self.model = None
        self.encoders = {}
        self.state_averages = {}
        self._base_dir = Path(__file__).resolve().parent.parent
        self._models_dir = self._base_dir / "models"
        self._data_dir = self._base_dir / "data"

    def load(self):
        """Load the trained stacking model, encoders, and state averages."""
        model_path = self._models_dir / "cropsense_yield_model.pkl"

        if model_path.exists():
            self.model = joblib.load(str(model_path))
            print(f"Yield model loaded from {model_path}")
        else:
            print(
                f"WARNING: Model file not found at {model_path}. "
                "Using heuristic predictions. Train the model first with: "
                "python train/train_yield.py"
            )
            self.model = None

        encoder_names = ["crop", "state", "season", "soil_type", "irrigation"]
        for name in encoder_names:
            enc_path = self._models_dir / f"{name}_encoder.pkl"
            if enc_path.exists():
                self.encoders[name] = joblib.load(str(enc_path))
            else:
                self.encoders[name] = None

        avg_path = self._data_dir / "state_averages.json"
        with open(avg_path) as f:
            self.state_averages = json.load(f)

        print("Yield predictor ready.")

    def predict(self, input_data: dict) -> dict:
        """
        Predict crop yield from input features.

        Args:
            input_data: dict with crop, state, season, soil_type,
                        irrigation_type, soil_ph, nitrogen, phosphorus,
                        potassium, rainfall, temperature, fertiliser_used,
                        pesticide_used, area

        Returns:
            dict with predicted_yield, unit, range, state_average,
            pct_vs_avg, rating, total_production
        """
        if self.model is None or any(v is None for v in self.encoders.values()):
            return self._heuristic_predict(input_data)

        features = [
            self.encoders["crop"].transform([input_data["crop"]])[0],
            self.encoders["state"].transform([input_data["state"]])[0],
            self.encoders["season"].transform([input_data["season"]])[0],
            self.encoders["soil_type"].transform([input_data["soil_type"]])[0],
            self.encoders["irrigation"].transform(
                [input_data["irrigation_type"]]
            )[0],
            input_data["soil_ph"],
            input_data["nitrogen"],
            input_data["phosphorus"],
            input_data["potassium"],
            input_data["rainfall"],
            input_data["temperature"],
            input_data["fertiliser_used"],
            input_data["pesticide_used"],
            input_data["area"],
        ]

        X = np.array(features).reshape(1, -1)
        predicted = float(self.model.predict(X)[0])

        return self._build_response(predicted, input_data)

    def _heuristic_predict(self, input_data: dict) -> dict:
        """
        Heuristic prediction when no trained model is available.
        Uses state averages as baseline with feature-based adjustments.
        """
        key = f"{input_data['state']}_{input_data['crop']}"
        base_yield = self.state_averages.get(key, 5000)

        # Adjust based on input features
        adjustment = 1.0

        # Soil pH adjustment (6.0-7.0 is optimal for most crops)
        ph = input_data.get("soil_ph", 6.5)
        if 6.0 <= ph <= 7.0:
            adjustment *= 1.05
        elif ph < 5.0 or ph > 8.0:
            adjustment *= 0.85

        # NPK adjustment
        n = input_data.get("nitrogen", 80)
        p = input_data.get("phosphorus", 40)
        k = input_data.get("potassium", 60)
        npk_score = min(n / 120, 1.0) * 0.4 + min(p / 60, 1.0) * 0.3 + min(k / 80, 1.0) * 0.3
        adjustment *= (0.7 + 0.3 * npk_score)

        # Rainfall adjustment
        rainfall = input_data.get("rainfall", 800)
        if 600 <= rainfall <= 1200:
            adjustment *= 1.02
        elif rainfall < 400:
            adjustment *= 0.75

        # Temperature adjustment
        temp = input_data.get("temperature", 25)
        if 20 <= temp <= 30:
            adjustment *= 1.0
        elif temp > 40 or temp < 10:
            adjustment *= 0.80

        predicted = base_yield * adjustment
        return self._build_response(predicted, input_data)

    def _build_response(self, predicted: float, input_data: dict) -> dict:
        """Build the standard yield prediction response."""
        # Confidence range: +/- 15%
        low = round(predicted * 0.85)
        high = round(predicted * 1.15)

        # State average comparison
        key = f"{input_data['state']}_{input_data['crop']}"
        state_avg = self.state_averages.get(key, predicted * 0.9)
        pct_diff = ((predicted - state_avg) / state_avg) * 100 if state_avg else 0

        # Rating logic
        if pct_diff > 20:
            rating = "EXCELLENT"
        elif pct_diff > 5:
            rating = "GOOD"
        elif pct_diff > -10:
            rating = "FAIR"
        else:
            rating = "POOR"

        return {
            "predicted_yield": round(predicted),
            "unit": "kg/hectare",
            "range": {"low": low, "high": high},
            "state_average": round(state_avg),
            "pct_vs_avg": round(pct_diff, 1),
            "rating": rating,
            "total_production": round(predicted * input_data["area"]),
        }
