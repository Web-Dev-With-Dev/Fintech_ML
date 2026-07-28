import logging
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from typing import List, Optional

try:
    import torch
    from torch_geometric.data import Data
    HAS_PYG = True
except ImportError:
    HAS_PYG = False
    logging.warning("torch_geometric not installed. PyG conversion will be limited/fallback.")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TransactionGraphBuilder:

    def __init__(self):
        pass

    def build_from_dataframe(self, df: pd.DataFrame) -> nx.DiGraph:
        logger.info("Building directed graph from DataFrame...")
        G = nx.DiGraph()
        
        for _, row in df.iterrows():
            sender = str(row['sender_id'])
            receiver = str(row['receiver_id'])
            amount = float(row['amount'])
            timestamp = row['timestamp']
            is_fraud = row.get('is_fraud', 0)
            
            if not G.has_node(sender):
                G.add_node(sender)
            if not G.has_node(receiver):
                G.add_node(receiver)
                
            G.add_edge(sender, receiver, amount=amount, timestamp=timestamp, is_fraud=is_fraud)

        logger.info(f"Graph built with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
        return G

    def compute_node_features(self, graph: nx.DiGraph) -> pd.DataFrame:
        logger.info("Computing node features...")
        features = []
        
        for node in graph.nodes():
            in_edges = list(graph.in_edges(node, data=True))
            out_edges = list(graph.out_edges(node, data=True))
            
            in_degree = len(in_edges)
            out_degree = len(out_edges)
            
            total_in_amount = sum(e[2].get('amount', 0) for e in in_edges)
            total_out_amount = sum(e[2].get('amount', 0) for e in out_edges)
            
            unique_senders = len(set(e[0] for e in in_edges))
            unique_receivers = len(set(e[1] for e in out_edges))
            
            total_tx = in_degree + out_degree
            total_amount = total_in_amount + total_out_amount
            avg_tx_amount = total_amount / total_tx if total_tx > 0 else 0
            
            tx_velocity = total_tx / 24.0
            balance_drain_ratio = total_out_amount / total_in_amount if total_in_amount > 0 else 0
            temporal_clustering_score = 0.5
            
            node_features = {
                'node_id': node,
                'in_degree': in_degree,
                'out_degree': out_degree,
                'total_in_amount': total_in_amount,
                'total_out_amount': total_out_amount,
                'tx_velocity': tx_velocity,
                'unique_senders': unique_senders,
                'unique_receivers': unique_receivers,
                'avg_tx_amount': avg_tx_amount,
                'balance_drain_ratio': balance_drain_ratio,
                'temporal_clustering_score': temporal_clustering_score
            }
            features.append(node_features)
            
        return pd.DataFrame(features).set_index('node_id')

    def detect_star_topology(self, graph: nx.DiGraph, threshold_victims: int = 5) -> List[str]:
        hubs = []
        for node in graph.nodes():
            in_edges = list(graph.in_edges(node))
            unique_senders = len(set(e[0] for e in in_edges))
            if unique_senders >= threshold_victims:
                hubs.append(node)
        return hubs

    def detect_mule_chains(self, graph: nx.DiGraph, min_hops: int = 3) -> List[List[str]]:
        mule_chains = []
        if graph.number_of_nodes() < 1000:
            for source in graph.nodes():
                for target in graph.nodes():
                    if source != target:
                        paths = nx.all_simple_paths(graph, source=source, target=target, cutoff=min_hops+2)
                        for path in paths:
                            if len(path) >= min_hops + 1:
                                mule_chains.append(path)
        return mule_chains

    def detect_rapid_drain(self, graph: nx.DiGraph, df: pd.DataFrame, window_seconds: int = 300) -> List[str]:
        drained = set()
        df = df.copy()
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            for node in graph.nodes():
                node_out_tx = df[df['sender_id'] == node].sort_values('timestamp')
                if len(node_out_tx) > 1:
                    time_diff = (node_out_tx['timestamp'].max() - node_out_tx['timestamp'].min()).total_seconds()
                    if time_diff <= window_seconds and len(node_out_tx) >= 3:
                        drained.add(node)
        except Exception as e:
            logger.error(f"Error in rapid drain detection: {e}")
        return list(drained)

    def get_subgraph_for_account(self, graph: nx.DiGraph, account_id: str, hops: int = 2) -> nx.DiGraph:
        if account_id not in graph:
            return nx.DiGraph()
            
        nodes_to_include = {account_id}
        current_layer = {account_id}
        
        for _ in range(hops):
            next_layer = set()
            for node in current_layer:
                next_layer.update(graph.predecessors(node))
                next_layer.update(graph.successors(node))
            nodes_to_include.update(next_layer)
            current_layer = next_layer
            
        return graph.subgraph(nodes_to_include).copy()

    def to_pytorch_geometric(self, graph: nx.DiGraph, node_features_df: pd.DataFrame) -> Optional[Data]:
        if not HAS_PYG:
            logger.error("torch_geometric is required for this method. Try 'pip install torch_geometric'")
            return None
            
        node_mapping = {node: i for i, node in enumerate(node_features_df.index)}
        
        edge_index = []
        for u, v in graph.edges():
            if u in node_mapping and v in node_mapping:
                edge_index.append([node_mapping[u], node_mapping[v]])
                
        if not edge_index:
            return None
            
        edge_index = torch.tensor(edge_index, dtype=torch.long).t().contiguous()
        
        x = torch.tensor(node_features_df.values, dtype=torch.float)
        
        return Data(x=x, edge_index=edge_index)

    def visualize_fraud_ring(self, subgraph: nx.DiGraph, output_path: str):
        plt.figure(figsize=(10, 8))
        pos = nx.spring_layout(subgraph)
        nx.draw_networkx_nodes(subgraph, pos, node_size=500, node_color='lightblue')
        nx.draw_networkx_edges(subgraph, pos, width=2, alpha=0.5, edge_color='gray')
        nx.draw_networkx_labels(subgraph, pos, font_size=10, font_family='sans-serif')
        plt.title('Fraud Ring Topology')
        plt.axis('off')
        plt.savefig(output_path)
        plt.close()
        logger.info(f"Fraud ring visualization saved to {output_path}")
