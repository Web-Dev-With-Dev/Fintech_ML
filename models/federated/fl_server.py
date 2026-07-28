import logging
from typing import List, Tuple, Dict, Optional, Any, Union
import numpy as np

try:
    import flwr as fl
except ImportError:
    logging.warning("Flower (flwr) not installed. Importing fallback.")
    class fl:
        class server:
            class strategy:
                class FedAvg:
                    pass
                Strategy = Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinShieldStrategy(fl.server.strategy.FedAvg if hasattr(fl, 'server') and hasattr(fl.server, 'strategy') else object):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.history = {
            "round": [],
            "accuracy": [],
            "loss": [],
            "clients_participated": []
        }

    def aggregate_fit(
        self,
        server_round: int,
        results: List[Tuple[Any, Any]],
        failures: List[Union[Tuple[Any, Any], BaseException]],
    ) -> Tuple[Optional[Any], Dict[str, Any]]:
        if not results:
            return None, {}
        aggregated_parameters, metrics = super().aggregate_fit(server_round, results, failures)
        total_samples = sum([fit_res.num_examples for _, fit_res in results])
        weighted_acc = sum([fit_res.metrics.get('accuracy', 0.0) * fit_res.num_examples for _, fit_res in results]) / total_samples
        weighted_loss = sum([fit_res.metrics.get('loss', 0.0) * fit_res.num_examples for _, fit_res in results]) / total_samples
        logger.info(f"--- Round {server_round} Aggregation ---")
        logger.info(f"Clients Participated: {len(results)}")
        logger.info(f"Global Weighted Accuracy: {weighted_acc:.4f}")
        logger.info(f"Global Weighted Loss: {weighted_loss:.4f}")
        self.history["round"].append(server_round)
        self.history["accuracy"].append(weighted_acc)
        self.history["loss"].append(weighted_loss)
        self.history["clients_participated"].append(len(results))
        return aggregated_parameters, {"accuracy": weighted_acc, "loss": weighted_loss}

class FinShieldFLServer:

    def __init__(self, num_rounds: int = 10, min_clients: int = 2):
        self.num_rounds = num_rounds
        self.min_clients = min_clients
        self.strategy = self.get_strategy()
        self.global_weights: List[np.ndarray] = []

    def get_strategy(self) -> Any:
        if not hasattr(fl, 'server'):
            return None
        return FinShieldStrategy(
            fraction_fit=1.0,
            fraction_evaluate=1.0,
            min_fit_clients=self.min_clients,
            min_evaluate_clients=self.min_clients,
            min_available_clients=self.min_clients,
            evaluate_metrics_aggregation_fn=self._aggregate_metrics
        )

    def _aggregate_metrics(self, metrics: List[Tuple[int, Dict[str, float]]]) -> Dict[str, float]:
        if not metrics:
            return {}
        total_examples = sum([num_examples for num_examples, _ in metrics])
        weighted_acc = sum([num_examples * m.get("accuracy", 0) for num_examples, m in metrics]) / total_examples
        return {"accuracy": weighted_acc}

    def start_server(self, port: int = 8080) -> None:
        logger.info(f"Starting FinShield FL Server on port {port} for {self.num_rounds} rounds.")
        if not hasattr(fl, 'server'):
            logger.error("Cannot start server: Flower (flwr) is not installed.")
            return
        fl.server.start_server(
            server_address=f"0.0.0.0:{port}",
            config=fl.server.ServerConfig(num_rounds=self.num_rounds),
            strategy=self.strategy
        )
        self.print_summary()

    def get_global_model_weights(self) -> List[np.ndarray]:
        return self.global_weights

    def print_summary(self) -> None:
        if not hasattr(self.strategy, 'history'):
            return
        history = self.strategy.history
        print("\n" + "="*60)
        print(" " * 15 + "FINSHIELD FL TRAINING SUMMARY")
        print("="*60)
        print(f"{'Round':<10} | {'Clients':<10} | {'Global Acc':<15} | {'Global Loss':<15}")
        print("-" * 60)
        for r, c, a, l in zip(history["round"], history["clients_participated"], history["accuracy"], history["loss"]):
            print(f"{r:<10} | {c:<10} | {a:<15.4f} | {l:<15.4f}")
        print("="*60 + "\n")
