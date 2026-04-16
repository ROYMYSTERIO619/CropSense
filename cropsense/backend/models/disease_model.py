import numpy as np
import json
from pathlib import Path

# Lazy import: tensorflow is only needed when a trained model exists
tf = None


def _load_tf():
    """Lazily import tensorflow."""
    global tf
    if tf is None:
        import tensorflow as _tf
        tf = _tf
    return tf


class DiseaseDetector:
    """
    CNN-based plant disease detector using MobileNetV2.
    Loads a trained model and performs inference on preprocessed leaf images.
    Falls back to mock predictions if tensorflow is not installed or model is missing.
    """

    def __init__(self):
        self.model = None
        self.class_names = []
        self._base_dir = Path(__file__).resolve().parent.parent
        self.model_path = self._base_dir / "models" / "cropsense_disease_model.h5"
        self.classes_path = self._base_dir / "data" / "disease_classes.json"

    def load(self):
        """Load the trained model and class labels."""
        if self.model_path.exists():
            try:
                _tf = _load_tf()
                self.model = _tf.keras.models.load_model(str(self.model_path))
                print(f"Disease model loaded from {self.model_path}")
            except (ImportError, Exception) as e:
                print(f"WARNING: Could not load TensorFlow model: {e}")
                self.model = None
        else:
            print(
                f"WARNING: Model file not found at {self.model_path}. "
                "Using mock predictions. Train the model first with: "
                "python train/train_disease.py"
            )
            self.model = None

        with open(self.classes_path) as f:
            self.class_names = json.load(f)
        print(f"Disease detector ready. Classes: {len(self.class_names)}")

    def predict(self, preprocessed_image: np.ndarray) -> dict:
        """
        Run inference on a preprocessed image.

        Args:
            preprocessed_image: numpy array of shape (1, 224, 224, 3), normalized [0,1]

        Returns:
            dict with disease_raw, confidence, and top3 predictions
        """
        if self.model is None:
            return self._mock_predict()

        predictions = self.model.predict(preprocessed_image, verbose=0)[0]
        top3_idx = np.argsort(predictions)[::-1][:3]

        top_class = self.class_names[top3_idx[0]]
        confidence = float(predictions[top3_idx[0]]) * 100

        return {
            "disease_raw": top_class,
            "confidence": round(confidence, 2),
            "top3": [
                {
                    "label": self.class_names[i],
                    "probability": round(float(predictions[i]), 4),
                }
                for i in top3_idx
            ],
        }

    def _mock_predict(self) -> dict:
        """Return mock predictions when no trained model is available."""
        import random

        idx = random.randint(0, len(self.class_names) - 1)
        mock_conf = round(random.uniform(0.85, 0.98), 4)

        other_indices = [i for i in range(len(self.class_names)) if i != idx]
        random.shuffle(other_indices)
        top3_indices = [idx] + other_indices[:2]

        remaining = 1.0 - mock_conf
        p2 = round(remaining * 0.6, 4)
        p3 = round(remaining * 0.4, 4)
        probs = [mock_conf, p2, p3]

        return {
            "disease_raw": self.class_names[idx],
            "confidence": round(mock_conf * 100, 2),
            "top3": [
                {
                    "label": self.class_names[top3_indices[i]],
                    "probability": probs[i],
                }
                for i in range(3)
            ],
        }
