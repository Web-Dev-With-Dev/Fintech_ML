import os
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_score, recall_score, classification_report

class BehavioralAnomalyDetector:
    FEATURE_COLUMNS = [
        # Core behavioral features
        'tx_count_1h', 'avg_amount_30d', 'current_amount', 'new_recipient',
        'time_of_day', 'day_of_week', 'account_age_days',
        # Derived in engineer_features()
        'amount_vs_avg_ratio', 'velocity_spike', 'balance_drain_ratio',
        # PaySim real fraud signals (populated by load_and_adapt_paysim)
        'balance_drain_pct', 'complete_wipeout', 'dest_was_empty', 'type_risk',
    ]
    
    def __init__(self, contamination: float = 'auto'):
        self.contamination = contamination
        self.model = IsolationForest(
            contamination=contamination if contamination != 'auto' else 0.05,
            n_estimators=200,
            max_samples='auto',
            random_state=42,
            n_jobs=-1
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self._score_threshold = None   # set after training for predict_anomaly

    def engineer_features(self, session_df: pd.DataFrame) -> pd.DataFrame:
        df = session_df.copy()

        df['avg_amount_30d']    = df['avg_amount_30d'].replace(0, 1e-5)
        df['avg_hourly_tx_30d'] = df.get('avg_hourly_tx_30d', pd.Series(0.3, index=df.index)).replace(0, 1e-5)
        df['estimated_balance'] = df.get('estimated_balance', df['current_amount'] + 100).replace(0, 1e-5)

        df['amount_vs_avg_ratio'] = df['current_amount'] / df['avg_amount_30d']
        df['velocity_spike']      = df['tx_count_1h']    / df['avg_hourly_tx_30d']
        df['balance_drain_ratio'] = df['current_amount'] / df['estimated_balance']

        # PaySim fraud-signal features — fill with safe defaults if not present
        if 'balance_drain_pct' not in df.columns:
            df['balance_drain_pct'] = df['balance_drain_ratio'].clip(0, 1)
        if 'complete_wipeout' not in df.columns:
            df['complete_wipeout']  = (df['balance_drain_ratio'] >= 0.99).astype(float)
        if 'dest_was_empty' not in df.columns:
            df['dest_was_empty']    = df.get('new_recipient', pd.Series(0, index=df.index)).astype(float)
        if 'type_risk' not in df.columns:
            df['type_risk']         = 0.3   # neutral default

        return df

    def prepare_features(self, df: pd.DataFrame) -> np.ndarray:
        missing_cols = [col for col in self.FEATURE_COLUMNS if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        return df[self.FEATURE_COLUMNS].values

    def train(self, dataset_path: str) -> None:
        print(f"Loading dataset from {dataset_path}...")
        df = pd.read_csv(dataset_path)

        # ── Auto-detect contamination from real fraud rate ──────────────────
        if 'label' in df.columns:
            real_fraud_rate     = float(df['label'].mean())
            auto_contamination  = float(np.clip(real_fraud_rate, 0.001, 0.1))
            print(f"Fraud rate: {real_fraud_rate:.4%} → contamination = {auto_contamination:.4f}")
            self.contamination  = auto_contamination
            self.model.set_params(contamination=auto_contamination)

        print("Engineering features...")
        df = self.engineer_features(df)

        # ── KEY FIX: Train Isolation Forest on NORMAL samples only ──────────
        # Unsupervised anomaly detection learns what is "normal".
        # Fraud samples will then score low (anomalous) at inference time.
        if 'label' in df.columns:
            df_normal   = df[df['label'] == 0]
            df_fraud    = df[df['label'] == 1]
            print(f"Training on {len(df_normal)} normal samples only (excluding {len(df_fraud)} fraud).")
        else:
            df_normal   = df
            df_fraud    = pd.DataFrame()

        X_normal    = self.prepare_features(df_normal)
        print("Scaling features...")
        X_scaled    = self.scaler.fit_transform(X_normal)

        print("Training Isolation Forest on normal data...")
        self.model.fit(X_scaled)

        # ── Set threshold using fraud samples if available, else use percentile ──
        if len(df_fraud) > 0:
            X_fraud     = self.prepare_features(df_fraud)
            X_fraud_sc  = self.scaler.transform(X_fraud)
            X_all_sc    = self.scaler.transform(self.prepare_features(df))

            normal_scores = self.model.score_samples(X_scaled)
            fraud_scores  = self.model.score_samples(X_fraud_sc)

            # Threshold = midpoint between mean normal score and mean fraud score
            self._score_threshold = float(
                (np.mean(normal_scores) + np.mean(fraud_scores)) / 2.0
            )
            print(f"Normal mean score : {np.mean(normal_scores):.4f}")
            print(f"Fraud  mean score : {np.mean(fraud_scores):.4f}")
            print(f"Threshold (midpt) : {self._score_threshold:.4f}")
        else:
            scores = self.model.score_samples(X_scaled)
            pct    = (1.0 - self.contamination) * 100
            self._score_threshold = float(np.percentile(scores, 100 - pct))
            print(f"Threshold (pct)   : {self._score_threshold:.4f}")

        self.is_trained = True
        print("Training completed.")

    def compute_panic_score(self, session_data: dict) -> float:
        score = 0.0
        max_score = 5.0
        
        current_amount = session_data.get('current_amount', 0)
        new_recipient = session_data.get('new_recipient', 0)
        hour = session_data.get('time_of_day', 12)
        velocity_spike = session_data.get('velocity_spike', 0)
        balance_drain_ratio = session_data.get('balance_drain_ratio', 0)
        
        if current_amount in [100, 500, 1000, 5000, 10000]:
            score += 1.0
            
        if new_recipient == 1:
            score += 1.0
            
        if hour >= 23 or hour <= 5:
            score += 1.0
            
        if velocity_spike > 3.0:
            score += 1.0
            
        if balance_drain_ratio > 0.8:
            score += 1.0
            
        return min(score / max_score, 1.0)

    def predict_anomaly(self, session_data: dict) -> Dict[str, Any]:
        if not self.is_trained:
            raise ValueError("Model is not trained. Call train() or load() first.")

        df = pd.DataFrame([session_data])
        df = self.engineer_features(df)
        X  = self.prepare_features(df)

        session_data_enriched = df.iloc[0].to_dict()
        X_scaled = self.scaler.transform(X)

        raw_score = float(self.model.score_samples(X_scaled)[0])

        # ── Use calibrated threshold for consistent is_anomaly detection ──────
        if self._score_threshold is not None:
            is_anomaly = bool(raw_score < self._score_threshold)
        else:
            # Fallback to model.predict if threshold not calibrated
            is_anomaly = bool(self.model.predict(X_scaled)[0] == -1)

        # Normalize: lower raw_score → higher anomaly_score (0–1)
        normalized_anomaly_score = float(np.clip(-raw_score / 0.5, 0, 1))

        panic_score = self.compute_panic_score(session_data_enriched)

        intervention_required = is_anomaly and (
            panic_score > 0.6 or
            session_data_enriched.get('balance_drain_ratio', 0) > 0.9
        )

        anomaly_type = "None"
        if is_anomaly:
            if panic_score > 0.7:
                anomaly_type = "High Panic / Coercion"
            elif session_data_enriched.get('velocity_spike', 0) > 5:
                anomaly_type = "Account Takeover / Rapid Transfer"
            else:
                anomaly_type = "Unusual Behavior Pattern"

        return {
            'is_anomaly':             is_anomaly,
            'anomaly_score':          round(normalized_anomaly_score, 4),
            'raw_score':              round(raw_score, 4),
            'panic_score':            round(panic_score, 4),
            'intervention_required':  intervention_required,
            'anomaly_type':           anomaly_type
        }

    def save(self, filepath: str) -> None:
        if not self.is_trained:
            raise ValueError("Model is not trained yet.")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({
            'model':            self.model,
            'scaler':           self.scaler,
            'score_threshold':  self._score_threshold,
            'contamination':    self.contamination
        }, filepath)
        print(f"Model saved to {filepath}")

    def load(self, filepath: str) -> None:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"No model found at {filepath}")
        artifacts           = joblib.load(filepath)
        self.model          = artifacts['model']
        self.scaler         = artifacts['scaler']
        self._score_threshold = artifacts.get('score_threshold', None)
        self.contamination  = artifacts.get('contamination', 0.05)
        self.is_trained     = True
        print(f"Model loaded from {filepath}")



# ─── Dataset paths ────────────────────────────────────────────────────────────
_BASE        = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
DATASET_DIR  = os.path.join(_BASE, 'datasets')

# PaySim: PS_20174392719_1491204439457_log.csv
PAYSIM_CSV   = os.path.join(DATASET_DIR, 'PS_20174392719_1491204439457_log.csv')

# IEEE-CIS Fraud Detection
IEEE_DIR     = os.path.join(DATASET_DIR, 'IEEE fraud deetction')
IEEE_TRAIN   = os.path.join(IEEE_DIR, 'train_transaction.csv')


def load_and_adapt_paysim(path: str, nrows: int = 100_000) -> pd.DataFrame:
    """
    Load PaySim and map columns to BehavioralAnomalyDetector feature schema.
    Uses REAL PaySim fraud signals:
      - balance_drain_pct : fraction of orig balance drained (high in fraud)
      - dest_was_empty    : receiver had 0 balance before (mule account signal)
      - complete_wipeout  : sender's balance went to exactly 0 (full drain)
      - amount_to_balance : transaction amount vs sender's starting balance
      - type_risk         : TRANSFER=0.8, CASH_OUT=0.9, others low
    """
    raw = pd.read_csv(path, nrows=nrows)
    print(f"PaySim loaded: {len(raw)} rows | Fraud rate: {raw['isFraud'].mean():.2%}")

    eps = 1e-5
    type_risk_map = {'TRANSFER': 0.8, 'CASH_OUT': 0.9, 'PAYMENT': 0.1, 'DEBIT': 0.2, 'CASH_IN': 0.05}

    df = pd.DataFrame()
    # Original behavioral features
    df['tx_count_1h']        = raw['step'] % 10 + 1            # proxy: more steps → more tx
    df['avg_amount_30d']     = raw['amount'].rolling(30, min_periods=1).mean().fillna(raw['amount'])
    df['current_amount']     = raw['amount']
    df['new_recipient']      = (raw['oldbalanceDest'] == 0).astype(int)   # real signal!
    df['time_of_day']        = raw['step'] % 24
    df['day_of_week']        = (raw['step'] // 24) % 7
    df['account_age_days']   = (raw['step'] // 24).clip(lower=1)
    df['avg_hourly_tx_30d']  = 0.3

    # ── REAL fraud signals from PaySim ───────────────────────────────────────
    old_bal  = raw['oldbalanceOrg'].replace(0, eps)
    df['estimated_balance']  = old_bal

    # amount_vs_avg_ratio & velocity_spike are computed in engineer_features()
    # but we add raw fraud signals as extra features below:
    df['balance_drain_pct']  = (raw['amount'] / old_bal).clip(0, 1)       # 1.0 = full drain
    df['complete_wipeout']   = (raw['newbalanceOrig'] == 0).astype(float) # account fully emptied
    df['dest_was_empty']     = (raw['oldbalanceDest'] == 0).astype(float) # mule account signal
    df['type_risk']          = raw['type'].map(type_risk_map).fillna(0.3)
    df['label']              = raw['isFraud']
    return df


def load_and_adapt_ieee(path: str, nrows: int = 100_000) -> pd.DataFrame:
    """
    Load IEEE-CIS fraud dataset and map to BehavioralAnomalyDetector feature schema.
    Key columns: TransactionAmt, isFraud, TransactionDT, card1..card6, etc.
    """
    usecols = ['TransactionDT', 'TransactionAmt', 'isFraud']
    raw = pd.read_csv(path, nrows=nrows, usecols=usecols)
    print(f"IEEE-CIS loaded: {len(raw)} rows | Fraud rate: {raw['isFraud'].mean():.2%}")

    df = pd.DataFrame()
    df['tx_count_1h']        = np.random.randint(1, 5, len(raw))
    df['avg_amount_30d']     = raw['TransactionAmt'].rolling(30, min_periods=1).mean().fillna(raw['TransactionAmt'])
    df['current_amount']     = raw['TransactionAmt']
    df['new_recipient']      = np.random.choice([0, 1], p=[0.85, 0.15], size=len(raw))
    df['time_of_day']        = (raw['TransactionDT'] // 3600) % 24
    df['day_of_week']        = (raw['TransactionDT'] // 86400) % 7
    df['account_age_days']   = (raw['TransactionDT'] // 86400).clip(lower=1)
    df['avg_hourly_tx_30d']  = 0.3
    df['estimated_balance']  = raw['TransactionAmt'] * np.random.uniform(1.5, 10, len(raw))
    df['label']              = raw['isFraud']
    return df


if __name__ == '__main__':
    np.random.seed(42)

    # ── Try loading real datasets (PaySim preferred, IEEE-CIS fallback) ───────
    df_combined = None

    if os.path.exists(PAYSIM_CSV):
        print(f"Loading PaySim dataset from: {PAYSIM_CSV}")
        df_combined = load_and_adapt_paysim(PAYSIM_CSV, nrows=100_000)

    elif os.path.exists(IEEE_TRAIN):
        print(f"Loading IEEE-CIS dataset from: {IEEE_TRAIN}")
        df_combined = load_and_adapt_ieee(IEEE_TRAIN, nrows=100_000)

    else:
        print("No real datasets found. Generating synthetic mock data...")
        n_samples = 1000
        normal_data = {
            'tx_count_1h': np.random.randint(1, 3, n_samples),
            'avg_amount_30d': np.random.uniform(100, 5000, n_samples),
            'current_amount': np.random.uniform(50, 2000, n_samples),
            'new_recipient': np.random.choice([0, 1], p=[0.9, 0.1], size=n_samples),
            'time_of_day': np.random.randint(8, 22, n_samples),
            'day_of_week': np.random.randint(0, 7, n_samples),
            'account_age_days': np.random.randint(180, 3650, n_samples),
            'avg_hourly_tx_30d': np.random.uniform(0.1, 0.5, n_samples),
            'estimated_balance': np.random.uniform(5000, 50000, n_samples),
            'label': 0
        }
        anomaly_data = {
            'tx_count_1h': np.random.randint(5, 15, 50),
            'avg_amount_30d': np.random.uniform(100, 500, 50),
            'current_amount': np.random.uniform(5000, 20000, 50),
            'new_recipient': np.ones(50, dtype=int),
            'time_of_day': np.random.randint(0, 5, 50),
            'day_of_week': np.random.randint(0, 7, 50),
            'account_age_days': np.random.randint(10, 180, 50),
            'avg_hourly_tx_30d': np.random.uniform(0.1, 0.5, 50),
            'estimated_balance': np.random.uniform(5000, 25000, 50),
            'label': 1
        }
        df_combined = pd.concat(
            [pd.DataFrame(normal_data), pd.DataFrame(anomaly_data)]
        ).sample(frac=1).reset_index(drop=True)

    # ── Save temp CSV and train ───────────────────────────────────────────────
    dataset_path = os.path.join(DATASET_DIR, '_behavioral_adapted.csv')
    df_combined.to_csv(dataset_path, index=False)

    detector = BehavioralAnomalyDetector(contamination='auto')
    detector.train(dataset_path)

    # ── Evaluate using calibrated score threshold ─────────────────────────────
    df_features = detector.engineer_features(df_combined)
    X           = detector.prepare_features(df_features)
    X_scaled    = detector.scaler.transform(X)

    raw_scores  = detector.model.score_samples(X_scaled)
    threshold   = detector._score_threshold
    pred_labels = [1 if s < threshold else 0 for s in raw_scores]
    true_labels = df_combined['label'].tolist()

    print("\n--- Evaluation Results ---")
    print(f"Threshold used: {threshold:.4f}")
    print("Precision:", precision_score(true_labels, pred_labels, zero_division=0))
    print("Recall:",    recall_score(true_labels, pred_labels, zero_division=0))
    print("\nClassification Report:\n", classification_report(true_labels, pred_labels, zero_division=0))

    # ── Save model ─────────────────────────────────────────────────────────────
    save_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), '..', 'saved', 'behavioral_anomaly_detector.pkl'
    )
    detector.save(save_path)

    os.remove(dataset_path)

    print("\nTest prediction (fraud sample):")
    sample = df_combined[df_combined['label'] == 1].iloc[0].drop('label').to_dict()
    res = detector.predict_anomaly(sample)
    print(res)

