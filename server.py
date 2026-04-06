from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import joblib
import socket
import requests
import whois
import math
from datetime import datetime
from urllib.parse import urlparse
from collections import Counter
import features_extraction

app = Flask(__name__)
CORS(app)

# 🔹 CONFIG
GOOGLE_API_KEY = "YOUR_API_KEY_HERE"

# 🔥 Load Tranco whitelist
trusted_domains = set()

def load_tranco():
    global trusted_domains
    try:
        with open("tranco.csv", "r") as f:
            for line in f:
                domain = line.strip().split(",")[-1]
                trusted_domains.add(domain)
        print(f"✅ Loaded {len(trusted_domains)} trusted domains")
    except Exception as e:
        print("❌ Error loading Tranco:", e)

load_tranco()

# 🔹 Load ML model
try:
    model = joblib.load("models/random_forest.pkl")
    print("✅ ML Model Loaded Successfully")
except Exception as e:
    print("❌ Error loading model:", e)
    model = None


# 🔥 Extract domain
def extract_domain(url):
    return urlparse(url).netloc.replace("www.", "")


# 🔥 Trusted domain check
def is_trusted_domain(url):
    return extract_domain(url) in trusted_domains


# 🔥 DNS Check
def is_domain_alive(url):
    try:
        socket.gethostbyname(extract_domain(url))
        return True
    except:
        return False


# 🔥 Google Safe Browsing
def check_google_safe_browsing(url):
    endpoint = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={GOOGLE_API_KEY}"

    body = {
        "client": {"clientId": "threatlens", "clientVersion": "1.0"},
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    }

    try:
        res = requests.post(endpoint, json=body)
        return "matches" in res.json()
    except:
        return False


# 🔥 WHOIS Age
def get_domain_age(url):
    try:
        w = whois.whois(extract_domain(url))
        creation_date = w.creation_date

        if isinstance(creation_date, list):
            creation_date = creation_date[0]

        if not creation_date:
            return None

        return (datetime.now() - creation_date).days
    except:
        return None


# 🔥 PRO ENTROPY
def calculate_entropy(text):
    counter = Counter(text)
    length = len(text)

    entropy = 0
    for count in counter.values():
        p = count / length
        entropy -= p * math.log2(p)

    return entropy


def entropy_risk_score(url):
    domain = extract_domain(url)
    entropy = calculate_entropy(domain)

    risk = 0

    if entropy > 4.0:
        risk += 50
    elif entropy > 3.5:
        risk += 30

    digits = sum(c.isdigit() for c in domain)
    if digits > 3:
        risk += 20

    hyphens = domain.count('-')
    if hyphens > 1:
        risk += 20

    if len(domain) > 20:
        risk += 15

    return risk, entropy


# 🔥 ADVANCED KEYWORD ENGINE
def get_keyword_risk(url):
    url = url.lower()

    high_risk = [
        "login", "signin", "verify", "account", "secure",
        "update", "password", "auth", "bank", "wallet",
        "payment", "billing", "invoice", "kyc", "otp",
        "refund", "claim", "bonus", "reward", "gift",
        "free", "win", "lottery", "prize", "cash",
        "paypal", "upi", "paytm", "phonepe", "gpay",
        "amazon", "netflix", "appleid", "microsoft",
        "facebook", "instagram", "whatsapp"
    ]

    phishing_words = [
        "phishing", "phish", "fake", "spoof", "clone"
    ]

    suspicious_patterns = [
        "secure-", "-secure", "login-", "-login",
        "verify-", "-verify", "update-", "-update"
    ]

    risk = 0

    for word in high_risk:
        if word in url:
            risk += 10

    for word in phishing_words:
        if word in url:
            risk += 50

    for pattern in suspicious_patterns:
        if pattern in url:
            risk += 15

    return risk


@app.route('/')
def home():
    return "ThreatLens Backend Running 🚀"


@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        url = data.get('url')

        if not url:
            return jsonify({"error": "No URL provided"}), 400

        print("\n🔍 Checking URL:", url)

        # 🔥 STEP 0: Tranco whitelist
        if is_trusted_domain(url):
            return jsonify({
                "url": url,
                "result": "Safe",
                "risk_score": 0,
                "reason": "Top trusted domain (Tranco)"
            })

        # 🔥 STEP 1: DNS
        if not is_domain_alive(url):
            return jsonify({
                "url": url,
                "result": "Malicious",
                "risk_score": 100,
                "reason": "Domain does not exist"
            })

        # 🔥 STEP 2: Google Safe Browsing
        if check_google_safe_browsing(url):
            return jsonify({
                "url": url,
                "result": "Malicious",
                "risk_score": 100,
                "reason": "Flagged by Google Safe Browsing"
            })

        # 🔥 STEP 3: ML
        features = features_extraction.main(url)
        features = np.array(features).reshape(1, -1)

        prediction = model.predict(features)[0]

        risk_score = None
        if hasattr(model, "predict_proba"):
            prob = model.predict_proba(features)[0][1]
            risk_score = round(prob * 100, 2)

        # 🔥 STEP 4: Keyword engine
        keyword_risk = get_keyword_risk(url)
        if keyword_risk > 0:
            risk_score = max(risk_score or 0, keyword_risk)

        # 🔥 STEP 5: WHOIS
        age = get_domain_age(url)
        if age is not None and age < 180:
            risk_score = max(risk_score or 0, 75)

        # 🔥 STEP 6: Entropy
        entropy_risk, entropy = entropy_risk_score(url)
        if entropy_risk > 50:
            risk_score = max(risk_score or 0, entropy_risk)

        # 🔥 FINAL DECISION
        if risk_score is not None:
            if risk_score < 80:
                result = "Safe"
            elif risk_score < 95:
                result = "Suspicious"
            else:
                result = "Malicious"
        else:
            result = "Safe" if prediction == 0 else "Malicious"

        return jsonify({
            "url": url,
            "result": result,
            "risk_score": risk_score,
            "domain_age_days": age,
            "entropy": round(entropy, 2)
        })

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)