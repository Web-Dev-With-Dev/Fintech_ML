import os
import logging
from typing import Any
from functools import lru_cache

logger = logging.getLogger(__name__)

class DynamicRuleFallback:
    """Smart fallback when ML models are not trained or saved models fail to load."""
    def __init__(self, model_type: str):
        self.model_type = model_type

    def predict(self, text: str, lang: str = "en", *args, **kwargs) -> Any:
        t = text.lower() if isinstance(text, str) else ""
        
                                                    
        scam_keywords = ['otp', 'winner', 'prize', 'lottery', 'arrest', 'blocked', 'kyc', 'suspend', 'urgent', 'turant', 'jald', 'inaam', 'jeet', 'bank account', 'update pan', 'aadhaar']
        found_keywords = [w for w in scam_keywords if w in t]
        has_url = 'http://' in t or 'https://' in t or '.com' in t or '.xyz' in t or 'bit.ly' in t
        has_phone = any(char.isdigit() for char in t) and len(t) > 10

        if found_keywords or (has_url and ('verify' in t or 'click' in t or 'login' in t)):
            risk_score = 0.92
            confidence = 0.95
            verdict = "SCAM"
        elif has_url or 'urgent' in t or 'update' in t:
            risk_score = 0.65
            confidence = 0.75
            verdict = "SUSPICIOUS"
        else:
            risk_score = 0.10
            confidence = 0.90
            verdict = "SAFE"

        return {
            "risk_score": risk_score,
            "confidence": confidence,
            "verdict": verdict,
            "label": verdict,
            "red_flags": found_keywords + (["Suspicious Link"] if has_url else []),
            "url_flags": ["Suspicious Link"] if has_url else [],
            "text_flags": ["Requests Action"] if found_keywords else [],
            "category": "PHISHING" if has_url else ("GENERAL_SCAM" if found_keywords else "SAFE")
        }

class ModelRegistry:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelRegistry, cls).__new__(cls)
            cls._instance.models = {}
            cls._instance.is_loaded = False
        return cls._instance

    def load_all_models(self, models_dir: str = "models/"):
        logger.info(f"Loading models from {models_dir}")
        saved_dir = os.path.join(models_dir, "saved")

                           
        try:
            from models.nlp.scam_sms_classifier import ScamSMSClassifier
            sms_model = ScamSMSClassifier()
            pkl_path = os.path.join(saved_dir, "scam_sms_classifier.pkl")
            if os.path.exists(pkl_path):
                sms_model.load(pkl_path)
                logger.info("Loaded scam_sms_classifier.pkl successfully.")
            self.models['sms'] = sms_model
        except Exception as e:
            logger.warning(f"Failed to load ScamSMSClassifier: {e}. Using DynamicRuleFallback.")
            self.models['sms'] = DynamicRuleFallback("sms")

                              
        try:
            from models.nlp.phishing_detector import PhishingDetector
            phish_model = PhishingDetector()
            pkl_path = os.path.join(saved_dir, "phishing_detector.pkl")
            if os.path.exists(pkl_path):
                phish_model.load(pkl_path)
                logger.info("Loaded phishing_detector.pkl successfully.")
            self.models['phishing'] = phish_model
        except Exception as e:
            logger.warning(f"Failed to load PhishingDetector: {e}. Using DynamicRuleFallback.")
            self.models['phishing'] = DynamicRuleFallback("phishing")

                               
        try:
            from models.nlp.loan_scam_detector import LoanScamDetector
            loan_model = LoanScamDetector()
            pkl_path = os.path.join(saved_dir, "loan_scam_detector.pkl")
            if os.path.exists(pkl_path):
                loan_model.load(pkl_path)
            self.models['loan'] = loan_model
        except Exception as e:
            self.models['loan'] = DynamicRuleFallback("loan")

                                        
        try:
            from models.behavioral.anomaly_detector import BehavioralAnomalyDetector
            beh_model = BehavioralAnomalyDetector()
            pkl_path = os.path.join(saved_dir, "behavioral_anomaly_detector.pkl")
            if os.path.exists(pkl_path):
                beh_model.load(pkl_path)
            self.models['behavior'] = beh_model
        except Exception as e:
            self.models['behavior'] = DynamicRuleFallback("behavior")

                                      
        self.models['voice'] = DynamicRuleFallback("voice")
        self.models['mule'] = DynamicRuleFallback("mule")

        self.is_loaded = True
        logger.info("All model loading checks complete.")

    @property
    def get_sms_classifier(self) -> Any:
        return self.models.get('sms', DynamicRuleFallback("sms"))

    @property
    def get_phishing_detector(self) -> Any:
        return self.models.get('phishing', DynamicRuleFallback("phishing"))

    @property
    def get_loan_detector(self) -> Any:
        return self.models.get('loan', DynamicRuleFallback("loan"))

    @property
    def get_behavioral_detector(self) -> Any:
        return self.models.get('behavior', DynamicRuleFallback("behavior"))

    @property
    def get_voice_detector(self) -> Any:
        return self.models.get('voice', DynamicRuleFallback("voice"))

    @property
    def get_mule_detector(self) -> Any:
        return self.models.get('mule', DynamicRuleFallback("mule"))

@lru_cache()
def get_model_registry() -> ModelRegistry:
    return ModelRegistry()

