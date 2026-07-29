import os
import re
import joblib
import numpy as np
import pandas as pd
from typing import Dict, List, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.metrics import classification_report
import xgboost as xgb
from loguru import logger


class ScamSMSClassifier:
    def __init__(self):
        self.lexicon = self.build_keyword_lexicon()
        self.vectorizer = TfidfVectorizer(
            analyzer='char_wb',
            ngram_range=(2, 5),
            max_features=8000,
            sublinear_tf=True
        )
        self.model = xgb.XGBClassifier(eval_metric='logloss', random_state=42)
        self.is_trained = False

    def build_keyword_lexicon(self) -> Dict[str, List[str]]:
        return {
            'en':  ['otp', 'prize', 'lottery', 'winner', 'urgent', 'arrest', 'blocked', 'kyc', 'suspend', 'claim'],
            'hi':  ['kya', 'band', 'jeet', 'inaam', 'hiraasat', 'jald', 'block', 'otp', 'paise', 'turant'],
            'bn':  ['purashkar', 'jitechen', 'bandha', 'shigri', 'aabar', 'otp', 'taka', 'bank', 'account'],
            'te':  ['bahumati', 'vijetha', 'ventane', 'aapi', 'otp', 'dabbulu', 'bank', 'account'],
            'ta':  ['parisu', 'vetri', 'udane', 'tada', 'otp', 'panam', 'bank', 'account'],
            'mr':  ['baksis', 'jinkla', 'taatdi', 'banda', 'otp', 'paise', 'bank', 'account'],
            'gu':  ['inam', 'jityo', 'tarat', 'bandh', 'otp', 'paisa', 'bank', 'account'],
            'kn':  ['bahumana', 'vijeta', 'takshana', 'bandh', 'otp', 'hana', 'bank', 'account'],
        }

    def _get_critical_keywords(self) -> List[str]:
        critical = []
        for words in self.lexicon.values():
            critical.extend(words)
        return list(set(critical))

    def extract_rule_features(self, text: str, lang: str) -> np.ndarray:
        t = text.lower()
        has_otp     = int('otp' in t)
        has_urgency = int(any(w in t for w in ['urgent', 'immediately', 'turant', 'jald']))
        has_threat  = int(any(w in t for w in ['arrest', 'blocked', 'suspend', 'band']))
        has_prize   = int(any(w in t for w in ['prize', 'lottery', 'winner', 'inaam']))
        has_link    = int(bool(re.search(r'(http|https)://\S+', t)))
        has_phone   = int(bool(re.search(r'\+?\d{10,12}', t)))
        has_amount  = int(bool(re.search(r'(rs\.?|₹|\$)\s*\d+', t)))
        urgency_lvl = has_urgency + has_threat
        return np.array([has_otp, has_urgency, has_threat, has_prize,
                         has_link, has_phone, has_amount, urgency_lvl], dtype=float)

    def _build_features(self, texts: List[str], langs: List[str], fit: bool) -> np.ndarray:
        if fit:
            tfidf = self.vectorizer.fit_transform(texts).toarray()
        else:
            tfidf = self.vectorizer.transform(texts).toarray()

        rules = np.vstack([self.extract_rule_features(t, l) for t, l in zip(texts, langs)])
        return np.hstack([tfidf, rules])

    def train(self, X_texts: List[str], y_labels: List[int], X_langs: List[str]):
        logger.info("Fitting unified vectorizer on all texts...")
        X = self._build_features(X_texts, X_langs, fit=True)
        y = np.array(y_labels)

        param_grid = {
            'max_depth':     [3, 5],
            'n_estimators':  [50, 100],
            'learning_rate': [0.1, 0.2]
        }
        grid = GridSearchCV(self.model, param_grid, cv=3, scoring='f1', n_jobs=-1)
        logger.info("Running GridSearchCV...")
        grid.fit(X, y)
        self.model = grid.best_estimator_
        self.is_trained = True
        logger.info(f"Training done. Best params: {grid.best_params_}")

    def predict(self, text: str, lang: str = "en") -> Dict[str, Any]:
        t = text.lower()
        found = [w for w in self._get_critical_keywords() if w in t]
        if found:
            return {
                'label': 'SCAM',
                'confidence': 0.99,
                'risk_score': 0.99,
                'red_flags': found,
                'rule_triggered': True
            }

        if not self.is_trained:
            return {
                'label': 'SAFE',
                'confidence': 0.8,
                'risk_score': 0.1,
                'red_flags': [],
                'rule_triggered': False
            }

        X = self._build_features([text], [lang], fit=False)
        prob = self.model.predict_proba(X)[0]
        is_scam = prob[1] > 0.5
        return {
            'label':        'SCAM' if is_scam else 'SAFE',
            'confidence':   float(prob[1] if is_scam else prob[0]),
            'risk_score':   float(prob[1]),
            'red_flags':    [],
            'rule_triggered': False
        }


    def save(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({
            'model':      self.model,
            'vectorizer': self.vectorizer,
            'is_trained': self.is_trained
        }, path)
        logger.info(f"Model saved to {path}")

    def load(self, path: str):
        if not os.path.exists(path):
            logger.warning(f"No saved model at {path}")
            return
        data = joblib.load(path)
        self.model      = data['model']
        self.vectorizer = data['vectorizer']
        self.is_trained = data['is_trained']
        logger.info(f"Model loaded from {path}")



# ─── Dataset paths (relative to project root /datasets/) ─────────────────────
DATASET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'datasets')

SMS_SPAM_COLLECTION = os.path.join(DATASET_DIR, 'SMSSpamCollection')   # UCI tab-separated
SPAM_CSV            = os.path.join(DATASET_DIR, 'spam.csv')             # Kaggle CSV


def load_sms_datasets() -> pd.DataFrame:
    """Load and merge UCI SMSSpamCollection + Kaggle spam.csv into a unified DataFrame."""
    frames = []

    # 1. UCI SMSSpamCollection (tab-separated: label\tmessage)
    if os.path.exists(SMS_SPAM_COLLECTION):
        uci = pd.read_csv(
            SMS_SPAM_COLLECTION, sep='\t', header=None,
            names=['label_raw', 'text'], encoding='latin-1'
        )
        uci['label'] = uci['label_raw'].map({'spam': 1, 'ham': 0})
        uci['lang']  = 'en'
        frames.append(uci[['text', 'label', 'lang']])
        logger.info(f"Loaded UCI SMSSpamCollection: {len(uci)} rows")
    else:
        logger.warning(f"UCI dataset not found at {SMS_SPAM_COLLECTION}")

    # 2. Kaggle spam.csv (columns: v1=label, v2=text)
    if os.path.exists(SPAM_CSV):
        kaggle = pd.read_csv(SPAM_CSV, encoding='latin-1')[['v1', 'v2']]
        kaggle.columns = ['label_raw', 'text']
        kaggle['label'] = kaggle['label_raw'].map({'spam': 1, 'ham': 0})
        kaggle['lang']  = 'en'
        frames.append(kaggle[['text', 'label', 'lang']])
        logger.info(f"Loaded Kaggle spam.csv: {len(kaggle)} rows")
    else:
        logger.warning(f"Kaggle spam.csv not found at {SPAM_CSV}")

    if not frames:
        raise FileNotFoundError(
            "No SMS datasets found in /datasets/. "
            "Expected: SMSSpamCollection and/or spam.csv"
        )

    df = pd.concat(frames, ignore_index=True).dropna(subset=['label', 'text'])
    df['label'] = df['label'].astype(int)
    logger.info(f"Combined dataset: {len(df)} rows | Scam rate: {df['label'].mean():.2%}")
    return df


if __name__ == '__main__':
    logger.info("Initializing ScamSMSClassifier pipeline...")
    classifier = ScamSMSClassifier()

    # ── Load real datasets from /datasets/ ──────────────────────────────────
    df = load_sms_datasets()

    X_train, X_test, y_train, y_test, lang_train, lang_test = train_test_split(
        df['text'].tolist(), df['label'].tolist(), df['lang'].tolist(),
        test_size=0.25, random_state=42
    )

    classifier.train(X_train, y_train, lang_train)

    preds = [1 if classifier.predict(t, l)['label'] == 'SCAM' else 0
             for t, l in zip(X_test, lang_test)]

    logger.info("Evaluation:\n" + classification_report(y_test, preds, zero_division=0))

    save_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), '..', 'saved', 'scam_sms_classifier.pkl'
    )
    classifier.save(save_path)

