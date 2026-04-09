from flask import Flask, request, jsonify
from flask_cors import CORS
from difflib import SequenceMatcher
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
GOOGLE_API_KEY = "AIzaSyC__G72Iok1TbdXiBjZ9QfEUmOYKiLn-3o"

# ================== LOAD TRUSTED DOMAINS ==================

trusted_domains = set()

def load_tranco():
    global trusted_domains
    try:
        with open("tranco.csv", "r") as f:
            for line in f:
                domain = line.strip().split(",")[-1].lower()
                trusted_domains.add(domain)
        print(f"✅ Loaded {len(trusted_domains)} trusted domains")
    except Exception as e:
        print("❌ Error loading Tranco:", e)

load_tranco()

# ================== LOAD MODEL ==================

try:
    model = joblib.load("models/random_forest.pkl")
    print("✅ ML Model Loaded Successfully")
except Exception as e:
    print("❌ Error loading model:", e)
    model = None


# ================== HELPERS ==================

def extract_domain(url):
    return urlparse(url).netloc.replace("www.", "").lower()

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def is_trusted_domain(url):
    domain = extract_domain(url)
    return any(domain == td or domain.endswith("." + td) for td in trusted_domains)

def is_domain_alive(url):
    try:
        socket.gethostbyname(extract_domain(url))
        return True
    except:
        return False

# ✅ FIXED FAKE BRAND DETECTION
def is_fake_brand(url):
    brands = ["google", "facebook", "amazon", "paypal", "microsoft"]

    domain = extract_domain(url)

    for brand in brands:
        # ✅ Real domain allowed
        if domain == f"{brand}.com":
            return False

        # 🚨 Fake domains like facebook-login.xyz
        if brand in domain and not domain.endswith(f"{brand}.com"):
            return True

        # 🚨 Similar domains like googie.com
        if similarity(domain, f"{brand}.com") > 0.8 and domain != f"{brand}.com":
            return True

    return False


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

    if domain.count('-') > 1:
        risk += 20

    if len(domain) > 20:
        risk += 15

    return risk, entropy


def get_keyword_risk(url):
    url = url.lower()

    keywords = [
        "login","signin","verify","account","secure","update","password",
        "bank","wallet","payment","billing","invoice","otp",
        "refund","claim","bonus","reward","gift","free","win","lottery",
        "paypal","upi","paytm","gpay","amazon","netflix","appleid","facebook"
    ]

    risk = 0
    for word in keywords:
        if word in url:
            risk += 10

    return risk


# ================== ROUTES ==================

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

        # 🟢 1. WHITELIST FIRST (CRITICAL FIX)
        if is_trusted_domain(url):
            return jsonify({
                "url": url,
                "result": "Safe",
                "risk_score": 0,
                "reason": "Trusted domain (Tranco)"
            })

        # 🚨 2. Fake brand detection
        if is_fake_brand(url):
            return jsonify({
                "url": url,
                "result": "Malicious",
                "risk_score": 100,
                "reason": "Fake brand domain"
            })

        # 🚨 3. DNS check
        if not is_domain_alive(url):
            return jsonify({
                "url": url,
                "result": "Malicious",
                "risk_score": 100,
                "reason": "Domain not found"
            })

        # 🚨 4. Google Safe Browsing
        if check_google_safe_browsing(url):
            return jsonify({
                "url": url,
                "result": "Malicious",
                "risk_score": 100,
                "reason": "Flagged by Google"
            })

        # 🤖 5. ML Prediction
        features = features_extraction.main(url)
        features = np.array(features).reshape(1, -1)

        prediction = model.predict(features)[0]

        risk_score = 0
        if hasattr(model, "predict_proba"):
            risk_score = round(model.predict_proba(features)[0][1] * 100, 2)

        # 🔥 6. Keyword risk
        risk_score = max(risk_score, get_keyword_risk(url))

        # 🔥 7. Domain age
        age = get_domain_age(url)
        if age and age < 180:
            risk_score = max(risk_score, 75)

        # 🔥 8. Entropy
        entropy_risk, entropy = entropy_risk_score(url)
        risk_score = max(risk_score, entropy_risk)

        # 🎯 FINAL DECISION
        if risk_score < 80:
            result = "Safe"
        elif risk_score < 95:
            result = "Suspicious"
        else:
            result = "Malicious"

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