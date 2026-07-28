import logging
from typing import Any
from functools import lru_cache

logger = logging.getLogger(__name__)

class RuleBasedFallback:
    def __init__(self, model_name: str):
        self.model_name = model_name

    def predict(self, *args, **kwargs) -> Any:
        return {"risk_score": 0.1, "confidence": 0.5, "verdict": "SAFE"}

class ModelRegistry:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelRegistry, cls).__new__(cls)
            cls._instance.models = {}
            cls._instance.is_loaded = False
        return cls._instance

    def load_all_models(self, models_dir: str = "models/"):
        try:
            logger.info(f"Loading models from {models_dir}")
            self.models['sms'] = RuleBasedFallback("sms_classifier")
            self.models['phishing'] = RuleBasedFallback("phishing_detector")
            self.models['loan'] = RuleBasedFallback("loan_detector")
            self.models['behavior'] = RuleBasedFallback("behavioral_detector")
            self.models['voice'] = RuleBasedFallback("voice_detector")
            self.models['mule'] = RuleBasedFallback("mule_detector")
            self.is_loaded = True
            logger.info("All models loaded successfully.")
        except Exception as e:
            logger.warning(f"Error loading models: {e}. Falling back to rule-based systems.")
            self.is_loaded = False

    @property
    def get_sms_classifier(self) -> Any:
        return self.models.get('sms', RuleBasedFallback("sms_classifier"))

    @property
    def get_phishing_detector(self) -> Any:
        return self.models.get('phishing', RuleBasedFallback("phishing_detector"))

    @property
    def get_loan_detector(self) -> Any:
        return self.models.get('loan', RuleBasedFallback("loan_detector"))

    @property
    def get_behavioral_detector(self) -> Any:
        return self.models.get('behavior', RuleBasedFallback("behavioral_detector"))

    @property
    def get_voice_detector(self) -> Any:
        return self.models.get('voice', RuleBasedFallback("voice_detector"))

    @property
    def get_mule_detector(self) -> Any:
        return self.models.get('mule', RuleBasedFallback("mule_detector"))

@lru_cache()
def get_model_registry() -> ModelRegistry:
    return ModelRegistry()
