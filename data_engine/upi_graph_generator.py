import pandas as pd
import networkx as nx
import random
import uuid
import os
from datetime import datetime, timedelta

class UPIGraphGenerator:
    def __init__(self):
        self.banks = ['SBI', 'HDFC', 'PNB', 'BOI', 'ICICI', 'Axis']
        self.locations = ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Pune', 'Kolkata', 'Ahmedabad']
        
    def generate_legitimate_users(self, n: int = 5000) -> list[dict]:
        users = []
        for _ in range(n):
            users.append({
                'user_id': str(uuid.uuid4()),
                'bank': random.choice(self.banks),
                'location': random.choice(self.locations),
                'age': random.randint(18, 75),
                'account_age_days': random.randint(30, 3650),
                'typical_tx_amount': random.uniform(100, 5000),
                'is_fraudster': False,
                'fraud_ring_id': 'None'
            })
        return users

    def generate_fraud_ring(self, ring_size: int, victim_count: int, ring_id: str) -> list[dict]:
        nodes = []
        
        scammer = {
            'user_id': str(uuid.uuid4()),
            'bank': random.choice(self.banks),
            'location': random.choice(self.locations),
            'age': random.randint(20, 45),
            'account_age_days': random.randint(1, 30),
            'typical_tx_amount': random.uniform(10000, 50000),
            'is_fraudster': True,
            'role': 'scammer',
            'fraud_ring_id': ring_id
        }
        nodes.append(scammer)
        
        for _ in range(ring_size - 1):
            nodes.append({
                'user_id': str(uuid.uuid4()),
                'bank': random.choice(self.banks),
                'location': random.choice(self.locations),
                'age': random.randint(18, 60),
                'account_age_days': random.randint(1, 100),
                'typical_tx_amount': random.uniform(5000, 20000),
                'is_fraudster': True,
                'role': 'mule',
                'fraud_ring_id': ring_id
            })
            
        for _ in range(victim_count):
            nodes.append({
                'user_id': str(uuid.uuid4()),
                'bank': random.choice(self.banks),
                'location': random.choice(self.locations),
                'age': random.randint(18, 75),
                'account_age_days': random.randint(100, 3000),
                'typical_tx_amount': random.uniform(1000, 10000),
                'is_fraudster': False,
                'role': 'victim',
                'fraud_ring_id': ring_id
            })
            
        return nodes

    def generate_transactions(self, normal_users: list, fraud_rings: list, total_tx: int = 100000) -> pd.DataFrame:
        print("Generating transactions...")
        transactions = []
        start_time = datetime.now() - timedelta(days=30)
        
        all_users = normal_users.copy()
        for ring in fraud_rings:
            all_users.extend(ring)
            
        normal_ids = [u['user_id'] for u in normal_users]
        
        normal_tx_count = int(total_tx * 0.95)
        for _ in range(normal_tx_count):
            sender = random.choice(normal_ids)
            receiver = random.choice(normal_ids)
            while sender == receiver:
                receiver = random.choice(normal_ids)
                
            amount = random.uniform(10, 10000)
            timestamp = start_time + timedelta(minutes=random.randint(0, 30 * 24 * 60))
            
            transactions.append({
                'tx_id': str(uuid.uuid4()),
                'sender_id': sender,
                'receiver_id': receiver,
                'amount': round(amount, 2),
                'timestamp': timestamp,
                'is_fraud': False,
                'fraud_type': 'None',
                'fraud_ring_id': 'None'
            })
            
        for ring in fraud_rings:
            scammer = next(u for u in ring if u.get('role') == 'scammer')
            mules = [u for u in ring if u.get('role') == 'mule']
            victims = [u for u in ring if u.get('role') == 'victim']
            ring_id = scammer['fraud_ring_id']
            
            fraud_type = random.choice(['star_topology', 'mule_chain', 'rapid_drain'])
            
            if fraud_type == 'star_topology':
                for victim in victims:
                    timestamp = start_time + timedelta(minutes=random.randint(0, 30 * 24 * 60))
                    transactions.append({
                        'tx_id': str(uuid.uuid4()),
                        'sender_id': victim['user_id'],
                        'receiver_id': scammer['user_id'],
                        'amount': random.uniform(1000, 50000),
                        'timestamp': timestamp,
                        'is_fraud': True,
                        'fraud_type': fraud_type,
                        'fraud_ring_id': ring_id
                    })
            elif fraud_type == 'mule_chain' and mules:
                for victim in victims:
                    current_sender = victim['user_id']
                    timestamp = start_time + timedelta(minutes=random.randint(0, 30 * 24 * 60))
                    amount = random.uniform(5000, 50000)
                    
                    chain = mules + [scammer]
                    for node in chain:
                        transactions.append({
                            'tx_id': str(uuid.uuid4()),
                            'sender_id': current_sender,
                            'receiver_id': node['user_id'],
                            'amount': amount,
                            'timestamp': timestamp,
                            'is_fraud': True,
                            'fraud_type': fraud_type,
                            'fraud_ring_id': ring_id
                        })
                        current_sender = node['user_id']
                        timestamp += timedelta(minutes=random.randint(1, 15))
                        amount *= 0.95
            elif fraud_type == 'rapid_drain':
                for victim in victims:
                    timestamp = start_time + timedelta(minutes=random.randint(0, 30 * 24 * 60))
                    amount = random.uniform(5000, 20000)
                    for _ in range(random.randint(3, 8)):
                        transactions.append({
                            'tx_id': str(uuid.uuid4()),
                            'sender_id': victim['user_id'],
                            'receiver_id': scammer['user_id'],
                            'amount': amount,
                            'timestamp': timestamp,
                            'is_fraud': True,
                            'fraud_type': fraud_type,
                            'fraud_ring_id': ring_id
                        })
                        timestamp += timedelta(seconds=random.randint(10, 60))
                        
        df = pd.DataFrame(transactions)
        df = df.sort_values(by='timestamp').reset_index(drop=True)
        return df

    def build_networkx_graph(self, transactions_df: pd.DataFrame) -> nx.DiGraph:
        print("Building graph...")
        G = nx.DiGraph()
        for _, row in transactions_df.iterrows():
            G.add_edge(
                row['sender_id'], 
                row['receiver_id'],
                tx_id=row['tx_id'],
                amount=row['amount'],
                timestamp=row['timestamp'],
                is_fraud=row['is_fraud'],
                fraud_type=row['fraud_type']
            )
        return G

    def save_graph_data(self, transactions_df: pd.DataFrame, graph: nx.DiGraph, output_dir: str):
        os.makedirs(output_dir, exist_ok=True)
        csv_path = os.path.join(output_dir, 'upi_transactions.csv')
        graph_path = os.path.join(output_dir, 'upi_graph.gpickle')
        
        transactions_df.to_csv(csv_path, index=False)
        import pickle
        with open(graph_path, 'wb') as f:
            pickle.dump(graph, f)
            
        print(f"Data saved to {output_dir}")

if __name__ == "__main__":
    generator = UPIGraphGenerator()
    normal_users = generator.generate_legitimate_users(5000)
    
    fraud_rings = []
    for i in range(50):
        ring = generator.generate_fraud_ring(
            ring_size=random.randint(2, 6), 
            victim_count=random.randint(5, 20),
            ring_id=f"ring_{i}"
        )
        fraud_rings.append(ring)
        
    df = generator.generate_transactions(normal_users, fraud_rings, total_tx=100000)
    G = generator.build_networkx_graph(df)
    
    output_dir = r"G:\Hackathon\Fintech_ML\FinShield\data_engine\datasets"
    generator.save_graph_data(df, G, output_dir)
    
    print("\n--- Graph Statistics ---")
    print(f"Nodes (Users): {G.number_of_nodes()}")
    print(f"Edges (Transactions): {G.number_of_edges()}")
    print(f"Fraudulent Transactions: {df['is_fraud'].sum()} / {len(df)}")
