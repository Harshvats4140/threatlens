import pandas as pd
import numpy as np
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score

# Import your feature extractor
import sys
sys.path.append("..")  # to access parent folder

import features_extraction

# 🔹 Dataset path (change if needed)
DATASET_PATH = "data/dataset.csv"

# 🔹 Model save path
MODEL_PATH = "../models/mlp_model.pkl"


def load_dataset():
    print("📂 Loading dataset...")
    df = pd.read_csv(DATASET_PATH)

    if 'url' not in df.columns or 'label' not in df.columns:
        raise Exception("Dataset must contain 'url' and 'label' columns")

    return df


def extract_features(df):
    print("⚙️ Extracting features...")

    X = []
    for url in df['url']:
        try:
            features = features_extraction.main(url)
            X.append(features)
        except Exception as e:
            print(f"❌ Error processing URL: {url}", e)

    return np.array(X)


def train_model(X, y):
    print("🤖 Training model...")

    model = MLPClassifier(
        hidden_layer_sizes=(100,),
        max_iter=300,
        random_state=42
    )

    model.fit(X, y)
    return model


def main():
    # Load data
    df = load_dataset()

    # Extract features
    X = extract_features(df)
    y = df['label']

    # Split
    print("🔀 Splitting dataset...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train
    model = train_model(X_train, y_train)

    # Evaluate
    print("📊 Evaluating model...")
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"✅ Accuracy: {round(acc * 100, 2)}%")

    # Save model
    print("💾 Saving model...")
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print("🎉 Model training complete!")
    print(f"📁 Saved at: {MODEL_PATH}")


if __name__ == "__main__":
    main()