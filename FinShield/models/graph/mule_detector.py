import logging
import pandas as pd
from typing import Dict, Any

from .transaction_graph import TransactionGraphBuilder
from .gat_model import GATTrainer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MuleDetector:
    
    def __init__(self, graph_builder: TransactionGraphBuilder, gat_model: GATTrainer):
        self.graph_builder = graph_builder
        self.gat_model = gat_model
        
    def analyze_account(self, account_id: str, transactions_df: pd.DataFrame) -> Dict[str, Any]:
        graph = self.graph_builder.build_from_dataframe(transactions_df)
        features_df = self.graph_builder.compute_node_features(graph)
        
        star_hubs = self.graph_builder.detect_star_topology(graph)
        mule_chains = self.graph_builder.detect_mule_chains(graph)
        drains = self.graph_builder.detect_rapid_drain(graph, transactions_df)
        
        topology_type = "normal"
        if account_id in star_hubs:
            topology_type = "star_hub"
        elif any(account_id in chain for chain in mule_chains):
            topology_type = "mule_chain"
        elif account_id in drains:
            topology_type = "rapid_drain"
            
        rule_flags = int(topology_type != "normal")
        
        gat_risk_score = 0.0
        try:
            pyg_data = self.graph_builder.to_pytorch_geometric(graph, features_df)
            if pyg_data is not None:
                node_mapping = {node: i for i, node in enumerate(features_df.index)}
                gat_risk_score = self.gat_model.predict_node_risk(pyg_data, account_id, node_mapping)
        except Exception as e:
            logger.warning(f"Failed to get GAT score: {e}")
            
        mule_probability = (rule_flags * 0.4) + (gat_risk_score * 0.6)
        
        hop_depth = max([len(c) for c in mule_chains if account_id in c], default=0)
        
        return {
            "account_id": account_id,
            "mule_probability": min(1.0, mule_probability),
            "fraud_ring_id": f"ring_{account_id[:4]}" if rule_flags else None,
            "hop_depth": hop_depth,
            "topology_type": topology_type,
            "gat_risk_score": gat_risk_score,
            "rule_flags": rule_flags
        }

    def scan_network(self, transactions_df: pd.DataFrame) -> pd.DataFrame:
        graph = self.graph_builder.build_from_dataframe(transactions_df)
        accounts = list(graph.nodes())
        
        results = []
        for acc in accounts:
            analysis = self.analyze_account(acc, transactions_df)
            results.append(analysis)
            
        res_df = pd.DataFrame(results)
        return res_df.sort_values(by="mule_probability", ascending=False)

    def generate_alert(self, account_id: str, analysis: dict, lang: str = "en") -> str:
        prob = analysis.get('mule_probability', 0.0)
        top = analysis.get('topology_type', 'unknown')
        
        if lang == "hi":
            return f"चेतावनी: खाता {account_id} में उच्च धोखाधड़ी संभावना ({prob:.2f}) है। पैटर्न: {top}"
        
        return f"ALERT: Account {account_id} shows high mule probability ({prob:.2f}). Topology: {top}"
