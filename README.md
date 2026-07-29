# FinShield AI — Multi-Modal Privacy-Preserving Financial Scam Interceptor & Vernacular AI Shield for Rural India

> **A 2-Stage Layered AI/ML Architecture for Real-Time Financial Cyber Fraud Interception, Money Mule Ring Detection, Predatory Loan Auditing, Voice Call Transcription, and Vernacular Explainable AI (XAI) across 8 Indian Languages.**

---

## 📌 Executive Summary & Problem Statement

Over **500 million rural Indians** are entering the digital banking ecosystem for the first time via UPI, AEPS, and micro-lending apps. Fraudsters exploit low digital literacy, language barriers, and unfamiliarity with payment mechanics through:
- **UPI Money Mule Chains**: Funds routed through 5-10 intermediary accounts before withdrawal.
- **Electricity & KYC Urgency SMS**: Fake cutoff threats demanding immediate OTP or fee payment.
- **Predatory Loan Apps**: Demanding advance processing fees and illegally scraping phone contacts.
- **Impersonation Voice Calls**: Fake bank officers demanding card PINs or OTPs.

**FinShield AI** solves this with a **2-Stage Hybrid Architecture**:
1. **Stage 1 (ML & Deep Neural Net Inference)**: Real-time risk probability calculation using trained XGBoost, PyTorch Graph Attention Networks (GAT), OpenAI Whisper, Librosa Acoustic DSP, and Isolation Forests.
2. **Stage 2 (Vernacular XAI & Regulatory Guardrails)**: Maps feature weights into localized human-readable explanations across 8 Indian languages (Hindi, Hinglish, Tamil, Telugu, Bengali, Marathi, Gujarati, and English) with voice text-to-speech (TTS) and 1930 Cybercrime Helpline triggers.

---

## 🏗️ System Architecture Diagram

```mermaid
graph TD
    subgraph Frontend["React 18 + Vite Portal (http://localhost:5173)"]
        UI[Vishleshan Official Government Dashboard]
        SMS_UI[Vernacular SMS Interceptor]
        UPI_UI[UPI Mule Graph Visualizer]
        VOICE_UI[Voice Call Studio]
        LOAN_UI[Loan App Auditor]
        PANIC_UI[Behavioral Panic Shield]
        FL_UI[Federated Learning Map]
        HELP_UI[Helpline Directory & Kiosk]
    end

    subgraph API_Layer["FastAPI REST Backend (http://localhost:8000/api/v1)"]
        SMS_ROUTER[POST /analyze/sms]
        UPI_ROUTER[POST /analyze/upi]
        AUDIO_ROUTER[POST /analyze/audio]
        LOAN_ROUTER[POST /analyze/loan]
        BEHAVIOR_ROUTER[POST /analyze/behavior]
        HELP_ROUTER[GET /helplines]
        HEALTH_ROUTER[GET /health]
    end

    subgraph ML_Models["Trained Machine Learning & Deep Learning Models (models/saved/)"]
        XGB[scam_sms_classifier.pkl - XGBoost NLP]
        RF[phishing_detector.pkl - Random Forest]
        GAT[gat_model.pt - PyTorch Graph Attention Net]
        WHISPER[OpenAI Whisper Neural Net + Librosa DSP]
        LOAN_MODEL[loan_scam_detector.pkl - RBI Auditor]
        ISO[behavioral_anomaly_detector.pkl - Isolation Forest]
    end

    subgraph Privacy_XAI["Vernacular XAI Engine & Privacy Layer"]
        XAI[SHAP Vernacular Explainer - 8 Languages]
        FL[Flower Federated Learning - 5 Regional Nodes]
        DP[Gaussian Differential Privacy (ε=1.2, δ=10⁻⁵)]
    end

    UI --> API_Layer
    SMS_ROUTER --> XGB & RF --> XAI
    UPI_ROUTER --> GAT --> XAI
    AUDIO_ROUTER --> WHISPER --> XAI
    LOAN_ROUTER --> LOAN_MODEL --> XAI
    BEHAVIOR_ROUTER --> ISO --> XAI
    HELP_ROUTER --> HELP_UI
```

---

## 🧠 Machine Learning & Deep Learning Models Deep Dive

The platform integrates **6 trained machine learning and deep learning models** located at [models/saved/](file:///g:/Hackathon/Fintech_ML/models/saved):

| Model Binary File | File Size | Algorithm / Architecture | Key Function & Detection Target |
|-------------------|-----------|--------------------------|---------------------------------|
| [phishing_detector.pkl](file:///g:/Hackathon/Fintech_ML/models/saved/phishing_detector.pkl) | **22.3 MB** | Random Forest Classifier + TF-IDF Vectorizer | Detects malicious domain URLs, URL shorteners, and credential phishing links. |
| [behavioral_anomaly_detector.pkl](file:///g:/Hackathon/Fintech_ML/models/saved/behavioral_anomaly_detector.pkl) | **2.87 MB** | Isolation Forest Anomaly Detector | Flags odd-hour transfers (1 AM - 4 AM), velocity spikes, and full account drains under coercion. |
| [gat_model.pt](file:///g:/Hackathon/Fintech_ML/models/saved/gat_model.pt) | **2.16 MB** | PyTorch Geometric Graph Attention Network (GAT) | Evaluates directed transaction graphs; flags Star Hubs ($\ge 5$ senders) and Money Mule Chains (`RING-MULE-XXXX`). |
| [scam_sms_classifier.pkl](file:///g:/Hackathon/Fintech_ML/models/saved/scam_sms_classifier.pkl) | **410 KB** | XGBoost Classifier + Char-n-gram Vectorizer | Classifies SMS & WhatsApp text for OTP theft, electricity bill cutoffs, and KBC lottery scams. |
| [lstm_autoencoder.pt](file:///g:/Hackathon/Fintech_ML/models/saved/lstm_autoencoder.pt) | **131 KB** | PyTorch LSTM Autoencoder Neural Network | Computes sequence reconstruction errors to detect anomalous coerced transfer behavior. |
| `OpenAI Whisper + Librosa` | External Neural Net | Transformer Speech ASR + Acoustic DSP | Transcribes multilingual calls (Hindi, Tamil, Telugu, Bengali) and extracts pitch variance ($> 5000\text{ Hz}^2$) & speech velocity. |

---

## 🌐 Vernacular Explainable AI (XAI) & 8 Supported Languages

Raw machine learning models output decimal probabilities (e.g., `0.98`). First-time digital banking users require explanations in their native language.

### Supported Languages:
1. **Hindi (`hi`)**: हिंदी
2. **Hinglish (`hinglish`)**: Romanized Hindi
3. **Tamil (`ta`)**: தமிழ்
4. **Telugu (`te`)**: తెలుగు
5. **Bengali (`bn`)**: বাংলা
6. **Marathi (`mr`)**: मराठी
7. **Gujarati (`gu`)**: ગુજરાતી
8. **English (`en`)**: English

### SHAP Feature Weight Mapping (`nlp/xai_explainer.py`):
```python
# Converts SHAP tree feature importance into vernacular explanations
EXPLANATION_TEMPLATES = {
    'otp_keyword': {
        'hi': 'OTP मांगा गया है (यह बैंक कभी नहीं मांगता)',
        'bn': 'OTP চাওয়া হয়েছে (ব্যাঙ্ক কখনও এটি চায় না)',
        'mr': 'OTP विचारला आहे (बँक कधीही विचारत नाही)',
        'gu': 'OTP માંગવામાં આવ્યો છે (બેંક ક્યારેય માંગતી નથી)'
    }
}
```

---

## 🖥️ Frontend Web Application Features

The frontend is an **official government/enterprise portal dashboard** built with React 18, Vite, Lucide Icons, and custom CSS design tokens:

1. **Overview Analytics Dashboard**:
   - 100% Real Live Telemetry KPI Cards (`Total Scans Processed`, `Scams Intercepted`, `Mule Rings Tracked`, `API ML Latency`).
   - Dynamic `+ Create Scan Session` modal executing real-time backend API calls.
   - Dynamic `Recent Interceptions` table with `Open Session >` detail view.
   - One-click `Export data` CSV report downloader.
2. **Vernacular SMS & Phishing Scanner**:
   - Message textarea + quick scam presets (Electricity cutoff, KBC lottery, SBI KYC block).
   - Dedicated **Response Language Dropdown Picker** right on the card.
   - Risk Probability Gauge ($0 - 100\%$) and verdict badges (`SCAM`, `SUSPICIOUS`, `SAFE`).
   - Dual-language XAI Reasoning Box & **Text-To-Speech (TTS) Voice Read-Aloud**.
   - Direct **Dial 1930 Helpline** action button.
3. **UPI Money Mule Network Visualizer**:
   - Interactive transaction form (Sender VPA, Receiver VPA, Amount ₹, Message note).
   - Interactive SVG Node Graph Visualizer showing money mule chain hops and star topology hubs.
   - Fraud ring ID badge (`RING-MULE-XXXX`).
4. **Vernacular Voice Studio**:
   - Sample audio selector and base64 audio loader.
   - Audio waveform visualizer spectrum.
   - Synchronized OpenAI Whisper transcript with Librosa acoustic pitch/pause flags.
5. **Predatory Loan App Auditor**:
   - Loan offer SMS and app name audit form.
   - RBI Compliance Scorecard with green checkmarks and red warning flags in native languages.
   - RBI regulatory advisory banner.
6. **Behavioral Panic Shield**:
   - Session simulation sliders (transaction velocity, odd hour, full balance drain).
   - Isolation Forest panic state score dial.
   - Automatic emergency soft-block intervention modal popup.
7. **Federated Learning & Privacy Map**:
   - Regional node cards for **Uttar Pradesh, Bihar, West Bengal, Maharashtra, and Tamil Nadu**.
   - Differential Privacy budget bounds ($\epsilon = 1.2, \delta = 10^{-5}$) & India DPDPA Act 2023 compliance shield.
8. **Emergency Cyber Helpline Directory & Report Kiosk**:
   - Native helpline lookup (1930, RBI Ombudsman 14448, NPCI 1800-120-1740) translated into 8 languages.
   - Community scam reporting form.

---

## 📡 REST API Reference & Endpoints Cheatsheet

FastAPI Backend runs on **`http://localhost:8000/api/v1`**. Interactive Swagger docs at `http://localhost:8000/docs`.

### Request Keys Note:
All POST endpoints accept both **`lang`** and **`language`** keys (e.g., `"lang": "hi"` or `"language": "hi"`).

| Method | Endpoint | Description | Sample JSON Request Body |
|--------|----------|-------------|--------------------------|
| `POST` | `/api/v1/analyze/sms` | Analyzes SMS or message text using XGBoost & Random Forest | `{"text": "Your electricity will be cut off tonight at 9:30. Call 9876543210.", "lang": "hi"}` |
| `POST` | `/api/v1/analyze/upi` | Evaluates UPI transaction for mule chains & collect fraud | `{"sender_id": "victim@upi", "receiver_id": "mule_temp@upi", "amount": 45000.0, "timestamp": "2026-07-29T10:00:00Z", "message_text": "Pay fee"}` |
| `POST` | `/api/v1/analyze/loan` | Audits digital loan offers for advance fees & RBI rules | `{"offer_text": "Instant 10k approved without CIBIL. Pay 1500 fee.", "app_name": "QuickCash", "lang": "hi"}` |
| `POST` | `/api/v1/analyze/audio` | Transcribes audio via Whisper & extracts acoustic pitch flags | `{"audio_url": "bank_scam_call.wav", "lang": "hi"}` |
| `POST` | `/api/v1/analyze/behavior` | Isolation Forest session monitor for panic state coercion | `{"user_id": "u101", "session_data": {"transaction_velocity": 7, "odd_hour_transfer": true, "full_balance_drain": true}, "lang": "hi"}` |
| `GET` | `/api/v1/helplines` | Retrieves 24x7 cybercrime helplines in native languages | `GET /api/v1/helplines?language=hi` |
| `GET` | `/api/v1/health` | System health status & ML models loaded check | `GET /api/v1/health` |

---

## 📂 Project Directory Structure

```
FinShield_ML/
├── api/                        # FastAPI REST API Backend
│   ├── main.py                 # Core FastAPI App & Middleware
│   ├── schemas.py              # Pydantic Request/Response Schemas
│   ├── dependencies.py         # ModelRegistry & Dynamic Rules Fallback
│   └── routers/                # Endpoint Routers
│       ├── sms_check.py        # SMS & Phishing NLP Router
│       ├── upi_check.py        # UPI Mule GAT Network Router
│       ├── loan_check.py       # Loan App Auditor Router
│       ├── voice_check.py      # Voice Whisper & Acoustic DSP Router
│       ├── behavioral.py       # Isolation Forest Behavior Router
│       └── helplines.py        # Vernacular Helplines Router
├── models/                     # ML / DL Model Architectures & Binary Weights
│   ├── saved/                  # Trained Model Binary Files (.pkl, .pt)
│   │   ├── scam_sms_classifier.pkl
│   │   ├── phishing_detector.pkl
│   │   ├── loan_scam_detector.pkl
│   │   ├── behavioral_anomaly_detector.pkl
│   │   ├── gat_model.pt
│   │   └── lstm_autoencoder.pt
│   ├── nlp/                    # NLP Trainers
│   ├── graph/                  # PyTorch Geometric GAT Architecture
│   ├── audio/                  # Whisper Transcriber & Librosa DSP
│   ├── behavioral/             # Isolation Forest Anomaly Trainer
│   └── federated/              # Flower (flwr) Federated Learning Simulation
├── nlp/                        # Vernacular NLP & XAI Explainer
│   ├── xai_explainer.py        # SHAP Vernacular Explainer (8 Languages)
│   └── language_detector.py    # Indic Language Detector
├── frontend/                   # React 18 + Vite Web Application
│   ├── src/
│   │   ├── App.jsx             # Main App Layout
│   │   ├── index.css           # Official Government Enterprise Design System
│   │   ├── components/         # Feature Components
│   │   │   ├── Sidebar.jsx     # Left Vertical Navigation
│   │   │   ├── Overview.jsx    # Live Telemetry Analytics Dashboard
│   │   │   ├── SMSScanner.jsx  # SMS & Phishing Scanner
│   │   │   ├── UPIGraphVisualizer.jsx # UPI Mule Graph Visualizer
│   │   │   ├── VoiceStudio.jsx # Voice Call Studio
│   │   │   ├── LoanAuditor.jsx# Predatory Loan App Auditor
│   │   │   ├── PanicShield.jsx# Behavioral Panic Shield
│   │   │   ├── FederatedDashboard.jsx # FL & Privacy Map
│   │   │   └── HelplineKiosk.jsx # Helpline Directory & Kiosk
│   │   └── utils/
│   │       └── scanLogger.js   # Live Scan Telemetry Logger
└── requirements.txt            # Python Dependencies
```

---

## ⚡ Installation & Execution Guide

### Prerequisites
- **Python**: 3.10 or later
- **Node.js**: v18 or later

### Step 1: Environment & Python Backend Setup

1. Open terminal in the project root folder:
   ```bash
   cd g:\Hackathon\Fintech_ML
   ```

2. Create and activate Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   ```

3. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Launch the FastAPI Backend Server:
   ```bash
   uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   *The backend will start at `http://localhost:8000`. You can test API endpoints at `http://localhost:8000/docs`.*

---

### Step 2: Frontend Web Application Setup

1. Open a new terminal window and navigate to `frontend/`:
   ```bash
   cd g:\Hackathon\Fintech_ML\frontend
   ```

2. Install Node dependencies:
   ```bash
   npm install
   ```

3. Start the Vite Frontend Development Server:
   ```bash
   npm run dev
   ```

4. Open your browser and navigate to:
   👉 **`http://localhost:5173/`**

---

## ⚖️ Regulatory & Privacy Compliance

- **India DPDPA (Digital Personal Data Protection Act, 2023)**: Satisfies Section 6 by keeping raw financial transaction data local to regional nodes.
- **RBI Cyber Security Framework**: Implements automated behavioral anomaly monitoring for odd-hour transactions and account drains.
- **NPCI Fraud Guidelines**: Directly surfaces 1930 Cybercrime Portal and RBI Ombudsman helplines across all 8 Indian languages.

---

## 📜 License

Distributed under the **MIT License**. Free for research, government, and educational use.
