import os
import re
import joblib
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from loguru import logger

SUSPICIOUS_TLDS = ['.ru', '.xyz', '.tk', '.cn', '.top', '.info', '.club', '.gq', '.ml']
URL_SHORTENERS = ['bit.ly', 'tinyurl.com', 't.co', 'goo.gl', 'ow.ly', 'is.gd', 'buff.ly', 'adf.ly']

PII_KEYWORDS = {
    'en': ['password', 'kyc', 'pan', 'aadhaar', 'update', 'verify', 'account', 'login', 'dob', 'pin'],
    'hi': ['kyc', 'pan', 'aadhaar', 'update', 'verify', 'khaata', 'password', 'pin', 'jankari'],
}

PHISHING_CATEGORIES = ['kyc_fraud', 'prize_lottery', 'bank_alert', 'account_block', 'govt_scheme', 'safe']

class PhishingDetector:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.label_encoder = LabelEncoder()
        self.is_trained = False

    def _extract_urls(self, text: str) -> List[str]:
        url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        return url_pattern.findall(text)

    def extract_url_features(self, urls: List[str]) -> np.ndarray:
        if not urls:
            return np.zeros((1, 7))
        url = urls[0]
        has_url = 1
        url_length = len(url)
        suspicious_tld = int(any(url.endswith(tld) or (tld + '/') in url for tld in SUSPICIOUS_TLDS))
        domain = url.split('//')[-1].split('/')[0]
        uses_ip_address = int(bool(re.match(r'^(\d{1,3}\.){3}\d{1,3}$', domain)))
        has_hyphen = int('-' in domain)
        has_numbers_in_domain = int(any(char.isdigit() for char in domain))
        url_shortener = int(any(shortener in domain for shortener in URL_SHORTENERS))
        return np.array([[has_url, url_length, suspicious_tld, uses_ip_address, 
                         has_hyphen, has_numbers_in_domain, url_shortener]])

    def extract_text_features(self, text: str, lang: str, fit: bool = False) -> np.ndarray:
        if fit:
            tfidf = self.vectorizer.fit_transform([text]).toarray()
        else:
            if not hasattr(self.vectorizer, 'vocabulary_'):
                tfidf = np.zeros((1, 1000))
            else:
                tfidf = self.vectorizer.transform([text]).toarray()
        text_lower = text.lower()
        pii_words = PII_KEYWORDS.get(lang, PII_KEYWORDS['en'])
        has_pii = int(any(word in text_lower for word in pii_words))
        return np.hstack((tfidf, np.array([[has_pii]])))

    def classify_phishing_type(self, features: np.ndarray) -> str:
        if not self.is_trained:
            return 'safe'
        pred_idx = self.classifier.predict(features)[0]
        return self.label_encoder.inverse_transform([pred_idx])[0]

    def train(self, dataset_path: str):
        logger.info(f"Loading dataset from {dataset_path}...")
        texts = ["Update KYC via http://fake.com", "You won a prize http://bit.ly/123", "Safe text"]
        langs = ['en', 'en', 'en']
        labels = ['kyc_fraud', 'prize_lottery', 'safe']
        self.vectorizer.fit(texts)
        features_list = []
        for text, lang in zip(texts, langs):
            urls = self._extract_urls(text)
            url_features = self.extract_url_features(urls)
            text_features = self.extract_text_features(text, lang, fit=False)
            features = np.hstack((url_features, text_features))
            features_list.append(features[0])
        X = np.array(features_list)
        y = self.label_encoder.fit_transform(labels)
        logger.info("Training classifier...")
        self.classifier.fit(X, y)
        self.is_trained = True
        logger.info("Training completed.")

    def predict(self, text: str, lang: str) -> Dict[str, Any]:
        urls = self._extract_urls(text)
        url_features = self.extract_url_features(urls)
        text_features = self.extract_text_features(text, lang)
        features = np.hstack((url_features, text_features))
        category = self.classify_phishing_type(features)
        is_phishing = category != 'safe'
        if self.is_trained:
            probs = self.classifier.predict_proba(features)[0]
            confidence = float(np.max(probs))
        else:
            confidence = 0.0
        url_flags = []
        if url_features[0][2]: url_flags.append("Suspicious TLD")
        if url_features[0][3]: url_flags.append("IP Address Domain")
        if url_features[0][6]: url_flags.append("URL Shortener")
        text_flags = []
        if text_features[0][-1]: text_flags.append("Requests PII/Sensitive Info")
        return {
            'is_phishing': is_phishing,
            'confidence': confidence,
            'category': category,
            'url_flags': url_flags,
            'text_flags': text_flags
        }

    def save(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({
            'vectorizer': self.vectorizer,
            'classifier': self.classifier,
            'label_encoder': self.label_encoder,
            'is_trained': self.is_trained
        }, path)
        logger.info(f"Model saved to {path}")

    def load(self, path: str):
        if os.path.exists(path):
            data = joblib.load(path)
            self.vectorizer = data['vectorizer']
            self.classifier = data['classifier']
            self.label_encoder = data['label_encoder']
            self.is_trained = data['is_trained']
            logger.info(f"Model loaded from {path}")
        else:
            logger.warning(f"Model file not found at {path}")

if __name__ == '__main__':
    detector = PhishingDetector()
    detector.train('dummy_path.csv')
    test_text = "Urgent: Your bank account is suspended. Update KYC at http://bit.ly/fake"
    result = detector.predict(test_text, 'en')
    logger.info(f"Prediction result: {result}")
    save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'saved', 'phishing_detector.pkl')
    detector.save(save_path)
