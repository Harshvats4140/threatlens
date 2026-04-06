import joblib
import pandas as pd
import features_extraction

# Load model
model = joblib.load("models/random_forest.pkl")

def check_url(url):
    # Extract features (your 20 features)
    features = features_extraction.main(url)

    # Convert to DataFrame (IMPORTANT)
    df = pd.DataFrame([features])

    # Predict
    prediction = model.predict(df)[0]

    print("URL:", url)
    print("Prediction:", "Phishing 🚨" if prediction == 1 else "Safe ✅")

# Test URLs
check_url("https://google.com")
check_url("http://free-login-bank.xyz")
check_url("https://chatgpt.com")
check_url("http://ascentcircle.in")
check_url("http://scam-ascentcircle.in")