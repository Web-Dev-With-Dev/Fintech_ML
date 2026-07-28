# FinShield AI

FinShield AI is a multi-modal, privacy-preserving financial scam detection platform built specifically for first-time digital banking users in rural India. The system detects scam calls, fake UPI payment requests, phishing messages, and predatory loan offers in eight Indian languages using a layered stack of machine learning models, graph analytics, federated learning, and explainable AI.

---

## Problem Statement

Over 500 million rural Indians are entering the digital banking ecosystem for the first time. This population is disproportionately targeted by financial fraudsters who exploit low digital literacy, language barriers, and unfamiliarity with UPI mechanics. Existing fraud detection systems operate at the bank or NPCI level and are invisible to the end user. There is no system that gives a rural user, in their own language, a clear and immediate signal that they are being scammed.

FinShield AI addresses this gap with a backend intelligence platform that can be integrated into banking apps, CSC kiosks, helpline systems, or telecom SMS filters.

---

## Core Innovations

### 1. Vernacular Voice Scam Interceptor

The majority of rural scam victims are targeted via phone calls, not SMS. This module transcribes call audio in real time using OpenAI Whisper across eight Indian languages, then runs the transcript through the scam NLP classifier. Acoustic features including speech rate, pitch variance, and pause frequency are extracted using librosa and combined with the text classification score to produce a final verdict. This gives a scam probability during or immediately after a call.

### 2. UPI Fraud Graph Neural Network

Standard ML models evaluate each transaction in isolation. Rural scam networks use money mule chains where funds are routed through five to ten intermediary accounts before being withdrawn. This module builds a directed transaction graph using NetworkX and trains a Graph Attention Network on it. The GAT assigns attention weights to high-risk nodes and detects structural fraud signatures including star topology (one scammer receiving from many victims), rapid multi-hop forwarding chains, and full account drain events within a short time window.

### 3. Federated Learning with Differential Privacy

Training fraud detection models requires access to sensitive transaction and message data. FinShield uses Federated Learning via the Flower framework to train models across five regional nodes representing Uttar Pradesh, Bihar, Tamil Nadu, West Bengal, and Maharashtra without any raw data leaving the local node. Only model gradients are shared, and Gaussian noise is added for differential privacy guarantees. This architecture is compliant with India's Digital Personal Data Protection Act (DPDPA) by design.

### 4. Explainable AI in Local Languages

A confidence score means nothing to a first-time smartphone user. FinShield uses SHAP (SHapley Additive Explanations) to identify which features drove a scam prediction, then maps those SHAP values to human-readable explanations in eight languages. For example, a Hindi-speaking user receives: "This message is dangerous because: an OTP was requested, your account was threatened with closure, and the call came from an unknown number." The explanation is also formatted as voice-ready text for text-to-speech integration.

### 5. Behavioral Panic State Detector

Scammers create artificial urgency to override rational decision-making. This module detects behavioral anomalies that indicate a user is in a compromised or panic state. An Isolation Forest model flags unusual transaction patterns, and an LSTM Autoencoder analyzes sequences of transactions for reconstruction errors that indicate anomalous behavior. Signals include transaction velocity spikes, round-number transfers to first-time recipients, and large transfers occurring during odd hours. When a panic state is detected, the system sets intervention_required to true, which can trigger a soft block or human callback.

### 6. Synthetic Multilingual Scam Data Engine

No labeled Indian-language scam dataset exists publicly. FinShield includes a template-based synthetic data generator that produces 50,000 labeled SMS and message samples across seven scam categories and eight languages with realistic noise injection including typos, emoji insertion, and number substitution. This dataset is structured for open-source release as a contribution to the Indian NLP research community.

---

## Supported Languages

Hindi, English, Hinglish (Romanized Hindi), Tamil, Telugu, Bengali, Marathi, Gujarati

---

## Scam Categories Detected

- OTP theft via impersonation of bank officials
- Account block or KYC expiry threats
- Prize and lottery fraud
- Fake UPI collect requests disguised as receive-money flows
- Phishing links in SMS and WhatsApp messages
- Instant loan apps demanding advance processing fees
- Government scheme impersonation fraud

---

## Project Structure

```
FinShield/
|
|-- requirements.txt
|-- README.md
|-- demo.py
|
|-- data_engine/
|   |-- synthetic_generator.py
|   |-- upi_graph_generator.py
|   |-- behavioral_generator.py
|   |-- datasets/
|
|-- nlp/
|   |-- language_detector.py
|   |-- preprocessor.py
|   |-- transliterator.py
|   |-- xai_explainer.py
|
|-- models/
|   |-- nlp/
|   |   |-- scam_sms_classifier.py
|   |   |-- phishing_detector.py
|   |   |-- loan_scam_detector.py
|   |-- graph/
|   |   |-- transaction_graph.py
|   |   |-- gat_model.py
|   |   |-- mule_detector.py
|   |-- behavioral/
|   |   |-- anomaly_detector.py
|   |   |-- lstm_autoencoder.py
|   |-- audio/
|   |   |-- voice_transcriber.py
|   |   |-- voice_scam_detector.py
|   |-- federated/
|   |   |-- fl_client.py
|   |   |-- fl_server.py
|   |   |-- simulate_federation.py
|   |-- saved/
|
|-- api/
|   |-- main.py
|   |-- schemas.py
|   |-- dependencies.py
|   |-- routers/
|       |-- sms_check.py
|       |-- upi_check.py
|       |-- voice_check.py
|       |-- loan_check.py
|       |-- behavioral.py
|       |-- helplines.py
|
|-- evaluate/
    |-- benchmark.py
    |-- cross_lingual_test.py
    |-- fairness_audit.py
    |-- outputs/
```

---

## Quick Start

### Prerequisites

Python 3.10 or later is required. A CUDA-capable GPU is recommended for MuRIL and Whisper inference but not required.

### Installation

```bash
pip install -r requirements.txt
```

### Step 1: Generate Datasets

```bash
python data_engine/synthetic_generator.py
python data_engine/upi_graph_generator.py
python data_engine/behavioral_generator.py
```

Output CSV and graph files are written to `data_engine/datasets/`.

### Step 2: Train Models

```bash
python models/nlp/scam_sms_classifier.py
python models/nlp/phishing_detector.py
python models/nlp/loan_scam_detector.py
python models/behavioral/anomaly_detector.py
python models/behavioral/lstm_autoencoder.py
python models/graph/gat_model.py
```

Trained models are saved to `models/saved/`.

### Step 3: Run Federated Learning Simulation

```bash
python models/federated/simulate_federation.py
```

This runs a five-node in-process simulation of federated training across regional nodes and generates a convergence plot at `evaluate/outputs/fl_convergence_plot.png`.

### Step 4: Run the Demo

```bash
python demo.py
```

The demo script runs seven end-to-end scenarios covering all six innovations with formatted console output.

### Step 5: Start the API Server

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

The interactive API documentation is available at `http://localhost:8000/docs`.

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/analyze/sms | Classify an SMS or message as scam, phishing, or safe |
| POST | /api/v1/analyze/upi | Analyze a UPI transaction for fraud and mule chain risk |
| POST | /api/v1/analyze/audio | Upload a call recording for voice scam detection |
| POST | /api/v1/analyze/loan | Evaluate a loan offer message for predatory signals |
| POST | /api/v1/analyze/behavior | Check a user session for panic-state behavioral anomalies |
| GET | /api/v1/helplines | Retrieve emergency helpline numbers by language or state |
| GET | /api/v1/health | Health check and model load status |

### Example Request

```bash
curl -X POST http://localhost:8000/api/v1/analyze/sms \
  -H "Content-Type: application/json" \
  -d '{"text": "Aapka SBI khata band ho jayega. Abhi OTP den.", "language": "hi"}'
```

### Example Response

```json
{
  "verdict": "SCAM",
  "confidence": 0.97,
  "risk_score": 0.97,
  "category": "otp_fraud",
  "red_flags": ["OTP requested", "account block threat", "urgency language"],
  "explanation_local": "Yeh sandesh khatarnak hai: OTP manga gaya hai aur khate band hone ki dhamki di gayi hai.",
  "explanation_en": "This message is dangerous: OTP was requested and account closure was threatened.",
  "action_advice": "Kisi ko OTP na den. 1930 par call karen.",
  "helpline": "1930"
}
```

---

## Evaluation

Run the full benchmark suite after training all models:

```bash
python evaluate/benchmark.py
```

This generates a markdown report with per-model and per-language precision, recall, and F1 scores, confusion matrices, and ROC curves saved to `evaluate/outputs/`.

Run cross-lingual generalization tests:

```bash
python evaluate/cross_lingual_test.py
```

Run the fairness and bias audit:

```bash
python evaluate/fairness_audit.py
```

The fairness audit checks for performance disparities across language groups and scam categories and includes notes on DPDPA compliance.

---

## Model Performance Targets

| Model | Target F1 | Target Recall | Design Priority |
|-------|-----------|---------------|-----------------|
| Scam SMS Classifier | 0.93 | 0.96 | High recall to never miss a scam |
| Phishing Detector | 0.91 | 0.95 | High recall |
| Loan Scam Detector | 0.90 | 0.94 | High recall |
| UPI Fraud GNN | 0.95 | 0.97 | High precision to avoid blocking legitimate transfers |
| Behavioral Anomaly Detector | 0.88 | 0.92 | Balanced |
| Voice Scam Detector | 0.87 | 0.91 | High recall |

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Core ML | scikit-learn, XGBoost, PyTorch |
| Graph ML | PyTorch Geometric, NetworkX |
| NLP | MuRIL (HuggingFace Transformers), langdetect, indic-transliteration |
| Speech Recognition | OpenAI Whisper |
| Audio Features | librosa |
| Federated Learning | Flower (flwr) |
| Explainability | SHAP |
| API | FastAPI, Uvicorn, Pydantic v2 |
| Data | pandas, numpy |
| Visualization | matplotlib, seaborn, plotly |

---

## Regulatory Alignment

The system is designed with the following regulatory considerations:

- **DPDPA (Digital Personal Data Protection Act, 2023):** The federated learning architecture ensures no raw personal data is transmitted to a central server. Only anonymized model gradients are shared.
- **RBI Guidelines on Cyber Security:** The behavioral anomaly module aligns with RBI's directive for banks to implement transaction monitoring for unusual patterns.
- **TRAI DLT Framework:** The SMS phishing detector is structured to complement TRAI's Distributed Ledger Technology framework for telecom fraud detection.
- **NPCI Fraud Reporting:** The helplines endpoint surfaces NPCI and Cyber Crime (1930) contact information in the user's preferred language at the point of every fraud alert.

---

## Emergency Helplines

| Service | Number |
|---------|--------|
| National Cyber Crime Helpline | 1930 |
| National Cyber Crime Reporting Portal | cybercrime.gov.in |
| RBI Banking Ombudsman | 14448 |
| NPCI Helpline | 1800-120-1740 |

---

## Roadmap

- Integration with TRAI's Chakshu portal for real-time scam number reporting
- On-device inference using ONNX-quantized models for offline rural connectivity
- IVR-based voice interface for feature phone users (UPI 123PAY integration)
- Expansion to Odia, Punjabi, and Assamese languages
- Community threat intelligence feed where verified scam reports improve the central model via federated updates
