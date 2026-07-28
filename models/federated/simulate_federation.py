import os
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Any, Tuple
import logging

from models.federated.fl_client import (
    create_up_client,
    create_bihar_client,
    create_tn_client,
    create_wb_client,
    create_mh_client
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FederationSimulator:

    def __init__(self, n_rounds: int = 10):
        self.n_rounds = n_rounds
        self.clients = self.initialize_clients()

    def initialize_clients(self) -> List[Any]:
        logger.info("Initializing regional federated learning clients...")
        clients = [
            create_up_client(),
            create_bihar_client(),
            create_tn_client(),
            create_wb_client(),
            create_mh_client()
        ]
        logger.info(f"Initialized {len(clients)} clients successfully.")
        return clients

    def _aggregate_weights_fedavg(self, client_weights: List[List[np.ndarray]], sample_counts: List[int]) -> List[np.ndarray]:
        total_samples = sum(sample_counts)
        aggregated = []
        num_layers = len(client_weights[0])
        for layer_idx in range(num_layers):
            weighted_sum = np.zeros_like(client_weights[0][layer_idx], dtype=np.float64)
            for i, weights in enumerate(client_weights):
                weighted_sum += weights[layer_idx] * sample_counts[i]
            aggregated.append(weighted_sum / total_samples)
        return aggregated

    def run_round(self, round_num: int, global_weights: List[np.ndarray]) -> Tuple[List[np.ndarray], Dict[str, Any]]:
        logger.info(f"\n{'='*20} ROUND {round_num} {'='*20}")
        client_weights = []
        sample_counts = []
        round_metrics = {
            "client_metrics": []
        }
        for client in self.clients:
            updated_params, num_samples, metrics = client.fit(global_weights, config={"round": str(round_num)})
            client_weights.append(updated_params)
            sample_counts.append(num_samples)
            metrics['client_id'] = client.client_id
            metrics['region'] = client.region
            round_metrics["client_metrics"].append(metrics)
        aggregated_weights = self._aggregate_weights_fedavg(client_weights, sample_counts)
        total_samples = sum(sample_counts)
        global_acc = sum([m['accuracy'] * c for m, c in zip(round_metrics["client_metrics"], sample_counts)]) / total_samples
        global_loss = sum([m['loss'] * c for m, c in zip(round_metrics["client_metrics"], sample_counts)]) / total_samples
        round_metrics["global_accuracy"] = global_acc
        round_metrics["global_loss"] = global_loss
        logger.info(f"Round {round_num} Global Accuracy: {global_acc:.4f} | Loss: {global_loss:.4f}")
        return aggregated_weights, round_metrics

    def run_simulation(self) -> Dict[str, Any]:
        history = {
            "global_accuracy": [],
            "global_loss": [],
            "per_client": {client.region: {"accuracy": [], "loss": []} for client in self.clients}
        }
        global_weights = self.clients[0].get_parameters({})
        for r in range(1, self.n_rounds + 1):
            global_weights, metrics = self.run_round(r, global_weights)
            history["global_accuracy"].append(metrics["global_accuracy"])
            history["global_loss"].append(metrics["global_loss"])
            for client_metric in metrics["client_metrics"]:
                region = client_metric["region"]
                history["per_client"][region]["accuracy"].append(client_metric["accuracy"])
                history["per_client"][region]["loss"].append(client_metric["loss"])
        return history

    def plot_federation_results(self, history: Dict[str, Any], output_path: str) -> None:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        rounds = list(range(1, len(history["global_accuracy"]) + 1))
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        ax1.plot(rounds, history["global_accuracy"], 'g-', marker='o', linewidth=2, label='Global Accuracy')
        ax1.plot(rounds, history["global_loss"], 'r-', marker='x', linewidth=2, label='Global Loss')
        ax1.set_title("FinShield FL: Global Model Convergence")
        ax1.set_xlabel("Communication Round")
        ax1.set_ylabel("Metric Value")
        ax1.grid(True, linestyle='--', alpha=0.7)
        ax1.legend()
        colors = ['b', 'c', 'm', 'y', 'orange']
        for idx, (region, metrics) in enumerate(history["per_client"].items()):
            ax2.plot(rounds, metrics["accuracy"], color=colors[idx % len(colors)], 
                     marker='s', linestyle='--', alpha=0.8, label=f'{region} Accuracy')
        ax2.set_title("Per-Region Client Accuracy Over Rounds")
        ax2.set_xlabel("Communication Round")
        ax2.set_ylabel("Accuracy")
        ax2.grid(True, linestyle='--', alpha=0.7)
        ax2.legend()
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"Saved simulation plots to {output_path}")

    def generate_report(self, history: Dict[str, Any]) -> str:
        final_global_acc = history["global_accuracy"][-1]
        report = []
        report.append("="*60)
        report.append(f"{'FINSHIELD FEDERATED LEARNING REPORT':^60}")
        report.append("="*60)
        report.append("\n[Privacy Guarantees]")
        report.append("- Raw user data never left local regional nodes.")
        report.append("- Differential Privacy (Gaussian Noise) applied to all client gradients.")
        report.append("- Communication limited to aggregated weight updates.\n")
        report.append("[Global Convergence]")
        report.append(f"Total Rounds Simulated : {self.n_rounds}")
        report.append(f"Final Global Accuracy  : {final_global_acc:.4f}\n")
        report.append("[Regional Client Performance (Final Round)]")
        report.append(f"{'Region':<10} | {'Final Accuracy':<15} | {'Final Loss':<15}")
        report.append("-" * 45)
        for region, metrics in history["per_client"].items():
            f_acc = metrics["accuracy"][-1]
            f_loss = metrics["loss"][-1]
            report.append(f"{region:<10} | {f_acc:<15.4f} | {f_loss:<15.4f}")
        report.append("\n" + "="*60)
        return "\n".join(report)

if __name__ == '__main__':
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    print("Starting FinShield Federated Learning Simulation...")
    simulator = FederationSimulator(n_rounds=10)
    training_history = simulator.run_simulation()
    report_text = simulator.generate_report(training_history)
    print("\n" + report_text)
    output_dir = r"G:\Hackathon\Fintech_ML\FinShield\evaluate\outputs"
    output_file = os.path.join(output_dir, "fl_convergence_plot.png")
    simulator.plot_federation_results(training_history, output_file)
    print(f"\nSimulation complete. Plot saved to: {output_file}")
