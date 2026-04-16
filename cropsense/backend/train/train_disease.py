"""
CropSense - Disease Detection Model Training Script
====================================================
Trains a MobileNetV2-based CNN for plant disease classification
using the PlantVillage dataset (38+ classes across 14+ crops).

Two-phase transfer learning:
  Phase 1: Frozen base, train classification head only (15 epochs)
  Phase 2: Fine-tune last 30 layers of MobileNetV2 (10 epochs)

Usage:
  python train/train_disease.py --data_dir ./data/plantvillage
  python train/train_disease.py --data_dir ./data/plantvillage --gpu -1
"""

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np


def parse_args():
    parser = argparse.ArgumentParser(description="Train CropSense disease detection model")
    parser.add_argument(
        "--data_dir",
        type=str,
        default="./data/plantvillage",
        help="Path to PlantVillage dataset directory (with class subdirectories)",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./models",
        help="Directory to save trained model and artifacts",
    )
    parser.add_argument(
        "--batch_size", type=int, default=32, help="Training batch size"
    )
    parser.add_argument(
        "--phase1_epochs", type=int, default=15, help="Phase 1 training epochs"
    )
    parser.add_argument(
        "--phase2_epochs", type=int, default=10, help="Phase 2 fine-tuning epochs"
    )
    parser.add_argument(
        "--gpu",
        type=int,
        default=None,
        help="GPU device ID to use. Set to -1 to force CPU training.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # GPU configuration
    if args.gpu is not None:
        os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu)
        if args.gpu == -1:
            print("Forcing CPU training (CUDA_VISIBLE_DEVICES=-1)")

    import tensorflow as tf
    from tensorflow.keras.applications import MobileNetV2
    from tensorflow.keras.callbacks import (
        EarlyStopping,
        ModelCheckpoint,
        ReduceLROnPlateau,
    )
    from tensorflow.keras.layers import (
        BatchNormalization,
        Dense,
        Dropout,
        GlobalAveragePooling2D,
    )
    from tensorflow.keras.models import Model
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.preprocessing.image import ImageDataGenerator

    print(f"TensorFlow version: {tf.__version__}")
    print(f"GPU available: {len(tf.config.list_physical_devices('GPU')) > 0}")

    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not data_dir.exists():
        print(f"ERROR: Dataset directory not found: {data_dir}")
        print("Download the PlantVillage dataset first:")
        print("  kaggle datasets download -d emmarex/plantdisease")
        print("  unzip plantdisease.zip -d ./data/plantvillage")
        sys.exit(1)

    # ----------------------------------------------------------------
    # Data generators with augmentation
    # ----------------------------------------------------------------
    print("\n[1/5] Setting up data generators...")

    train_datagen = ImageDataGenerator(
        rescale=1.0 / 255,
        rotation_range=30,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        brightness_range=[0.8, 1.2],
        fill_mode="nearest",
        validation_split=0.2,
    )

    train_generator = train_datagen.flow_from_directory(
        data_dir,
        target_size=(224, 224),
        batch_size=args.batch_size,
        class_mode="categorical",
        subset="training",
        shuffle=True,
        seed=42,
    )

    val_generator = train_datagen.flow_from_directory(
        data_dir,
        target_size=(224, 224),
        batch_size=args.batch_size,
        class_mode="categorical",
        subset="validation",
        shuffle=False,
        seed=42,
    )

    num_classes = train_generator.num_classes
    class_names = list(train_generator.class_indices.keys())
    print(f"Found {train_generator.samples} training images")
    print(f"Found {val_generator.samples} validation images")
    print(f"Number of classes: {num_classes}")

    # Save class indices
    classes_path = output_dir.parent / "data" / "disease_classes.json"
    classes_path.parent.mkdir(parents=True, exist_ok=True)
    with open(classes_path, "w") as f:
        json.dump(class_names, f, indent=2)
    print(f"Class names saved to {classes_path}")

    # ----------------------------------------------------------------
    # Build model
    # ----------------------------------------------------------------
    print("\n[2/5] Building MobileNetV2 model...")

    base_model = MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights="imagenet",
    )
    # Phase 1: Freeze base, train head only
    base_model.trainable = False

    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = BatchNormalization()(x)
    x = Dense(512, activation="relu")(x)
    x = Dropout(0.4)(x)
    x = Dense(256, activation="relu")(x)
    x = Dropout(0.3)(x)
    output = Dense(num_classes, activation="softmax")(x)

    model = Model(inputs=base_model.input, outputs=output)

    model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    total_params = model.count_params()
    trainable_params = sum(
        tf.keras.backend.count_params(w) for w in model.trainable_weights
    )
    print(f"Total parameters: {total_params:,}")
    print(f"Trainable parameters (Phase 1): {trainable_params:,}")

    # ----------------------------------------------------------------
    # Phase 1: Train classification head
    # ----------------------------------------------------------------
    print(f"\n[3/5] Phase 1 - Training classification head ({args.phase1_epochs} epochs)...")

    phase1_checkpoint = str(output_dir / "best_phase1.h5")
    callbacks_p1 = [
        EarlyStopping(
            monitor="val_accuracy",
            patience=5,
            restore_best_weights=True,
            verbose=1,
        ),
        ModelCheckpoint(
            phase1_checkpoint,
            monitor="val_accuracy",
            save_best_only=True,
            verbose=1,
        ),
        ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.3,
            patience=3,
            min_lr=1e-7,
            verbose=1,
        ),
    ]

    history_p1 = model.fit(
        train_generator,
        epochs=args.phase1_epochs,
        validation_data=val_generator,
        callbacks=callbacks_p1,
        verbose=1,
    )

    print(f"Phase 1 best val_accuracy: {max(history_p1.history['val_accuracy']):.4f}")

    # ----------------------------------------------------------------
    # Phase 2: Fine-tune last 30 layers
    # ----------------------------------------------------------------
    print(f"\n[4/5] Phase 2 - Fine-tuning last 30 layers ({args.phase2_epochs} epochs)...")

    base_model.trainable = True
    for layer in base_model.layers[:-30]:
        layer.trainable = False

    trainable_params_p2 = sum(
        tf.keras.backend.count_params(w) for w in model.trainable_weights
    )
    print(f"Trainable parameters (Phase 2): {trainable_params_p2:,}")

    model.compile(
        optimizer=Adam(learning_rate=0.0001),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    final_model_path = str(output_dir / "cropsense_disease_model.h5")
    callbacks_p2 = [
        EarlyStopping(
            monitor="val_accuracy",
            patience=5,
            restore_best_weights=True,
            verbose=1,
        ),
        ModelCheckpoint(
            final_model_path,
            monitor="val_accuracy",
            save_best_only=True,
            verbose=1,
        ),
        ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.3,
            patience=3,
            min_lr=1e-8,
            verbose=1,
        ),
    ]

    history_p2 = model.fit(
        train_generator,
        epochs=args.phase2_epochs,
        validation_data=val_generator,
        callbacks=callbacks_p2,
        verbose=1,
    )

    print(f"Phase 2 best val_accuracy: {max(history_p2.history['val_accuracy']):.4f}")

    # Save final model
    model.save(final_model_path)
    print(f"Final model saved to {final_model_path}")

    # ----------------------------------------------------------------
    # Evaluation & reporting
    # ----------------------------------------------------------------
    print("\n[5/5] Evaluating model...")

    from sklearn.metrics import classification_report

    val_generator.reset()
    y_pred_probs = model.predict(val_generator, verbose=1)
    y_pred = np.argmax(y_pred_probs, axis=1)
    y_true = val_generator.classes[: len(y_pred)]

    report = classification_report(
        y_true,
        y_pred,
        target_names=class_names,
        output_dict=False,
        zero_division=0,
    )
    print("\nClassification Report:")
    print(report)

    # Save report to file
    report_path = output_dir / "classification_report.txt"
    with open(report_path, "w") as f:
        f.write("CropSense Disease Detection - Classification Report\n")
        f.write("=" * 60 + "\n\n")
        f.write(report)
    print(f"Classification report saved to {report_path}")

    # ----------------------------------------------------------------
    # Plot training curves
    # ----------------------------------------------------------------
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        # Combine histories
        acc = history_p1.history["accuracy"] + history_p2.history["accuracy"]
        val_acc = history_p1.history["val_accuracy"] + history_p2.history["val_accuracy"]
        loss = history_p1.history["loss"] + history_p2.history["loss"]
        val_loss = history_p1.history["val_loss"] + history_p2.history["val_loss"]
        epochs_range = range(1, len(acc) + 1)
        phase1_end = len(history_p1.history["accuracy"])

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        # Accuracy plot
        ax1.plot(epochs_range, acc, "b-", label="Training Accuracy")
        ax1.plot(epochs_range, val_acc, "r-", label="Validation Accuracy")
        ax1.axvline(x=phase1_end, color="gray", linestyle="--", label="Phase 2 Start")
        ax1.set_title("Model Accuracy", fontsize=14)
        ax1.set_xlabel("Epoch")
        ax1.set_ylabel("Accuracy")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Loss plot
        ax2.plot(epochs_range, loss, "b-", label="Training Loss")
        ax2.plot(epochs_range, val_loss, "r-", label="Validation Loss")
        ax2.axvline(x=phase1_end, color="gray", linestyle="--", label="Phase 2 Start")
        ax2.set_title("Model Loss", fontsize=14)
        ax2.set_xlabel("Epoch")
        ax2.set_ylabel("Loss")
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.suptitle("CropSense Disease Detection - Training Curves", fontsize=16)
        plt.tight_layout()

        curves_path = output_dir / "training_curves.png"
        plt.savefig(curves_path, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"Training curves saved to {curves_path}")

    except ImportError:
        print("matplotlib not available - skipping training curve plots")

    # Final summary
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)
    print(f"Model saved: {final_model_path}")
    print(f"Classes: {num_classes}")
    print(f"Phase 1 best accuracy: {max(history_p1.history['val_accuracy']):.4f}")
    print(f"Phase 2 best accuracy: {max(history_p2.history['val_accuracy']):.4f}")
    print("=" * 60)


if __name__ == "__main__":
    main()
