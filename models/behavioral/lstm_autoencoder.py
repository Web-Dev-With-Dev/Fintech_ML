import os
import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any, List

class LSTMAutoencoder(nn.Module):
    def __init__(self, input_size: int = 10, hidden_size: int = 32, num_layers: int = 2):
        super(LSTMAutoencoder, self).__init__()
        
        self.encoder = nn.LSTM(
            input_size=input_size, 
            hidden_size=hidden_size, 
            num_layers=num_layers, 
            batch_first=True
        )
        
        self.decoder = nn.LSTM(
            input_size=hidden_size, 
            hidden_size=hidden_size, 
            num_layers=num_layers, 
            batch_first=True
        )
        
        self.fc = nn.Linear(hidden_size, input_size)
        
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        batch_size, seq_len, _ = x.size()
        
        enc_out, _ = self.encoder(x)
        
        latent = enc_out[:, -1, :]
        
        latent_repeated = latent.unsqueeze(1).repeat(1, seq_len, 1)
        
        dec_out, _ = self.decoder(latent_repeated)
        
        reconstruction = self.fc(dec_out)
        
        return reconstruction, latent

class LSTMAnomalyTrainer:
    def __init__(self, input_size: int = 10, hidden_size: int = 32, num_layers: int = 2):
        self.model = LSTMAutoencoder(input_size, hidden_size, num_layers)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        self.threshold = 0.0
        self.is_trained = False
        
    def prepare_sequences(self, df: pd.DataFrame, seq_len: int = 10) -> np.ndarray:
        data = df.values
        sequences = []
        for i in range(len(data) - seq_len + 1):
            sequences.append(data[i : i + seq_len])
        return np.array(sequences)
        
    def train(self, sequences: np.ndarray, epochs: int = 100, lr: float = 0.001) -> Dict[str, List[float]]:
        self.model.train()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        criterion = nn.MSELoss()
        
        batch_size = 64
        dataset = torch.utils.data.TensorDataset(torch.FloatTensor(sequences))
        dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        history = {'loss': []}
        
        for epoch in range(epochs):
            epoch_loss = 0.0
            for batch in dataloader:
                x = batch[0].to(self.device)
                
                optimizer.zero_grad()
                reconstruction, _ = self.model(x)
                
                loss = criterion(reconstruction, x)
                loss.backward()
                optimizer.step()
                
                epoch_loss += loss.item()
                
            avg_loss = epoch_loss / len(dataloader)
            history['loss'].append(avg_loss)
            
            if (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.6f}")
                
        self.is_trained = True
        return history

    def compute_reconstruction_error(self, sequences: np.ndarray) -> np.ndarray:
        self.model.eval()
        with torch.no_grad():
            x = torch.FloatTensor(sequences).to(self.device)
            reconstruction, _ = self.model(x)
            
            errors = torch.mean((reconstruction - x) ** 2, dim=(1, 2)).cpu().numpy()
        return errors

    def set_threshold(self, normal_errors: np.ndarray, percentile: float = 95.0) -> float:
        self.threshold = float(np.percentile(normal_errors, percentile))
        print(f"Anomaly threshold set to: {self.threshold:.6f}")
        return self.threshold

    def predict_anomaly(self, sequence: np.ndarray) -> Dict[str, Any]:
        if not self.is_trained:
            raise ValueError("Model is not trained.")
        if self.threshold == 0.0:
            raise ValueError("Threshold not set.")
            
        if len(sequence.shape) == 2:
            sequence = np.expand_dims(sequence, axis=0)
            
        error = self.compute_reconstruction_error(sequence)[0]
        is_anomaly = bool(error > self.threshold)
        
        confidence = float(min(error / (self.threshold * 2), 1.0)) if is_anomaly else float(min(1.0 - (error / self.threshold), 1.0))
        
        return {
            'is_anomaly': is_anomaly,
            'reconstruction_error': float(error),
            'threshold': self.threshold,
            'confidence': confidence
        }

    def save_model(self, filepath: str) -> None:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'threshold': self.threshold
        }, filepath)
        print(f"Model saved to {filepath}")

    def load_model(self, filepath: str) -> None:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"No model found at {filepath}")
            
        checkpoint = torch.load(filepath, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.threshold = checkpoint['threshold']
        self.is_trained = True
        print(f"Model loaded from {filepath}")



# ─── Dataset paths ────────────────────────────────────────────────────────────
import os as _os
_BASE       = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..')
_DATASETS   = _os.path.join(_BASE, 'datasets')
PAYSIM_CSV  = _os.path.join(_DATASETS, 'PS_20174392719_1491204439457_log.csv')
IEEE_DIR    = _os.path.join(_DATASETS, 'IEEE fraud deetction')
IEEE_TRAIN  = _os.path.join(IEEE_DIR, 'train_transaction.csv')

LSTM_FEATURE_COLS = [
    'amount_norm', 'step_norm', 'oldbalanceOrg_norm',
    'newbalanceOrig_norm', 'oldbalanceDest_norm',
    'newbalanceDest_norm', 'is_transfer', 'is_cash_out',
    'balance_diff_orig', 'balance_diff_dest'
]


def load_paysim_sequences(path: str, nrows: int = 50_000, seq_len: int = 10) -> tuple:
    """
    Load PaySim and convert to normalized feature sequences for LSTM Autoencoder.
    Returns (normal_sequences, anomaly_sequences)
    """
    from sklearn.preprocessing import MinMaxScaler
    raw = pd.read_csv(path, nrows=nrows)
    print(f"PaySim loaded: {len(raw)} rows | Fraud: {raw['isFraud'].sum()} ({raw['isFraud'].mean():.2%})")

    # Feature engineering
    raw['is_transfer']       = (raw['type'] == 'TRANSFER').astype(float)
    raw['is_cash_out']       = (raw['type'] == 'CASH_OUT').astype(float)
    raw['balance_diff_orig'] = raw['newbalanceOrig'] - raw['oldbalanceOrg']
    raw['balance_diff_dest'] = raw['newbalanceDest'] - raw['oldbalanceDest']

    num_cols = ['amount', 'step', 'oldbalanceOrg', 'newbalanceOrig', 'oldbalanceDest', 'newbalanceDest']
    scaler   = MinMaxScaler()
    scaled   = scaler.fit_transform(raw[num_cols])
    for i, col in enumerate(num_cols):
        raw[f'{col}_norm'] = scaled[:, i]

    feat_df = raw[LSTM_FEATURE_COLS].fillna(0)
    normal  = feat_df[raw['isFraud'] == 0]
    fraud   = feat_df[raw['isFraud'] == 1]

    def make_seqs(df, seq_len):
        arr  = df.values
        seqs = [arr[i:i+seq_len] for i in range(len(arr)-seq_len+1)]
        return np.array(seqs)

    return make_seqs(normal, seq_len), make_seqs(fraud, seq_len)


def load_ieee_sequences(path: str, nrows: int = 50_000, seq_len: int = 10) -> tuple:
    """Load IEEE-CIS and convert to normalized feature sequences."""
    from sklearn.preprocessing import MinMaxScaler
    usecols = ['TransactionDT', 'TransactionAmt', 'isFraud']
    raw = pd.read_csv(path, nrows=nrows, usecols=usecols).fillna(0)
    print(f"IEEE-CIS loaded: {len(raw)} rows | Fraud: {raw['isFraud'].sum()}")

    # Build 10-feature representation
    scaler = MinMaxScaler()
    feats  = pd.DataFrame(scaler.fit_transform(raw[['TransactionDT', 'TransactionAmt']]),
                          columns=['dt_norm', 'amt_norm'])
    for i in range(8):
        feats[f'feat_{i}'] = np.random.randn(len(feats)) * 0.1

    normal = feats[raw['isFraud'].values == 0]
    fraud  = feats[raw['isFraud'].values == 1]

    def make_seqs(df, seq_len):
        arr  = df.values
        seqs = [arr[i:i+seq_len] for i in range(len(arr)-seq_len+1)]
        return np.array(seqs)

    return make_seqs(normal, seq_len), make_seqs(fraud, seq_len)


if __name__ == '__main__':
    print("Running LSTM Autoencoder pipeline...")
    np.random.seed(42)

    seq_len      = 10
    num_features = 10

    # ── Load real dataset ─────────────────────────────────────────────────────
    normal_seqs  = None
    anomaly_seqs = None

    if _os.path.exists(PAYSIM_CSV):
        print(f"Loading PaySim → {PAYSIM_CSV}")
        normal_seqs, anomaly_seqs = load_paysim_sequences(PAYSIM_CSV, nrows=50_000, seq_len=seq_len)
        num_features = normal_seqs.shape[2]

    elif _os.path.exists(IEEE_TRAIN):
        print(f"Loading IEEE-CIS → {IEEE_TRAIN}")
        normal_seqs, anomaly_seqs = load_ieee_sequences(IEEE_TRAIN, nrows=50_000, seq_len=seq_len)
        num_features = normal_seqs.shape[2]

    else:
        print("No real dataset found. Using synthetic data...")
        normal_data  = pd.DataFrame(np.cumsum(np.random.randn(500, num_features), axis=0))
        trainer_tmp  = LSTMAnomalyTrainer(input_size=num_features, hidden_size=16, num_layers=1)
        normal_seqs  = trainer_tmp.prepare_sequences(normal_data, seq_len=seq_len)
        # Simulate anomalies
        anomaly_data = normal_data.copy()
        anomaly_data.iloc[200:210, :] += 10.0
        anomaly_seqs = trainer_tmp.prepare_sequences(anomaly_data, seq_len=seq_len)[200:210]

    print(f"Normal sequences : {normal_seqs.shape}")
    print(f"Anomaly sequences: {anomaly_seqs.shape}")

    # ── Train on normal sequences only (autoencoder learns normal patterns) ──
    trainer = LSTMAnomalyTrainer(input_size=num_features, hidden_size=32, num_layers=2)
    trainer.train(normal_seqs, epochs=20, lr=0.001)

    # ── Set anomaly threshold from normal reconstruction errors ───────────────
    normal_errors = trainer.compute_reconstruction_error(normal_seqs)
    trainer.set_threshold(normal_errors, percentile=95.0)

    # ── Evaluate ──────────────────────────────────────────────────────────────
    print("\nTesting on normal sequence:")
    res_normal = trainer.predict_anomaly(normal_seqs[0])
    print(f"  Normal → {res_normal}")

    if len(anomaly_seqs) > 0:
        print("Testing on anomalous (fraud) sequence:")
        res_anomaly = trainer.predict_anomaly(anomaly_seqs[0])
        print(f"  Anomaly → {res_anomaly}")

    # ── Save model ────────────────────────────────────────────────────────────
    save_path = _os.path.join(
        _os.path.dirname(_os.path.abspath(__file__)), '..', 'saved', 'lstm_autoencoder.pt'
    )
    trainer.save_model(save_path)

