import os
import re
import joblib
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.metrics import classification_report
import xgboost as xgb
from loguru import logger

class ScamSMSClassifier:
    def __init__(self):
        self.lexicon = self.build_keyword_lexicon()
        self.en_vectorizer = TfidfVectorizer(ngram_range=(1, 3), max_features=5000)
        self.indic_vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 5), max_features=5000)
        self.model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
        self.is_trained = False

    def build_keyword_lexicon(self) -> Dict[str, List[str]]:
        return {
            'en': ['otp', 'prize', 'lottery', 'winner', 'urgent', 'arrest', 'blocked', 'kyc', 'suspend', 'claim'],
            'hi': ['kya', 'band', 'jeet', 'inaam', 'hiraasat', 'jald', 'block', 'otp', 'paise', 'turant'],
            'bn': ['purashkar', 'jitechen', 'bandha', 'shigri', 'aabar', 'otp', 'taka', 'bank', 'account'],
            'te': ['bahumati', 'vijetha', 'ventane', 'aapi', 'otp', 'dabbulu', 'bank', 'account'],
            'ta': ['parisu', 'vetri', 'udane', 'tada', 'otp', 'panam', 'bank', 'account'],
            'mr': ['baksis', 'jinkla', 'taatdi', 'banda', 'otp', 'paise', 'bank', 'account'],
            'gu': ['inam', 'jityo', 'tarat', 'bandh', 'otp', 'paisa', 'bank', 'account'],
            'kn': ['bahumana', 'vijeta', 'takshana', 'bandh', 'otp', 'hana', 'bank', 'account'],
        }

    def _get_critical_keywords(self) -> List[str]:
        critical = []
        for lang, words in self.lexicon.items():
            critical.extend(words)
        return list(set(critical))

    def extract_tfidf_features(self, texts: List[str], fit: bool, lang: str = 'en') -> np.ndarray:
        if lang == 'en':
            if fit:
                return self.en_vectorizer.fit_transform(texts).toarray()
            return self.en_vectorizer.transform(texts).toarray()
        else:
            if fit:
                return self.indic_vectorizer.fit_transform(texts).toarray()
            return self.indic_vectorizer.transform(texts).toarray()

    def extract_rule_features(self, text: str, lang: str) -> np.ndarray:
        text_lower = text.lower()
        has_otp = 'otp' in text_lower
        has_urgency = any(word in text_lower for word in ['urgent', 'immediately', 'turant', 'jald'])
        has_threat = any(word in text_lower for word in ['arrest', 'blocked', 'suspend', 'band'])
        has_prize = any(word in text_lower for word in ['prize', 'lottery', 'winner', 'inaam'])
        has_link = bool(re.search(r'(http|https)://[^\s]+', text_lower))
        has_phone = bool(re.search(r'\+?\d{10,12}', text_lower))
        has_amount = bool(re.search(r'(rs\.?|₹|\$)\s*\d+', text_lower))
        urgency_level = int(has_urgency) + int(has_threat)
        return np.array([[has_otp, has_urgency, has_threat, has_prize, has_link, has_phone, has_amount, urgency_level]])

    def train(self, X_texts: List[str], y_labels: List[int], X_langs: List[str]):
        logger.info("Starting training process...")
        en_texts = [text for text, lang in zip(X_texts, X_langs) if lang == 'en']
        indic_texts = [text for text, lang in zip(X_texts, X_langs) if lang != 'en']
        if en_texts:
            logger.info("Fitting English vectorizer...")
            self.extract_tfidf_features(en_texts, fit=True, lang='en')
        if indic_texts:
            logger.info("Fitting Indic vectorizer...")
            self.extract_tfidf_features(indic_texts, fit=True, lang='hi')
        features = []
        for text, lang in zip(X_texts, X_langs):
            tfidf = self.extract_tfidf_features([text], fit=False, lang='en' if lang == 'en' else 'hi')
            rules = self.extract_rule_features(text, lang)
            combined = np.hstack((tfidf, rules))
            features.append(combined[0])
        X_train = np.array(features)
        y_train = np.array(y_labels)
        param_grid = {
            'max_depth': [3, 5],
            'n_estimators': [50, 100],
            'learning_rate': [0.1, 0.2]
        }
        grid_search = GridSearchCV(estimator=self.model, param_grid=param_grid, cv=3, scoring='f1', n_jobs=-1)
        logger.info("Running GridSearchCV...")
        grid_search.fit(X_train, y_train)
        self.model = grid_search.best_estimator_
        self.is_trained = True
        logger.info(f"Training completed. Best params: {grid_search.best_params_}")

    def predict(self, text: str, lang: str) -> Dict[str, Any]:
        text_lower = text.lower()
        critical_keywords = self._get_critical_keywords()
        found_critical = [word for word in critical_keywords if word in text_lower]
        if found_critical:
            return {
                'label': 'SCAM',
                'confidence': 0.99,
                'red_flags': found_critical,
                'rule_triggered': True
            }
        if not self.is_trained:
            raise ValueError("Model is not trained. Cannot perform Stage 2 prediction.")
        tfidf = self.extract_tfidf_features([text], fit=False, lang='en' if lang == 'en' else 'hi')
        rules = self.extract_rule_features(text, lang)
        features = np.hstack((tfidf, rules))
        prob = self.model.predict_proba(features)[0]
        is_scam = prob[1] > 0.5
        return {
            'label': 'SCAM' if is_scam else 'HAM',
            'confidence': float(prob[1] if is_scam else prob[0]),
            'red_flags': [],
            'rule_triggered': False
        }

    def save(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({
            'model': self.model,
            'en_vectorizer': self.en_vectorizer,
            'indic_vectorizer': self.indic_vectorizer,
            'is_trained': self.is_trained
        }, path)
        logger.info(f"Model saved to {path}")

    def load(self, path: str):
        if os.path.exists(path):
            data = joblib.load(path)
            self.model = data['model']
            self.en_vectorizer = data['en_vectorizer']
            self.indic_vectorizer = data['indic_vectorizer']
            self.is_trained = data['is_trained']
            logger.info(f"Model loaded from {path}")
        else:
            logger.warning(f"Model file not found at {path}")

if __name__ == '__main__':
    logger.info("Initializing ScamSMSClassifier pipeline...")
    classifier = ScamSMSClassifier()
    data = {
        'text': [
            "Your bank account is blocked. Update KYC immediately via http://fake.com",
            "Hey, let's meet for lunch tomorrow.",
            "You won a prize! Call now.",
            "Meeting at 5 PM",
            "Aapka account band ho gaya hai, OTP share karein",
            "Aaj khana khane chalein?"
        ],
        'lang': ['en', 'en', 'en', 'en', 'hi', 'hi'],
        'label': [1, 0, 1, 0, 1, 0]
    }
    df = pd.DataFrame(data)
    X_train, X_test, y_train, y_test, lang_train, lang_test = train_test_split(
        df['text'].tolist(), df['label'].tolist(), df['lang'].tolist(), test_size=0.2, random_state=42
    )
    classifier.train(X_train, y_train, lang_train)
    predictions = []
    for text, lang in zip(X_test, lang_test):
        pred = classifier.predict(text, lang)
        predictions.append(1 if pred['label'] == 'SCAM' else 0)
    logger.info("Evaluation Results:")
    logger.info(classification_report(y_test, predictions))
    save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'saved', 'scam_sms_classifier.pkl')
    classifier.save(save_path)
