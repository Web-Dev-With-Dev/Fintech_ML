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
        """
        Train on a phishing URL/text dataset.
        Supports:
          - datasets/csv.txt  : URLhaus Database Dump
            Format: id, date_added, url, url_status, last_online, threat, tags, urlhaus_link, reporter
            (No header row; comment lines start with '#')
          - Any CSV with 'url' and 'label' columns (0=safe, 1=phishing)
        """
        logger.info(f"Loading phishing dataset from {dataset_path}...")

        # ── Load real URL dataset ─────────────────────────────────────────────
        if os.path.exists(dataset_path):
            try:
                raw = pd.read_csv(dataset_path, encoding='latin-1', on_bad_lines='skip')
                raw.columns = raw.columns.str.strip()

                # ── Format 1: phishing_site_urls.csv (URL + Label: bad/good) ─
                if 'URL' in raw.columns and 'Label' in raw.columns:
                    raw = raw.dropna(subset=['URL', 'Label'])

                    # Sample balanced subset for speed (max 5000 each class)
                    bad  = raw[raw['Label'] == 'bad'].sample(
                        min(5000, (raw['Label'] == 'bad').sum()), random_state=42)
                    good = raw[raw['Label'] == 'good'].sample(
                        min(5000, (raw['Label'] == 'good').sum()), random_state=42)
                    sampled = pd.concat([bad, good], ignore_index=True)

                    phish_urls  = bad['URL'].astype(str).tolist()
                    safe_urls   = good['URL'].astype(str).tolist()

                    texts      = phish_urls + safe_urls
                    langs      = ['en'] * len(texts)
                    labels_raw = ['kyc_fraud'] * len(phish_urls) + ['safe'] * len(safe_urls)
                    logger.info(
                        f"phishing_site_urls.csv loaded: "
                        f"{len(phish_urls)} phishing + {len(safe_urls)} safe URLs "
                        f"(sampled from {len(raw)} total)"
                    )

                # ── Format 2: URLhaus csv.txt (no header, # comments) ────────
                elif dataset_path.endswith('.txt') or 'urlhaus' in dataset_path.lower():
                    raw2 = pd.read_csv(
                        dataset_path,
                        comment='#', header=None,
                        names=['id','date_added','url','url_status','last_online',
                               'threat','tags','urlhaus_link','reporter'],
                        encoding='latin-1', on_bad_lines='skip'
                    )
                    raw2 = raw2.dropna(subset=['url'])
                    phish_urls = raw2['url'].astype(str).tolist()[:3000]
                    threat_map = {
                        'malware_download': 'kyc_fraud',
                        'phishing':         'kyc_fraud',
                        'botnet_cc':        'account_block',
                        'exploit':          'prize_lottery',
                    }
                    raw2['category'] = raw2['threat'].map(threat_map).fillna('kyc_fraud')
                    categories  = raw2['category'].tolist()[:3000]
                    safe_urls   = [
                        'https://www.google.com', 'https://www.sbi.co.in',
                        'https://www.npci.org.in', 'https://www.amazon.in',
                        'https://www.flipkart.com', 'https://www.irctc.co.in',
                        'https://www.uidai.gov.in', 'https://www.incometax.gov.in'
                    ] * (len(phish_urls) // 8)
                    texts      = phish_urls + safe_urls
                    langs      = ['en'] * len(texts)
                    labels_raw = categories + ['safe'] * len(safe_urls)
                    logger.info(f"URLhaus loaded: {len(phish_urls)} malicious + {len(safe_urls)} safe URLs")

                else:
                    raise ValueError("Unrecognised format. Expected 'URL'+'Label' or URLhaus columns.")

            except Exception as e:
                logger.warning(f"Could not parse dataset ({e}). Falling back to mock data.")
                texts      = ["Update KYC via http://fake.com", "You won a prize http://bit.ly/123", "Safe text"]
                langs      = ['en', 'en', 'en']
                labels_raw = ['kyc_fraud', 'prize_lottery', 'safe']
        else:
            logger.warning(f"Dataset not found at {dataset_path}. Using mock data.")
            texts      = ["Update KYC via http://fake.com", "You won a prize http://bit.ly/123", "Safe text"]
            langs      = ['en', 'en', 'en']
            labels_raw = ['kyc_fraud', 'prize_lottery', 'safe']


        # ── Fit vectorizer & build features ──────────────────────────────────
        self.vectorizer.fit(texts)
        features_list = []
        for text, lang in zip(texts, langs):
            urls = self._extract_urls(text)
            url_features = self.extract_url_features(urls)
            text_features = self.extract_text_features(text, lang, fit=False)
            features = np.hstack((url_features, text_features))
            features_list.append(features[0])

        X = np.array(features_list)
        y = self.label_encoder.fit_transform(labels_raw)
        logger.info("Training Random Forest classifier...")
        self.classifier.fit(X, y)
        self.is_trained = True
        logger.info("Training completed.")

    def predict(self, text: str, lang: str = "en") -> Dict[str, Any]:
        urls = self._extract_urls(text)
        url_features = self.extract_url_features(urls)
        text_features = self.extract_text_features(text, lang)
        features = np.hstack((url_features, text_features))

        url_flags = []
        if url_features[0][2]: url_flags.append("Suspicious TLD")
        if url_features[0][3]: url_flags.append("IP Address Domain")
        if url_features[0][6]: url_flags.append("URL Shortener")
        text_flags = []
        if text_features[0][-1]: text_flags.append("Requests PII/Sensitive Info")

        if self.is_trained:
            probs = self.classifier.predict_proba(features)[0]
            pred_idx = np.argmax(probs)
            category = str(self.label_encoder.inverse_transform([pred_idx])[0])

            if not urls and not text_flags:
                category = 'safe'
                is_phishing = False
                risk_score = 0.05
                confidence = 0.95
            else:
                is_phishing = category != 'safe'
                classes = list(self.label_encoder.classes_)
                safe_idx = classes.index('safe') if 'safe' in classes else -1
                risk_score = float(1.0 - probs[safe_idx]) if safe_idx != -1 else (float(probs[pred_idx]) if is_phishing else 0.1)
                confidence = float(np.max(probs))
        else:
            is_phishing = bool(url_flags or text_flags)
            category = 'phishing' if is_phishing else 'safe'
            risk_score = 0.85 if is_phishing else 0.1
            confidence = 0.8 if is_phishing else 0.9

        return {
            'is_phishing': is_phishing,
            'confidence': confidence,
            'risk_score': risk_score,
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
    import os as _os
    _DATASET_DIR  = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..', 'datasets')
    _PHISH_CSV    = _os.path.join(_DATASET_DIR, 'phishing_site_urls.csv')  # 549K rows, URL+Label

    detector = PhishingDetector()
    detector.train(_PHISH_CSV)

    test_cases = [
        ("Urgent: Your bank account is suspended. Update KYC at http://bit.ly/fake", "en"),
        ("nobell.it/paypal.com/verification/login/index.php?cmd=_profile", "en"),
        ("https://www.google.com", "en"),
        ("Aapka SBI account band ho gaya hai http://sbi-kyc.tk/verify", "hi"),
    ]

    for text, lang in test_cases:
        result = detector.predict(text, lang)
        status = "🚨 PHISHING" if result['is_phishing'] else "✅ SAFE"
        logger.info(f"{status} [{result['confidence']:.0%}] → {text[:60]}...")

    save_path = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', 'saved', 'phishing_detector.pkl')
    detector.save(save_path)


