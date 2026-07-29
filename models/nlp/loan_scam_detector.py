import os
import re
import joblib
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
from imblearn.over_sampling import SMOTE
import xgboost as xgb
from loguru import logger

LOAN_KEYWORDS = {
    'processing_fee': {
        'en': ['processing fee', 'advance payment', 'registration fee', 'upfront'],
        'hi': ['prakriya shulk', 'advance paise', 'registration fee', 'shuruaati paise'],
        'bn': ['processing fee', 'ogrim', 'registration fee'],
        'te': ['processing fee', 'mundastu', 'registration fee'],
        'ta': ['processing fee', 'munpanam', 'registration fee'],
        'mr': ['processing fee', 'advance paise', 'registration fee'],
        'gu': ['processing fee', 'advance paisa', 'registration fee'],
        'kn': ['processing fee', 'mundada hana', 'registration fee']
    },
    'no_cibil': {
        'en': ['no cibil', 'no credit check', 'bad credit ok'],
        'hi': ['cibil bina', 'cibil score ki jarurat nahi'],
        'bn': ['cibil lagbe na', 'bina cibil'],
        'te': ['cibil avasaram ledu', 'no cibil'],
        'ta': ['cibil thevai illai', 'no cibil'],
        'mr': ['cibil shivay', 'cibil nako'],
        'gu': ['cibil vagar', 'no cibil'],
        'kn': ['cibil illade', 'no cibil']
    }
}

FAKE_NBFCS = [
    'easy loan finance', 'instant cash nbfc', 'quick money lenders', 
    'bharat fast loan', 'pm mudra instant', 'trust finance india'
]

class LoanScamDetector:
    def __init__(self):
        self.model = xgb.XGBClassifier(eval_metric='logloss', random_state=42)
        self.is_trained = False

    def detect_fake_nbfc(self, text: str) -> Tuple[bool, str]:
        text_lower = text.lower()
        for nbfc in FAKE_NBFCS:
            if nbfc in text_lower:
                return True, nbfc
        suspicious_pattern = r'(pm|pradhan\s*mantri|sarkari|govt).*?(loan|finance|nbfc)'
        if re.search(suspicious_pattern, text_lower):
            return True, "Suspicious Govt/Finance Name Pattern"
        return False, ""

    def extract_features(self, text: str, lang: str) -> np.ndarray:
        text_lower = text.lower()
        lang_key = lang if lang in LOAN_KEYWORDS['processing_fee'] else 'en'
        proc_fee_words = LOAN_KEYWORDS['processing_fee'][lang_key]
        no_cibil_words = LOAN_KEYWORDS['no_cibil'][lang_key]
        advance_fee_mentioned = int(any(word in text_lower for word in proc_fee_words))
        guaranteed_approval = int('100% approval' in text_lower or 'guaranteed' in text_lower)
        no_cibil_check = int(any(word in text_lower for word in no_cibil_words))
        rbi_registered_mentioned = int('rbi' in text_lower and 'registered' in text_lower)
        processing_fee_mentioned = advance_fee_mentioned
        interest_rate_too_low = int(re.search(r'(0%|1%|2%)\s*interest', text_lower) is not None)
        contact_via_whatsapp_only = int('whatsapp only' in text_lower or 'only whatsapp' in text_lower)
        urgency_24h = int('24 hours' in text_lower or '24h' in text_lower or 'urgent' in text_lower)
        fake_nbfc_detected, _ = self.detect_fake_nbfc(text)
        fake_nbfc_name_detected = int(fake_nbfc_detected)
        return np.array([[
            advance_fee_mentioned, guaranteed_approval, no_cibil_check, 
            rbi_registered_mentioned, processing_fee_mentioned, interest_rate_too_low, 
            contact_via_whatsapp_only, urgency_24h, fake_nbfc_name_detected
        ]])

    def train(self, dataset_path: str):
        """
        Train on CFPB complaints.csv from /datasets/.
        Filters for loan/lending related complaints to build training data.
        """
        logger.info(f"Loading dataset from {dataset_path}...")

                                                                                
        if os.path.exists(dataset_path):
            try:
                                                                   
                raw = pd.read_csv(
                    dataset_path, encoding='latin-1',
                    on_bad_lines='skip', nrows=50000,
                    usecols=['Product', 'Consumer complaint narrative']
                )
                raw.columns = ['product', 'text']
                raw = raw.dropna(subset=['text'])

                                                               
                loan_keywords = [
                    'processing fee', 'advance fee', 'no credit check',
                    'guaranteed approval', 'upfront', 'no cibil', 'instant loan',
                    'payday', 'predatory', 'unauthorized charge'
                ]
                raw['label'] = raw['text'].str.lower().apply(
                    lambda t: 1 if any(kw in t for kw in loan_keywords) else 0
                )

                texts  = raw['text'].tolist()
                langs  = ['en'] * len(texts)
                labels = raw['label'].tolist()
                pos = sum(labels)
                logger.info(f"Loaded CFPB complaints: {len(texts)} rows | Loan scam: {pos} ({pos/len(texts):.2%})")

            except Exception as e:
                logger.warning(f"Could not parse CFPB dataset ({e}). Using mock data.")
                texts  = [
                    "Get 5 lakh loan with 0% interest. Pay processing fee upfront. No CIBIL.",
                    "Personal loan available. RBI registered NBFC. Standard interest rates apply.",
                    "Instant cash nbfc offers guaranteed approval via whatsapp only.",
                    "Bank loan approved. Visit branch for details."
                ]
                langs  = ['en', 'en', 'en', 'en']
                labels = [1, 0, 1, 0]
        else:
            logger.warning(f"Dataset not found at {dataset_path}. Using mock data.")
            texts  = [
                "Get 5 lakh loan with 0% interest. Pay processing fee upfront. No CIBIL.",
                "Personal loan available. RBI registered NBFC. Standard interest rates apply.",
                "Instant cash nbfc offers guaranteed approval via whatsapp only.",
                "Bank loan approved. Visit branch for details."
            ]
            langs  = ['en', 'en', 'en', 'en']
            labels = [1, 0, 1, 0]

        features_list = []
        for text, lang in zip(texts, langs):
            features = self.extract_features(text, lang)
            features_list.append(features[0])
        X = np.array(features_list)
        y = np.array(labels)
        logger.info("Applying SMOTE...")
        smote = SMOTE(random_state=42, k_neighbors=min(1, sum(y) - 1) if sum(y) > 1 else 1)
        try:
            X_resampled, y_resampled = smote.fit_resample(X, y)
        except Exception as e:
            logger.warning(f"SMOTE failed ({e}), using original data.")
            X_resampled, y_resampled = X, y
        logger.info("Training XGBoost...")
        self.model.fit(X_resampled, y_resampled)
        self.is_trained = True
        logger.info("Training completed.")

    def predict(self, text: str, lang: str) -> Dict[str, Any]:
        features = self.extract_features(text, lang)
        fake_nbfc_detected, nbfc_name = self.detect_fake_nbfc(text)
        if self.is_trained:
            probs = self.model.predict_proba(features)[0]
            is_scam = probs[1] > 0.5
            risk_score = float(probs[1])
        else:
            is_scam = bool(np.sum(features) > 2)
            risk_score = min(1.0, np.sum(features) * 0.2)
        warning_flags = []
        feature_names = [
            "Advance Fee Demanded", "Guaranteed Approval", "No CIBIL Check",
            "Claims RBI Registration", "Processing Fee", "Suspiciously Low Interest",
            "Whatsapp Only Contact", "Artificial Urgency", "Fake NBFC Detected"
        ]
        for i, val in enumerate(features[0]):
            if val == 1:
                warning_flags.append(feature_names[i])
        regulatory_note = ""
        if fake_nbfc_detected:
            regulatory_note = f"Alert: Mentions known fake or suspicious NBFC '{nbfc_name}'."
        elif is_scam:
            regulatory_note = "Warning: This offer violates RBI guidelines for digital lending."
        return {
            'is_scam': bool(is_scam),
            'risk_score': risk_score,
            'warning_flags': warning_flags,
            'regulatory_note': regulatory_note
        }

    def save(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({
            'model': self.model,
            'is_trained': self.is_trained
        }, path)
        logger.info(f"Model saved to {path}")

    def load(self, path: str):
        if os.path.exists(path):
            data = joblib.load(path)
            self.model = data['model']
            self.is_trained = data['is_trained']
            logger.info(f"Model loaded from {path}")
        else:
            logger.warning(f"Model file not found at {path}")

if __name__ == '__main__':
    _DATASET_DIR   = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'datasets')
    _COMPLAINTS_CSV = os.path.join(_DATASET_DIR, 'complaints.csv')                            

    detector = LoanScamDetector()
    detector.train(_COMPLAINTS_CSV)

    test_text = "Need money? PM Mudra Instant offers 5 lakh loan. No CIBIL. WhatsApp only. Pay processing fee."
    result = detector.predict(test_text, 'en')
    logger.info(f"Prediction result: {result}")

    save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'saved', 'loan_scam_detector.pkl')
    detector.save(save_path)

