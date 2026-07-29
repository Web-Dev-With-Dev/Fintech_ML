import logging
import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

try:
    from torch_geometric.nn import GATConv
    from torch_geometric.data import Data
    HAS_PYG = True
except ImportError:
    HAS_PYG = False
    logging.warning("torch_geometric not installed! Falling back to PyTorch-only GraphSAGE-style model.")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


if HAS_PYG:
    class FraudGATModel(nn.Module):

        def __init__(self, in_channels: int = 10, hidden_channels: int = 64, out_channels: int = 1):
            super(FraudGATModel, self).__init__()
            self.conv1 = GATConv(in_channels, hidden_channels, heads=8, concat=True, dropout=0.3)
            self.conv2 = GATConv(hidden_channels * 8, hidden_channels, heads=8, concat=True, dropout=0.3)
            self.conv3 = GATConv(hidden_channels * 8, out_channels, heads=1, concat=False, dropout=0.3)
            
            self.lin1 = nn.Linear(in_channels, hidden_channels * 8)
            self.lin2 = nn.Linear(hidden_channels * 8, hidden_channels * 8)

        def forward(self, x, edge_index):
            x_res1 = self.lin1(x)
            x1 = self.conv1(x, edge_index)
            x1 = F.elu(x1 + x_res1)
            x1 = F.dropout(x1, p=0.3, training=self.training)
            
            x_res2 = self.lin2(x1)
            x2 = self.conv2(x1, edge_index)
            x2 = F.elu(x2 + x_res2)
            x2 = F.dropout(x2, p=0.3, training=self.training)
            
            logits = self.conv3(x2, edge_index)
            return logits.squeeze()
else:
    class FraudGATModel(nn.Module):
        def __init__(self, in_channels: int = 10, hidden_channels: int = 64, out_channels: int = 1):
            super(FraudGATModel, self).__init__()
            logger.info("Using Fallback MLP-based 'GNN' as PyG is absent.")
            self.fc1 = nn.Linear(in_channels, hidden_channels * 8)
            self.fc2 = nn.Linear(hidden_channels * 8, hidden_channels * 8)
            self.fc3 = nn.Linear(hidden_channels * 8, out_channels)
            self.dropout = nn.Dropout(0.3)
            
        def forward(self, x, edge_index):
            x_res1 = self.fc1(x)
            x1 = F.elu(self.fc1(x))
            x1 = x1 + x_res1
            x1 = self.dropout(x1)
            
            x_res2 = self.fc2(x1)
            x2 = F.elu(self.fc2(x1))
            x2 = x2 + x_res2
            x2 = self.dropout(x2)
            
            logits = self.fc3(x2)
            return logits.squeeze()


class GATTrainer:
    
    def __init__(self, device: str = 'cpu'):
        self.device = device
        self.model = FraudGATModel().to(self.device)
        self.optimizer = None

    def train(self, data, labels: torch.Tensor, epochs: int = 200, lr: float = 0.005) -> dict:
        self.model.train()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=lr, weight_decay=1e-4)
        
        x = data.x.to(self.device)
        edge_index = data.edge_index.to(self.device) if hasattr(data, 'edge_index') else None
        y = labels.to(self.device)
        
        # Calculate class imbalance weighting
        num_pos = (y == 1).sum().item()
        num_neg = (y == 0).sum().item()
        pos_weight = torch.tensor([num_neg / max(1, num_pos)], device=self.device)
        
        criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
        history = {'loss': []}
        
        for epoch in range(epochs):
            self.optimizer.zero_grad()
            
            if edge_index is not None:
                logits = self.model(x, edge_index)
            else:
                logits = self.model(x, None)
                
            loss = criterion(logits, y)
            loss.backward()
            self.optimizer.step()
            
            history['loss'].append(loss.item())
            
            if (epoch + 1) % 50 == 0:
                logger.info(f"Epoch {epoch+1}/{epochs}, Loss: {loss.item():.4f}")
                
        return history

    def evaluate(self, data, labels: torch.Tensor) -> dict:
        from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
        self.model.eval()
        with torch.no_grad():
            x = data.x.to(self.device)
            edge_index = data.edge_index.to(self.device) if hasattr(data, 'edge_index') else None
            y_true = labels.numpy()
            
            if edge_index is not None:
                logits = self.model(x, edge_index)
            else:
                logits = self.model(x, None)
                
            probs = torch.sigmoid(logits).cpu().numpy()
            preds = (probs > 0.5).astype(int)
            
            precision = float(precision_score(y_true, preds, zero_division=0))
            recall = float(recall_score(y_true, preds, zero_division=0))
            f1 = float(f1_score(y_true, preds, zero_division=0))
            try:
                auc = float(roc_auc_score(y_true, probs))
            except Exception:
                auc = 0.5
            
        return {'precision': precision, 'recall': recall, 'f1': f1, 'auc_roc': auc}


    def predict_node_risk(self, data, account_id: str, node_mapping: dict) -> float:
        self.model.eval()
        with torch.no_grad():
            x = data.x.to(self.device)
            edge_index = data.edge_index.to(self.device) if hasattr(data, 'edge_index') else None
            
            if edge_index is not None:
                logits = self.model(x, edge_index)
            else:
                logits = self.model(x, None)
                
            probs = torch.sigmoid(logits)
            node_idx = node_mapping.get(account_id)
            if node_idx is not None and node_idx < probs.size(0):
                return probs[node_idx].item()
            return 0.0

    def save_model(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        torch.save(self.model.state_dict(), path)
        logger.info(f"Model saved to {path}")

    def load_model(self, path: str):
        self.model.load_state_dict(torch.load(path, map_location=self.device))
        self.model.eval()
        logger.info(f"Model loaded from {path}")


if __name__ == '__main__':
    from sklearn.preprocessing import StandardScaler
    from models.graph.transaction_graph import TransactionGraphBuilder, load_paysim_as_graph_df
    
    _BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
    PAYSIM_CSV = os.path.join(_BASE, 'datasets', 'PS_20174392719_1491204439457_log.csv')
    
    if os.path.exists(PAYSIM_CSV):
        logger.info(f"Loading PaySim Graph Data from {PAYSIM_CSV}...")
        df = load_paysim_as_graph_df(PAYSIM_CSV, nrows=50000)
    else:
        logger.warning("PaySim dataset not found. Generating synthetic graph data...")
        n = 500
        df = pd.DataFrame({
            'sender_id': [f'C{i:04d}' for i in range(n)],
            'receiver_id': [f'M{i % 50:04d}' for i in range(n)],
            'amount': [round(1000 * (i % 10 + 1), 2) for i in range(n)],
            'timestamp': pd.date_range('2023-01-01', periods=n, freq='1h'),
            'is_fraud': [1 if i % 15 == 0 else 0 for i in range(n)]
        })

    builder = TransactionGraphBuilder()
    G = builder.build_from_dataframe(df)
    node_features_df = builder.compute_node_features(G)
    
    # Compute true node labels: 1 if node was involved in a fraud transaction
    fraud_senders = set(df[df['is_fraud'] == 1]['sender_id'])
    fraud_receivers = set(df[df['is_fraud'] == 1]['receiver_id'])
    fraud_nodes = fraud_senders.union(fraud_receivers)
    
    node_labels = torch.tensor(
        [1.0 if node in fraud_nodes else 0.0 for node in node_features_df.index],
        dtype=torch.float
    )
    logger.info(f"Total Graph Nodes: {len(node_labels)} | Fraud Nodes: {int(node_labels.sum())}")

    # Scale node features to prevent exploding gradients
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(node_features_df.values)
    x_tensor = torch.tensor(scaled_features, dtype=torch.float)

    # Prepare PyG/Tensor graph representation
    edge_index = []
    node_mapping = {node: i for i, node in enumerate(node_features_df.index)}
    for u, v in G.edges():
        if u in node_mapping and v in node_mapping:
            edge_index.append([node_mapping[u], node_mapping[v]])
            
    if edge_index:
        edge_tensor = torch.tensor(edge_index, dtype=torch.long).t().contiguous()
    else:
        edge_tensor = torch.zeros((2, 0), dtype=torch.long)
        
    if HAS_PYG:
        data = Data(x=x_tensor, edge_index=edge_tensor)
    else:
        class GraphData:
            pass
        data = GraphData()
        data.x = x_tensor
        data.edge_index = edge_tensor


    trainer = GATTrainer()
    logger.info("Training GAT Model on PaySim Graph...")
    history = trainer.train(data, node_labels, epochs=150, lr=0.005)
    metrics = trainer.evaluate(data, node_labels)
    logger.info(f"Evaluation Metrics on PaySim Graph: {metrics}")

    save_path = os.path.join(_BASE, 'models', 'saved', 'gat_model.pt')
    trainer.save_model(save_path)

