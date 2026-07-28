import pandas as pd
import numpy as np
import random
import uuid
import os
from datetime import datetime, timedelta

class BehavioralDataGenerator:
    def __init__(self):
        pass
        
    def generate_normal_session(self, user_id: str, n_days: int = 30) -> list[dict]:
        sessions = []
        start_time = datetime.now() - timedelta(days=n_days)
        
        avg_amount = random.uniform(500, 5000)
        account_age = random.randint(100, 2000)
        
        for _ in range(random.randint(5, 20)):
            timestamp = start_time + timedelta(days=random.randint(0, n_days), hours=random.randint(8, 22), minutes=random.randint(0, 59))
            
            sessions.append({
                'user_id': user_id,
                'session_id': str(uuid.uuid4()),
                'timestamp': timestamp,
                'tx_count_1h': random.randint(1, 3),
                'avg_amount_30d': avg_amount,
                'current_amount': random.uniform(avg_amount*0.5, avg_amount*1.5),
                'new_recipient': random.choice([0, 0, 0, 1]),
                'time_of_day': timestamp.hour,
                'day_of_week': timestamp.weekday(),
                'account_age_days': account_age,
                'is_anomaly': 0,
                'anomaly_type': 'None'
            })
            
        return sessions

    def generate_scam_session(self, user_id: str, scam_type: str) -> list[dict]:
        sessions = []
        timestamp = datetime.now() - timedelta(days=random.randint(1, 5))
        
        if random.random() < 0.3:
            timestamp = timestamp.replace(hour=random.randint(1, 5))
        else:
            timestamp = timestamp.replace(hour=random.randint(9, 18))
            
        avg_amount = random.uniform(500, 2000)
        account_age = random.randint(100, 2000)
        
        if scam_type == 'panic_transfer':
            tx_count = random.randint(4, 10)
            for i in range(tx_count):
                sessions.append({
                    'user_id': user_id,
                    'session_id': str(uuid.uuid4()),
                    'timestamp': timestamp + timedelta(minutes=i*2),
                    'tx_count_1h': tx_count,
                    'avg_amount_30d': avg_amount,
                    'current_amount': random.uniform(avg_amount*5, avg_amount*20),
                    'new_recipient': 1,
                    'time_of_day': timestamp.hour,
                    'day_of_week': timestamp.weekday(),
                    'account_age_days': account_age,
                    'is_anomaly': 1,
                    'anomaly_type': scam_type
                })
        elif scam_type == 'rapid_drain':
            tx_count = random.randint(3, 7)
            for i in range(tx_count):
                sessions.append({
                    'user_id': user_id,
                    'session_id': str(uuid.uuid4()),
                    'timestamp': timestamp + timedelta(seconds=i*30),
                    'tx_count_1h': tx_count,
                    'avg_amount_30d': avg_amount,
                    'current_amount': random.uniform(avg_amount*2, avg_amount*10),
                    'new_recipient': 1,
                    'time_of_day': timestamp.hour,
                    'day_of_week': timestamp.weekday(),
                    'account_age_days': account_age,
                    'is_anomaly': 1,
                    'anomaly_type': scam_type
                })
                
        return sessions

    def generate_dataset(self, n_users: int = 500) -> pd.DataFrame:
        print(f"Generating behavioral data for {n_users} users...")
        all_sessions = []
        
        for _ in range(n_users):
            user_id = str(uuid.uuid4())
            
            all_sessions.extend(self.generate_normal_session(user_id))
            
            if random.random() < 0.1:
                scam_type = random.choice(['panic_transfer', 'rapid_drain'])
                all_sessions.extend(self.generate_scam_session(user_id, scam_type))
                
        df = pd.DataFrame(all_sessions)
        df = df.sort_values(by=['user_id', 'timestamp']).reset_index(drop=True)
        return df

if __name__ == "__main__":
    generator = BehavioralDataGenerator()
    dataset = generator.generate_dataset(n_users=1000)
    
    output_dir = r"G:\Hackathon\Fintech_ML\FinShield\data_engine\datasets"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'behavioral_sessions.csv')
    
    dataset.to_csv(output_path, index=False)
    print(f"\nBehavioral dataset saved to {output_path}")
    
    print("\n--- Behavioral Data Statistics ---")
    print(f"Total sessions/events: {len(dataset)}")
    print("\nAnomaly Distribution:")
    print(dataset['is_anomaly'].value_counts(normalize=True) * 100)
    print("\nAnomaly Types:")
    print(dataset[dataset['is_anomaly'] == 1]['anomaly_type'].value_counts())
