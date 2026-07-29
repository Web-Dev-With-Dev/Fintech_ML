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
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinShieldFLClient(NUMPY_CLIENT_CLASS):

    def __init__(self, client_id: str, region: str, local_data_path: str, model_type: str = 'scam_sms'):
        self.client_id = client_id
        self.region = region
        self.local_data_path = local_data_path
        self.model_type = model_type
        self.model = Pipeline([
            ('vectorizer', HashingVectorizer(n_features=128, alternate_sign=False)),
            ('clf', LogisticRegression(max_iter=20, warm_start=True))
        ])
        self._load_local_data()

    SCAM_TEMPLATES = {
        "UP":    ["Aapka account band ho jayega OTP dijiye turant",
                  "Aapko prize mila hai 50000 rupaye claim karein abhi",
                  "SBI bank se bol rahe hain KYC update nahi hua account suspend hoga",
                  "Lottery winner aap hain link pe click karein",
                  "Ek baar OTP share karein account block nahi hoga"],
        "Bihar": ["Aapka khata band hoga OTP batao jaldi",
                  "Inam jeet liya hai turant link kholein",
                  "Bank adhikari bol rahe hain KYC karo nahi to account freeze",
                  "50000 ka prize claim karo abhi call karo",
                  "OTP share karo account safe rahega"],
        "TN":    ["Ungal account suspend aagum OTP kodunkal",
                  "Neenga prize winner OTP paarunga link click pannunga",
                  "Bank official pesugiren KYC update illana account block",
                  "50000 rupay claim pannunga link la click pannunga",
                  "Ungal OTP share pannunga account safe aagum"],
        "WB":    ["Apnar account bondho hobe OTP din ekhoni",
                  "Aapni prize jitechen link e click korun",
                  "Bank official bolchi KYC update na hole account freeze",
                  "50000 taka claim korun ekhoni call korun",
                  "OTP share korun account safe thakbe"],
        "MH":    ["Tumcha account band hoel OTP dya lagech",
                  "Tumhi prize jinkla link var click kara",
                  "Bank adhikari bolat ahet KYC update kara nahitar account suspend",
                  "50000 rupaye claim kara abhi call kara",
                  "OTP share kara account surakshit rahil"],
    }

    SAFE_TEMPLATES = {
        "UP":    ["Aaj ka mausam bahut accha hai",
                  "Dukaan se sabzi laana mat bhoolna",
                  "Kal ka meeting rescheduled ho gaya hai",
                  "Bhai ko call karo shaam ko",
                  "Market se dudh laana hai aaj"],
        "Bihar": ["Khana khake aana aaj",
                  "Kal school bandh hai holiday hai",
                  "Chacha ji ka birthday hai kal",
                  "Raste mein traffic hai thoda late hoga",
                  "Meeting 5 baje hai office mein"],
        "TN":    ["Indru kaalai weather nalla irukku",
                  "Kal school holiday irukku",
                  "Kadaila paal vaanga marandhuvidathe",
                  "Traffic jaasthi irukku konjam late aagalam",
                  "Meeting 5 manikku office la irukku"],
        "WB":    ["Aaj rasta onek jam ache",
                  "Kal school bondho ache",
                  "Bazaar theke dudh aneche",
                  "Bhai ke phone koro bikel e",
                  "Meeting ta 5 tar office e"],
        "MH":    ["Aaj rasta khup jam ahe",
                  "Udya school band ahe",
                  "Bajar madhun dudh ana",
                  "Bhavala phone kar sandhyakali",
                  "Meeting 5 vajta office madhye ahe"],
    }

    def _load_local_data(self) -> None:
        rng = np.random.default_rng(hash(self.client_id) % 2**32)
        region = self.region
        scam_pool = self.SCAM_TEMPLATES.get(region, self.SCAM_TEMPLATES["UP"]) * 40
        safe_pool = self.SAFE_TEMPLATES.get(region, self.SAFE_TEMPLATES["UP"]) * 40

        n_scam = int(rng.integers(200, 600))
        n_safe = int(rng.integers(200, 600))

        scam_idx = rng.integers(0, len(scam_pool), size=n_scam)
        safe_idx  = rng.integers(0, len(safe_pool),  size=n_safe)

        X_scam = [scam_pool[i] for i in scam_idx]
        X_safe = [safe_pool[i]  for i in safe_idx]

        X = X_scam + X_safe
        y = np.array([1] * n_scam + [0] * n_safe)

        shuffle_idx = rng.permutation(len(X))
        X = [X[i] for i in shuffle_idx]
        y = y[shuffle_idx]

        split = int(0.8 * len(X))
        self.X_train, self.X_test = X[:split], X[split:]
        self.y_train, self.y_test = y[:split], y[split:]

        self.model.fit(self.X_train, self.y_train)


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
            clf.coef_ = np.array(parameters[0], copy=True)
            clf.intercept_ = np.array(parameters[1], copy=True)

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
        X_train_transformed = self.model.named_steps['vectorizer'].transform(self.X_train)
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
