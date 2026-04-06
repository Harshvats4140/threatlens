import sys
import os

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import features_extraction  # ✅ IMPORTANT

# 🔹 Dataset path
DATASET_PATH = "data/dataset.csv"

# 🔹 Model save path
MODEL_PATH = "../models/random_forest.pkl"


def load_dataset():
    print("📂 Loading dataset...")
    df = pd.read_csv(DATASET_PATH)

    # Normalize column names
    df.columns = [col.lower() for col in df.columns]

    # ✅ Check required columns
    if 'url' not in df.columns or 'label' not in df.columns:
        raise Exception("Dataset must contain 'url' and 'label' columns")

    # 🔥 Ensure label is numeric
    df['label'] = df['label'].replace({
        'legitimate': 0,
        'phishing': 1,
        'benign': 0,
        'malicious': 1
    })

    return df


def extract_features(df):
    print("⚙️ Extracting features from URLs...")

    X = []
    valid_labels = []

    for i, row in df.iterrows():
        url = row['url']
        label = row['label']

        try:
            features = features_extraction.main(url)
            X.append(features)
            valid_labels.append(label)
        except Exception as e:
            print(f"❌ Error processing: {url}")

    return np.array(X), np.array(valid_labels)


def main():
    df = load_dataset()

    # 🔥 Convert URLs → features
    X, y = extract_features(df)

    print("🔀 Splitting dataset...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print("🌲 Training Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        class_weight='balanced',
        random_state=42
    )

    model.fit(X_train, y_train)

    print("📊 Evaluating model...")
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print(f"✅ Accuracy: {round(accuracy * 100, 2)}%")

    print("💾 Saving model...")
    joblib.dump(model, MODEL_PATH)

    print(f"🎉 Model saved at: {MODEL_PATH}")


if __name__ == "__main__":
    main()