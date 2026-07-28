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
        'tx_count_1h', 'avg_amount_30d', 'current_amount', 'new_recipient', 
        'time_of_day', 'day_of_week', 'account_age_days', 'amount_vs_avg_ratio', 
        'velocity_spike', 'balance_drain_ratio'
    ]
    
    def __init__(self, contamination: float = 0.05):
        self.contamination = contamination
        self.model = IsolationForest(contamination=self.contamination, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def engineer_features(self, session_df: pd.DataFrame) -> pd.DataFrame:
        df = session_df.copy()
        
        df['avg_amount_30d'] = df['avg_amount_30d'].replace(0, 1e-5)
        df['avg_hourly_tx_30d'] = df.get('avg_hourly_tx_30d', 1).replace(0, 1e-5)
        df['estimated_balance'] = df.get('estimated_balance', df['current_amount'] + 100).replace(0, 1e-5)
        
        df['amount_vs_avg_ratio'] = df['current_amount'] / df['avg_amount_30d']
        df['velocity_spike'] = df['tx_count_1h'] / df['avg_hourly_tx_30d']
        df['balance_drain_ratio'] = df['current_amount'] / df['estimated_balance']
        
        return df

    def prepare_features(self, df: pd.DataFrame) -> np.ndarray:
        missing_cols = [col for col in self.FEATURE_COLUMNS if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
            
        return df[self.FEATURE_COLUMNS].values

    def train(self, dataset_path: str) -> None:
        print(f"Loading dataset from {dataset_path}...")
        df = pd.read_csv(dataset_path)
        
        print("Engineering features...")
        df = self.engineer_features(df)
        X = self.prepare_features(df)
        
        print("Scaling features...")
        X_scaled = self.scaler.fit_transform(X)
        
        print("Training Isolation Forest...")
        self.model.fit(X_scaled)
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
        X = self.prepare_features(df)
        
        session_data_enriched = df.iloc[0].to_dict()
        X_scaled = self.scaler.transform(X)
        
        prediction = self.model.predict(X_scaled)[0]
        score = self.model.score_samples(X_scaled)[0]
        
        normalized_anomaly_score = float(np.clip(0.5 - score, 0, 1))
        
        is_anomaly = bool(prediction == -1)
        panic_score = self.compute_panic_score(session_data_enriched)
        
        intervention_required = is_anomaly and (panic_score > 0.6 or session_data_enriched['balance_drain_ratio'] > 0.9)
        
        anomaly_type = "None"
        if is_anomaly:
            if panic_score > 0.7:
                anomaly_type = "High Panic / Coercion"
            elif session_data_enriched['velocity_spike'] > 5:
                anomaly_type = "Account Takeover / Rapid Transfer"
            else:
                anomaly_type = "Unusual Behavior Pattern"
        
        return {
            'is_anomaly': is_anomaly,
            'anomaly_score': normalized_anomaly_score,
            'panic_score': panic_score,
            'intervention_required': intervention_required,
            'anomaly_type': anomaly_type
        }

    def save(self, filepath: str) -> None:
        if not self.is_trained:
            raise ValueError("Model is not trained yet.")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({'model': self.model, 'scaler': self.scaler}, filepath)
        print(f"Model saved to {filepath}")

    def load(self, filepath: str) -> None:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"No model found at {filepath}")
        
        artifacts = joblib.load(filepath)
        self.model = artifacts['model']
        self.scaler = artifacts['scaler']
        self.is_trained = True
        print(f"Model loaded from {filepath}")


if __name__ == '__main__':
    np.random.seed(42)
    
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
        'new_recipient': np.random.choice([1], size=50),
        'time_of_day': np.random.randint(0, 5, 50),
        'day_of_week': np.random.randint(0, 7, 50),
        'account_age_days': np.random.randint(10, 180, 50),
        'avg_hourly_tx_30d': np.random.uniform(0.1, 0.5, 50),
        'estimated_balance': np.random.uniform(5000, 25000, 50),
        'label': 1
    }
    
    df_normal = pd.DataFrame(normal_data)
    df_anomaly = pd.DataFrame(anomaly_data)
    df_combined = pd.concat([df_normal, df_anomaly]).sample(frac=1).reset_index(drop=True)
    
    dataset_path = 'mock_behavioral_data.csv'
    df_combined.to_csv(dataset_path, index=False)
    
    detector = BehavioralAnomalyDetector(contamination=0.05)
    detector.train(dataset_path)
    
    df_features = detector.engineer_features(df_combined)
    X = detector.prepare_features(df_features)
    X_scaled = detector.scaler.transform(X)
    
    predictions = detector.model.predict(X_scaled)
    pred_labels = [1 if p == -1 else 0 for p in predictions]
    true_labels = df_combined['label'].tolist()
    
    print("\n--- Evaluation Results ---")
    print("Precision:", precision_score(true_labels, pred_labels))
    print("Recall:", recall_score(true_labels, pred_labels))
    print("\nClassification Report:\n", classification_report(true_labels, pred_labels))
    
    if os.path.exists(dataset_path):
        os.remove(dataset_path)
        
    print("\nTest prediction:")
    sample_anomaly = df_anomaly.iloc[0].drop('label').to_dict()
    res = detector.predict_anomaly(sample_anomaly)
    print(res)
