# services/disease_service.py
import json
from pathlib import Path
import tensorflow as tf
from PIL import Image
import numpy as np

MODEL_PATH = Path("models/plant_disease_efficientnet_b1.keras")
CLASS_NAMES_PATH = Path("models/class_names.json")

model = tf.keras.models.load_model(MODEL_PATH)
with open(CLASS_NAMES_PATH, "r", encoding="utf-8") as f:
    class_names = json.load(f)

IMG_SIZE = (224, 224)

def parse_prediction(pred):
    label = pred["class"]
    if " - " in label:
        crop, disease = label.split(" - ", 1)
    else:
        crop, disease = label, ""
    return {"crop": crop, "disease": disease}

def predict_disease(img_path, top_k=3):
    # Load and preprocess image
    img = tf.keras.utils.load_img(img_path, target_size=IMG_SIZE)
    arr = tf.keras.utils.img_to_array(img)
    arr = tf.keras.applications.efficientnet.preprocess_input(arr[None, ...])  # expand + preprocess in one line

    # Predict probabilities
    preds = model.predict(arr, verbose=0)[0]

    # Get top-k indices sorted by confidence
    top_indices = np.argsort(preds)[-top_k:][::-1]

    # Build results
    results = []
    for i in top_indices:
        label = class_names[i]
        crop, disease = label.split(" - ", 1) if " - " in label else (label, "")
        results.append({
            "class": label,
            "confidence": float(preds[i]),
            "crop": crop,
            "disease": disease
        })
    return results
