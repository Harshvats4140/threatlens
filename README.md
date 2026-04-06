# 🛡️ ThreatLens – AI-Powered URL Safety Detector

ThreatLens is a real-time cybersecurity tool that detects phishing and malicious URLs using Machine Learning and intelligent rule-based analysis. It integrates a Flask backend with a Chrome Extension to provide instant website safety feedback.

---

## 🚀 Features

* 🔍 Real-time URL scanning via Chrome Extension
* 🤖 Machine Learning-based phishing detection (Random Forest)
* 🧠 Hybrid detection system (ML + Rule-based)
* 🌐 DNS validation (detects fake/non-existent domains)
* ⚠️ Suspicious keyword detection (e.g., "free", "win", "login")
* 📊 Risk scoring system (Safe / Suspicious / Malicious)
* ⚡ Fast and lightweight API (Flask backend)

---

## 🧠 How It Works

```
User visits website → Extension captures URL  
→ Sends to Flask API  
→ Feature Extraction  
→ ML Model Prediction  
→ Rule-based checks (DNS + keywords)  
→ Final Risk Score + Result  
→ Displayed in Extension UI
```

---

## 🏗️ Project Structure

```
URLDETECTION/
│
├── server.py                # Flask backend API
├── features_extraction.py  # URL feature engineering
├── models/
│   └── random_forest.pkl   # Trained ML model
│
├── train/
│   ├── train_rf.py         # Model training script
│   └── data/
│       └── dataset.csv     # URL dataset
│
├── extension/
│   ├── manifest.json       # Chrome extension config
│   ├── popup.html          # UI
│   ├── popup.js            # Logic
│   ├── style.css           # Styling
│   └── icon.jpg            # Extension icon
│
└── test_url.py             # Local testing script
```

---

## ⚙️ Installation & Setup

### 🔹 1. Clone Repository

```bash
git clone https://github.com/your-username/threatlens.git
cd threatlens
```

---

### 🔹 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 🔹 3. Train Model

```bash
cd train
python train_rf.py
```

---

### 🔹 4. Run Backend Server

```bash
cd ..
python server.py
```

Server runs at:

```
http://127.0.0.1:5000
```

---

### 🔹 5. Load Chrome Extension

1. Open Chrome
2. Go to:

```
chrome://extensions/
```

3. Enable **Developer Mode**
4. Click **Load Unpacked**
5. Select:

```
extension/
```

---

## 🧪 Usage

1. Open any website
2. Click the ThreatLens extension
3. Click **Scan URL**
4. View:

   * ✅ Safe
   * ⚠️ Suspicious
   * 🚨 Malicious
   * 📊 Risk Score

---

## 🧠 Detection Logic

ThreatLens uses a **hybrid approach**:

### 🔹 1. Machine Learning

* Random Forest Classifier
* Trained on URL-based features
* Detects phishing patterns

### 🔹 2. Rule-Based Checks

#### ✅ DNS Validation

* Detects non-existent domains
* Marks as **Malicious**

#### ⚠️ Suspicious Keywords

Detects terms like:

```
free, win, login, verify, bank, secure, reward
```

#### 🔐 HTTPS Check (Optional)

* Penalizes non-secure URLs

---

## 📊 Risk Scoring

| Score  | Result        |
| ------ | ------------- |
| 0–79   | ✅ Safe        |
| 80–94  | ⚠️ Suspicious |
| 95–100 | 🚨 Malicious  |

---

## 🔥 Example

| URL                        | Result                        |
| -------------------------- | ----------------------------- |
| https://google.com         | ✅ Safe                        |
| http://free-login-bank.xyz | 🚨 Malicious                  |
| http://winfreephone.com    | 🚨 Malicious (DNS + keywords) |

---

## ⚡ Future Enhancements

* 🔴 Auto-block malicious websites
* 🌐 WHOIS domain age detection
* 📡 Integration with phishing APIs (PhishTank, OpenPhish)
* ☁️ Firebase logging & analytics
* 📊 Admin dashboard
* 🧠 Deep Learning model (LSTM / Transformer)

---

## 🛡️ Tech Stack

* **Frontend:** HTML, CSS, JavaScript (Chrome Extension)
* **Backend:** Python, Flask
* **ML:** Scikit-learn (Random Forest)
* **Data:** Custom + phishing datasets

---

## 👨‍💻 Author

**Harshvardhan Vats**
Cybersecurity Enthusiast | Developer

---

## ⭐ Contribute

Pull requests are welcome!
For major changes, open an issue first.

---

## 📜 License

This project is licensed under the MIT License.

---

## 🔥 Final Note

ThreatLens is not just a project — it’s a **real-time cybersecurity system** designed to protect users from phishing attacks using AI.

---
