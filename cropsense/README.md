# 🌾 CropSense — AI-Powered Crop Disease Detection & Yield Prediction

CropSense is a production-ready AI system that combines **deep learning** for plant disease detection with an **ensemble ML model** for crop yield prediction. Built with FastAPI, TensorFlow, and scikit-learn.

---

## 📐 Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                     CropSense API                        │
│                    (FastAPI + Uvicorn)                    │
├─────────────────────┬────────────────────────────────────┤
│   Disease Detection │         Yield Prediction           │
│   ─────────────────-│   ────────────────────────────     │
│   MobileNetV2 CNN   │   Stacking Ensemble                │
│   41 Classes        │   RF + GBM + XGBoost + Ridge       │
│   Transfer Learning │   14 Features                      │
│   224×224 Input     │   Categorical + Numerical          │
├─────────────────────┼────────────────────────────────────┤
│   Image Upload      │   JSON Input                       │
│   → Preprocess      │   → Encode + Validate              │
│   → Predict         │   → Predict                        │
│   → Treatment Info  │   → Fertiliser Recommendation      │
└─────────────────────┴────────────────────────────────────┘
```

## 📁 Project Structure

```
cropsense/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── routers/
│   │   ├── disease.py           # /api/disease endpoints
│   │   └── yield_pred.py        # /api/yield endpoints
│   ├── models/
│   │   ├── disease_model.py     # CNN model loader + inference
│   │   └── yield_model.py       # Sklearn model loader + inference
│   ├── schemas/
│   │   ├── disease_schema.py    # Pydantic request/response models
│   │   └── yield_schema.py
│   ├── utils/
│   │   ├── image_utils.py       # Preprocessing pipeline
│   │   └── recommendations.py   # Treatment & fertiliser logic
│   ├── data/
│   │   ├── disease_classes.json # All 41 class labels
│   │   ├── treatments.json      # Disease → treatment mapping
│   │   ├── state_averages.json  # Crop × state yield averages
│   │   └── fertiliser_optima.json # Optimal NPK per crop
│   ├── train/
│   │   ├── train_disease.py     # CNN training script
│   │   └── train_yield.py       # Yield model training script
│   ├── requirements.txt
│   └── Dockerfile
├── render.yaml
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone & Install Dependencies

```bash
git clone https://github.com/yourusername/cropsense.git
cd cropsense/backend
pip install -r requirements.txt
```

### 2. Download Datasets

**Disease Detection (PlantVillage):**
```bash
# Option A: Kaggle CLI
kaggle datasets download -d emmarex/plantdisease
unzip plantdisease.zip -d ./data/plantvillage

# Option B: Manual download from
# https://www.kaggle.com/datasets/emmarex/plantdisease
```

**Yield Prediction:**
```bash
# Option A: Kaggle CLI
kaggle datasets download -d patelris/crop-yield-prediction-dataset
unzip crop-yield-prediction-dataset.zip -d ./data/

# Option B: Manual download from
# https://www.kaggle.com/datasets/patelris/crop-yield-prediction-dataset
```

### 3. Train Models

```bash
# Disease detection model (~2 hours on GPU, ~6-8 hours on CPU)
python train/train_disease.py --data_dir ./data/plantvillage

# Force CPU training (if no GPU available):
python train/train_disease.py --data_dir ./data/plantvillage --gpu -1

# Yield prediction model (~20 minutes on CPU)
python train/train_yield.py --data_path ./data/crop_yield.csv
```

### 4. Run the API

```bash
# Development mode (with hot reload)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

> **Note:** The API works even without trained models — it falls back to heuristic/mock predictions for demo purposes.

### 5. Access the API

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

---

## 📡 API Documentation

### Health Check

```bash
curl http://localhost:8000/health
```

```json
{
  "status": "ok",
  "models": {
    "disease": {"loaded": true, "classes": 41, "type": "MobileNetV2 CNN"},
    "yield": {"loaded": true, "type": "Stacking Ensemble (RF + GBM + XGB + Ridge)"}
  }
}
```

### Disease Detection

**POST /api/disease/predict** — Upload a leaf image for disease detection

```bash
curl -X POST http://localhost:8000/api/disease/predict \
  -F "file=@leaf_image.jpg" \
  -F "crop_type=Tomato"
```

**Response:**

```json
{
  "crop": "Tomato",
  "disease": "Late Blight",
  "is_healthy": false,
  "confidence": 94.52,
  "severity": "SEVERE",
  "predictions": [
    {"label": "Tomato___Late_blight", "probability": 0.9452},
    {"label": "Tomato___Early_blight", "probability": 0.0312},
    {"label": "Tomato___Septoria_leaf_spot", "probability": 0.0098}
  ],
  "description": "Caused by Phytophthora infestans...",
  "treatment": [
    "Apply Mancozeb 75% WP at 2g per litre of water",
    "Spray Metalaxyl + Mancozeb (Ridomil Gold) at 2.5g/litre",
    "..."
  ],
  "prevention": [
    "Use certified disease-resistant varieties",
    "..."
  ],
  "analyzed_at": "2026-04-16T10:00:00+00:00"
}
```

**GET /api/disease/classes** — List all supported disease classes

```bash
curl http://localhost:8000/api/disease/classes
```

### Yield Prediction

**POST /api/yield/predict** — Predict crop yield

```bash
curl -X POST http://localhost:8000/api/yield/predict \
  -H "Content-Type: application/json" \
  -d '{
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
    "area": 2
  }'
```

**Response:**

```json
{
  "predicted_yield": 19250,
  "unit": "kg/hectare",
  "range": {"low": 16363, "high": 22138},
  "state_average": 18500,
  "pct_vs_avg": 4.1,
  "rating": "FAIR",
  "total_production": 38500,
  "fertiliser_recommendation": {
    "recommended_N": 40.0,
    "recommended_P": 20.0,
    "recommended_K": 20.0,
    "npk_ratio": "2:1:1.3",
    "note": "Soil appears nitrogen-deficient. Apply top-up fertiliser..."
  }
}
```

**POST /api/yield/batch** — Batch predictions (max 10)

```bash
curl -X POST http://localhost:8000/api/yield/batch \
  -H "Content-Type: application/json" \
  -d '[
    {"crop": "Tomato", "state": "Maharashtra", ...},
    {"crop": "Rice", "state": "Punjab", ...}
  ]'
```

---

## 🧠 Model Architecture & Design Decisions

### Disease Detection — MobileNetV2 CNN

| Aspect | Detail |
|--------|--------|
| **Base Model** | MobileNetV2 (pretrained on ImageNet) |
| **Input Size** | 224 × 224 × 3 (RGB) |
| **Head** | GAP → BN → Dense(512) → Dropout(0.4) → Dense(256) → Dropout(0.3) → Softmax(41) |
| **Training** | 2-phase transfer learning |
| **Phase 1** | Frozen base, Adam(lr=0.001), 15 epochs |
| **Phase 2** | Last 30 layers unfrozen, Adam(lr=0.0001), 10 epochs |
| **Target Accuracy** | 94%+ on validation set |
| **Dataset** | PlantVillage — 54,000+ images, 41 classes, 15 crops |

**Why MobileNetV2 over ResNet?**
- **3.4M params** vs ResNet50's 25.6M — 7.5× smaller
- **Inverted residual blocks** with depthwise separable convolutions
- Optimized for mobile/edge deployment
- Comparable accuracy with much faster inference (~10ms vs ~45ms)
- Ideal for real-time field use on farmer smartphones

**Transfer Learning Strategy:**
- Phase 1 trains only the classification head while base features are frozen
- Phase 2 fine-tunes the last 30 layers to adapt ImageNet features to leaf textures
- This prevents catastrophic forgetting while improving domain-specific accuracy

### Yield Prediction — Stacking Ensemble

| Aspect | Detail |
|--------|--------|
| **Architecture** | StackingRegressor with 5-fold CV |
| **Base Models** | RandomForest(200), GradientBoosting(200), XGBoost(300) |
| **Meta-Learner** | Ridge Regression |
| **Features** | 14 (5 encoded categorical + 9 numerical) |
| **Target** | yield_kg_per_ha (Production / Area) |

**Why Stacking Ensemble?**
- **Reduces variance** — individual tree models can overfit, stacking stabilizes
- **Captures diverse patterns** — RF handles interactions, GBM sequential errors, XGB regularized gradients
- **Ridge meta-learner** prevents overfitting the ensemble
- Consistently outperforms single models by 5-15% in agricultural yield prediction

### PlantVillage Dataset Credibility
- Published by **Penn State University** researchers
- Peer-reviewed dataset used in 500+ research papers
- Contains lab-controlled images with consistent lighting
- Covers 14 crop species and 26 diseases + healthy classes

---

## 📊 Model Performance (Target Metrics)

### Disease Detection
| Metric | Target |
|--------|--------|
| Overall Accuracy | ≥ 94% |
| Per-class Precision | ≥ 85% |
| Per-class Recall | ≥ 80% |
| Inference Time | < 100ms |

### Yield Prediction
| Metric | Target |
|--------|--------|
| R² Score | ≥ 0.85 |
| MAE | < 500 kg/ha |
| RMSE | < 800 kg/ha |

---

## 🐳 Docker Deployment

```bash
cd cropsense/backend

# Build image
docker build -t cropsense-api .

# Run container
docker run -p 8000:8000 cropsense-api
```

## ☁️ Render Deployment

1. Push code to GitHub
2. Connect repository to [Render](https://render.com)
3. Render will auto-detect `render.yaml` and deploy

---

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8000` | Server port |
| `CUDA_VISIBLE_DEVICES` | auto | GPU device ID (-1 for CPU) |
| `TF_CPP_MIN_LOG_LEVEL` | `2` | TensorFlow log level |

---

## 🗺️ Supported Coverage

### Crops (15)
Apple, Blueberry, Cherry, Corn (Maize), Grape, Orange, Peach, Pepper (Bell), Potato, Raspberry, Rice, Soybean, Squash, Strawberry, Tomato

### Disease Classes (41)
Includes both diseased and healthy classes across all supported crops. Run `GET /api/disease/classes` for the full list.

### Indian States (20+)
Maharashtra, Karnataka, Tamil Nadu, Uttar Pradesh, Punjab, Haryana, Madhya Pradesh, Rajasthan, Gujarat, West Bengal, Andhra Pradesh, Telangana, Bihar, Odisha, Assam, Kerala, Jharkhand, Chhattisgarh, Uttarakhand, Himachal Pradesh, Jammu & Kashmir, Goa

---

## 🎤 Interview Talking Points

1. **Why MobileNetV2 over ResNet?**
   - 7.5× fewer parameters (3.4M vs 25.6M)
   - Inverted residual blocks with linear bottlenecks
   - Depthwise separable convolutions reduce compute by 8-9×
   - Designed for mobile deployment — critical for farmer smartphone use
   - Comparable accuracy with much lower latency

2. **Transfer Learning Strategy (2-Phase)**
   - Phase 1: Freeze ImageNet weights, train only the classification head
   - Phase 2: Unfreeze last 30 layers for domain adaptation
   - Prevents catastrophic forgetting of useful low-level features
   - Low learning rate (0.0001) in Phase 2 preserves base knowledge

3. **Why Stacking Ensemble for Yield?**
   - Agricultural data has complex non-linear interactions
   - RF captures feature interactions, GBM corrects sequential residuals, XGBoost adds L1/L2 regularization
   - Ridge meta-learner optimally combines predictions
   - 5-fold CV in stacking prevents information leakage
   - Reduces prediction variance by 15-20% vs single models

4. **PlantVillage Dataset Credibility**
   - Curated by Penn State University researchers
   - Published in peer-reviewed journals
   - 54,000+ expert-verified images
   - Standard benchmark in plant pathology ML research
   - Used in 500+ academic publications

5. **Production Readiness**
   - Bilingual error messages (English + Hindi) for farmer accessibility
   - Graceful fallback (mock/heuristic) when models aren't trained
   - Request logging middleware for analytics
   - Input validation with clear field-level constraints
   - Batch prediction support for large-scale farm management
   - Docker + Render deployment ready

---

## 📝 License

MIT License — See [LICENSE](LICENSE) for details.

## 👤 Author

Built with ❤️ for Indian agriculture By Deepta Roy.
