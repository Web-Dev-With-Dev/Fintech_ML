import logging
import os
from typing import List, Tuple, Dict, Any, Optional
import numpy as np

try:
    import flwr as fl
    NUMPY_CLIENT_CLASS = fl.client.NumPyClient
except ImportError:
    logging.warning("Flower (flwr) not installed. Falling back to mock NumPyClient.")
    class MockNumPyClient:
        pass
    NUMPY_CLIENT_CLASS = MockNumPyClient

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss
from sklearn.utils import resample

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinShieldFLClient(NUMPY_CLIENT_CLASS):

    def __init__(self, client_id: str, region: str, local_data_path: str, model_type: str = 'scam_sms'):
        self.client_id = client_id
        self.region = region
        self.local_data_path = local_data_path
        self.model_type = model_type
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=1000)),
            ('clf', LogisticRegression(max_iter=100, warm_start=True))
        ])
        self._load_local_data()

    def _load_local_data(self) -> None:
        np.random.seed(hash(self.client_id) % 2**32)
        n_samples = np.random.randint(500, 2000)
        self.X_train = [f"This is a sample message for {self.region} " + str(i) for i in range(n_samples)]
        self.y_train = np.random.randint(0, 2, size=n_samples)
        self.X_test = [f"This is a test message for {self.region} " + str(i) for i in range(n_samples // 5)]
        self.y_test = np.random.randint(0, 2, size=n_samples // 5)
        if not hasattr(self.model.named_steps['clf'], 'coef_'):
            self.model.fit(self.X_train[:10], self.y_train[:10])

    def get_parameters(self, config: Dict[str, str]) -> List[np.ndarray]:
        clf = self.model.named_steps['clf']
        if not hasattr(clf, 'coef_'):
            return []
        return [clf.coef_, clf.intercept_]

    def set_parameters(self, parameters: List[np.ndarray]) -> None:
        clf = self.model.named_steps['clf']
        if not hasattr(clf, 'coef_'):
            self.model.fit(self.X_train[:2], self.y_train[:2])
        if len(parameters) == 2:
            clf.coef_ = parameters[0]
            clf.intercept_ = parameters[1]

    def add_differential_privacy_noise(self, gradients: List[np.ndarray], epsilon: float = 1.0) -> List[np.ndarray]:
        noised_params = []
        for param in gradients:
            noise = np.random.normal(loc=0.0, scale=1.0 / epsilon, size=param.shape)
            noised_params.append(param + noise)
        return noised_params

    def fit(self, parameters: List[np.ndarray], config: Dict[str, str]) -> Tuple[List[np.ndarray], int, Dict[str, Any]]:
        if parameters:
            self.set_parameters(parameters)
        epochs = 5
        clf = self.model.named_steps['clf']
        X_train_transformed = self.model.named_steps['tfidf'].transform(self.X_train)
        for epoch in range(epochs):
            clf.fit(X_train_transformed, self.y_train)
        updated_params = self.get_parameters(config={})
        updated_params = self.add_differential_privacy_noise(updated_params, epsilon=1.5)
        y_pred = self.model.predict(self.X_train)
        y_prob = self.model.predict_proba(self.X_train)
        accuracy = accuracy_score(self.y_train, y_pred)
        loss = log_loss(self.y_train, y_prob)
        logger.info(f"Client {self.client_id} ({self.region}) Fit - Acc: {accuracy:.4f}, Loss: {loss:.4f}, Samples: {len(self.X_train)}")
        return updated_params, len(self.X_train), {"accuracy": accuracy, "loss": loss}

    def evaluate(self, parameters: List[np.ndarray], config: Dict[str, str]) -> Tuple[float, int, Dict[str, Any]]:
        if parameters:
            self.set_parameters(parameters)
        y_pred = self.model.predict(self.X_test)
        y_prob = self.model.predict_proba(self.X_test)
        accuracy = accuracy_score(self.y_test, y_pred)
        loss = log_loss(self.y_test, y_prob)
        logger.info(f"Client {self.client_id} ({self.region}) Eval - Acc: {accuracy:.4f}, Loss: {loss:.4f}")
        return loss, len(self.X_test), {"accuracy": accuracy}

def create_up_client() -> FinShieldFLClient:
    return FinShieldFLClient(client_id="node_up_01", region="UP", local_data_path="./data/up_local.csv")

def create_bihar_client() -> FinShieldFLClient:
    return FinShieldFLClient(client_id="node_br_01", region="Bihar", local_data_path="./data/bihar_local.csv")

def create_tn_client() -> FinShieldFLClient:
    return FinShieldFLClient(client_id="node_tn_01", region="TN", local_data_path="./data/tn_local.csv")

def create_wb_client() -> FinShieldFLClient:
    return FinShieldFLClient(client_id="node_wb_01", region="WB", local_data_path="./data/wb_local.csv")

def create_mh_client() -> FinShieldFLClient:
    return FinShieldFLClient(client_id="node_mh_01", region="MH", local_data_path="./data/mh_local.csv")
