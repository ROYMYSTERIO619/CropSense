"""
CropSense - Yield Prediction Model Training Script
====================================================
Trains a stacking ensemble (RF + GBM + XGBoost + Ridge meta-learner)
for crop yield prediction using the Crop Yield Prediction Dataset.

Usage:
  python train/train_yield.py --data_path ./data/crop_yield.csv
  python train/train_yield.py --data_path ./data/crop_yield.csv --output_dir ./models
"""

import argparse
import json
import pickle
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import (
    GradientBoostingRegressor,
    RandomForestRegressor,
    StackingRegressor,
)
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder


def parse_args():
    parser = argparse.ArgumentParser(
        description="Train CropSense yield prediction model"
    )
    parser.add_argument(
        "--data_path",
        type=str,
        default="./data/crop_yield.csv",
        help="Path to the crop yield CSV dataset",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./models",
        help="Directory to save trained model and encoders",
    )
    parser.add_argument(
        "--test_size",
        type=float,
        default=0.2,
        help="Proportion of data for testing",
    )
    parser.add_argument(
        "--random_state",
        type=int,
        default=42,
        help="Random seed for reproducibility",
    )
    return parser.parse_args()


def load_and_clean(data_path: str) -> pd.DataFrame:
    """Load dataset and perform cleaning."""
    print(f"Loading dataset from {data_path}...")
    df = pd.read_csv(data_path)

    print(f"Raw dataset shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")

    # Standardize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Map common column name variations
    col_map = {
        "state_name": "state",
        "district_name": "district",
        "crop_year": "year",
        "crop": "crop",
        "season": "season",
        "area": "area",
        "production": "production",
    }
    for old, new in col_map.items():
        if old in df.columns and new not in df.columns:
            df.rename(columns={old: new}, inplace=True)

    # Drop rows with null/zero production or area
    initial_len = len(df)
    if "production" in df.columns and "area" in df.columns:
        df = df.dropna(subset=["production", "area"])
        df = df[(df["production"] > 0) & (df["area"] > 0)]

        # Create target: yield = production / area
        df["yield_kg_per_ha"] = df["production"] / df["area"]
    elif "yield" in df.columns:
        df.rename(columns={"yield": "yield_kg_per_ha"}, inplace=True)
        df = df.dropna(subset=["yield_kg_per_ha"])
        df = df[df["yield_kg_per_ha"] > 0]
    else:
        print("ERROR: Cannot find production/area or yield columns.")
        print(f"Available columns: {list(df.columns)}")
        sys.exit(1)

    # Remove outliers: top/bottom 1% of yield
    q_low = df["yield_kg_per_ha"].quantile(0.01)
    q_high = df["yield_kg_per_ha"].quantile(0.99)
    df = df[(df["yield_kg_per_ha"] >= q_low) & (df["yield_kg_per_ha"] <= q_high)]

    print(f"After cleaning: {len(df)} rows (dropped {initial_len - len(df)})")
    print(f"Yield range: {df['yield_kg_per_ha'].min():.0f} - {df['yield_kg_per_ha'].max():.0f} kg/ha")
    print(f"Yield mean: {df['yield_kg_per_ha'].mean():.0f} kg/ha")

    return df


def prepare_features(df: pd.DataFrame, output_dir: Path) -> tuple:
    """Encode categoricals and prepare feature matrix."""
    print("\nPreparing features...")

    # Identify available categorical and numerical columns
    categorical_cols = {}
    encoder_mapping = {
        "crop": "crop",
        "state": "state",
        "season": "season",
        "soil_type": "soil_type",
        "irrigation_type": "irrigation",
        "irrigation": "irrigation",
    }

    encoders = {}
    encoded_features = []

    for col, enc_name in encoder_mapping.items():
        if col in df.columns:
            le = LabelEncoder()
            df[f"{enc_name}_encoded"] = le.fit_transform(df[col].astype(str))
            encoders[enc_name] = le
            encoded_features.append(f"{enc_name}_encoded")
            print(f"  Encoded '{col}': {len(le.classes_)} unique values")

    # Identify available numerical columns
    numerical_candidates = [
        "soil_ph", "nitrogen", "phosphorus", "potassium",
        "rainfall", "temperature", "fertiliser_used",
        "pesticide_used", "area", "year",
        "n", "p", "k",
    ]
    numerical_features = [c for c in numerical_candidates if c in df.columns]

    # Map short names
    if "n" in df.columns and "nitrogen" not in df.columns:
        df["nitrogen"] = df["n"]
        numerical_features = [c if c != "n" else "nitrogen" for c in numerical_features]
    if "p" in df.columns and "phosphorus" not in df.columns:
        df["phosphorus"] = df["p"]
        numerical_features = [c if c != "p" else "phosphorus" for c in numerical_features]
    if "k" in df.columns and "potassium" not in df.columns:
        df["potassium"] = df["k"]
        numerical_features = [c if c != "k" else "potassium" for c in numerical_features]

    # Remove duplicates
    numerical_features = list(dict.fromkeys(numerical_features))

    all_features = encoded_features + numerical_features
    print(f"  Final feature set ({len(all_features)}): {all_features}")

    # Handle missing values in numerical columns
    for col in numerical_features:
        if df[col].isnull().any():
            median_val = df[col].median()
            df[col].fillna(median_val, inplace=True)
            print(f"  Filled NaN in '{col}' with median={median_val:.2f}")

    X = df[all_features].values
    y = df["yield_kg_per_ha"].values

    # Save encoders
    for name, encoder in encoders.items():
        enc_path = output_dir / f"{name}_encoder.pkl"
        joblib.dump(encoder, str(enc_path))
        print(f"  Saved encoder: {enc_path}")

    # Save feature list
    feature_path = output_dir / "feature_names.json"
    with open(feature_path, "w") as f:
        json.dump(all_features, f, indent=2)
    print(f"  Feature names saved to {feature_path}")

    return X, y, all_features, encoders


def train_model(X_train, y_train, random_state=42):
    """Build and train the stacking ensemble model."""
    print("\nBuilding stacking ensemble...")

    try:
        from xgboost import XGBRegressor

        base_models = [
            (
                "rf",
                RandomForestRegressor(
                    n_estimators=200,
                    max_depth=15,
                    random_state=random_state,
                    n_jobs=-1,
                ),
            ),
            (
                "gbm",
                GradientBoostingRegressor(
                    n_estimators=200,
                    learning_rate=0.05,
                    max_depth=6,
                    random_state=random_state,
                ),
            ),
            (
                "xgb",
                XGBRegressor(
                    n_estimators=300,
                    learning_rate=0.05,
                    max_depth=6,
                    subsample=0.8,
                    random_state=random_state,
                    verbosity=0,
                ),
            ),
        ]
        print("  Using: RandomForest + GradientBoosting + XGBoost + Ridge")
    except ImportError:
        print("  WARNING: XGBoost not installed. Using RF + GBM only.")
        base_models = [
            (
                "rf",
                RandomForestRegressor(
                    n_estimators=200,
                    max_depth=15,
                    random_state=random_state,
                    n_jobs=-1,
                ),
            ),
            (
                "gbm",
                GradientBoostingRegressor(
                    n_estimators=200,
                    learning_rate=0.05,
                    max_depth=6,
                    random_state=random_state,
                ),
            ),
        ]

    meta_model = Ridge(alpha=1.0)

    stacker = StackingRegressor(
        estimators=base_models,
        final_estimator=meta_model,
        cv=5,
        n_jobs=-1,
        verbose=1,
    )

    print("Training stacking ensemble (this may take 10-20 minutes)...")
    stacker.fit(X_train, y_train)
    print("Training complete.")

    return stacker


def evaluate_model(model, X_test, y_test, feature_names, output_dir):
    """Evaluate model and print metrics."""
    print("\nEvaluating model...")

    y_pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    print(f"  MAE:  {mae:.2f} kg/ha")
    print(f"  RMSE: {rmse:.2f} kg/ha")
    print(f"  R2:   {r2:.4f}")

    # Save metrics
    metrics = {
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "r2_score": round(r2, 4),
        "test_samples": len(y_test),
    }
    metrics_path = output_dir / "yield_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"  Metrics saved to {metrics_path}")

    # Feature importances (from RF estimator)
    try:
        rf_model = None
        for name, estimator in model.named_estimators_.items():
            if name == "rf":
                rf_model = estimator
                break

        if rf_model is not None and hasattr(rf_model, "feature_importances_"):
            importances = rf_model.feature_importances_
            indices = np.argsort(importances)[::-1]

            print("\n  Feature Importances (from Random Forest):")
            for i, idx in enumerate(indices[:15]):
                if idx < len(feature_names):
                    print(f"    {i + 1}. {feature_names[idx]}: {importances[idx]:.4f}")

            # Plot feature importances
            try:
                import matplotlib
                matplotlib.use("Agg")
                import matplotlib.pyplot as plt

                top_n = min(15, len(feature_names))
                top_indices = indices[:top_n]
                top_names = [feature_names[i] for i in top_indices if i < len(feature_names)]
                top_values = [importances[i] for i in top_indices if i < len(feature_names)]

                fig, ax = plt.subplots(figsize=(10, 6))
                ax.barh(range(len(top_names)), top_values[::-1], color="#2ecc71", edgecolor="#27ae60")
                ax.set_yticks(range(len(top_names)))
                ax.set_yticklabels(top_names[::-1])
                ax.set_xlabel("Importance")
                ax.set_title("CropSense Yield Model - Feature Importances", fontsize=14)
                ax.grid(True, axis="x", alpha=0.3)
                plt.tight_layout()

                plot_path = output_dir / "feature_importances.png"
                plt.savefig(plot_path, dpi=150, bbox_inches="tight")
                plt.close()
                print(f"  Feature importance plot saved to {plot_path}")

            except ImportError:
                print("  matplotlib not available - skipping feature importance plot")

    except Exception as e:
        print(f"  Could not extract feature importances: {e}")

    return metrics


def generate_state_averages(df: pd.DataFrame, output_dir: Path):
    """Generate state x crop yield averages for comparison."""
    if "state" not in df.columns or "crop" not in df.columns:
        print("  Skipping state averages (state/crop columns not found)")
        return

    print("\nGenerating state averages...")
    averages = {}
    grouped = df.groupby(["state", "crop"])["yield_kg_per_ha"].mean()

    for (state, crop), avg in grouped.items():
        key = f"{state}_{crop}"
        averages[key] = round(avg)

    avg_path = output_dir.parent / "data" / "state_averages.json"
    avg_path.parent.mkdir(parents=True, exist_ok=True)
    with open(avg_path, "w") as f:
        json.dump(averages, f, indent=2)
    print(f"  State averages saved to {avg_path} ({len(averages)} entries)")


def main():
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    data_path = Path(args.data_path)
    if not data_path.exists():
        print(f"ERROR: Dataset not found: {data_path}")
        print("Download the Crop Yield Prediction Dataset first:")
        print("  kaggle datasets download -d patelris/crop-yield-prediction-dataset")
        print("  unzip crop-yield-prediction-dataset.zip -d ./data/")
        sys.exit(1)

    # Load and clean
    df = load_and_clean(str(data_path))

    # Generate state averages from data
    generate_state_averages(df, output_dir)

    # Prepare features
    X, y, feature_names, encoders = prepare_features(df, output_dir)

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=args.test_size,
        random_state=args.random_state,
    )
    print(f"\nTrain set: {X_train.shape[0]} samples")
    print(f"Test set:  {X_test.shape[0]} samples")

    # Train
    model = train_model(X_train, y_train, args.random_state)

    # Evaluate
    metrics = evaluate_model(model, X_test, y_test, feature_names, output_dir)

    # Save model
    model_path = output_dir / "cropsense_yield_model.pkl"
    joblib.dump(model, str(model_path))
    print(f"\nModel saved to {model_path}")

    # Final summary
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)
    print(f"Model: {model_path}")
    print(f"MAE:   {metrics['mae']} kg/ha")
    print(f"RMSE:  {metrics['rmse']} kg/ha")
    print(f"R2:    {metrics['r2_score']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
