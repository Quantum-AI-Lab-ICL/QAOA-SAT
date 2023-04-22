import torch
from torch.optim import Optimizer
from typing import List

from formula.formula import Formula
from k_sat.pytorch_solver.pytorch_circuit import PytorchCircuit


class PytorchOptimiser:
    def __init__(
        self, circuit: PytorchCircuit, optimiser: Optimizer = None, epochs: int = 250
    ) -> None:
        """Pytorch implementation of optimiser for QAOA circuit parameters.

        Args:
            circuit (PytorchCircuit): Pytorch circuit being optimised over.
            optimiser (Optimizer, optional): Classical optimiser to use for circuit parameters. Defaults to Adam, lr = 0.01
            epochs (int, optional): Epochs to train for. Defaults to 250.
        """
        self.circuit = circuit

        if optimiser is None:
            optimiser = torch.optim.Adam(circuit.parameters(), lr=0.01, maximize=True)
        self.optimiser = optimiser

        self.epochs = epochs

    def find_optimal_params(self, formulas: List[Formula]) -> None:
        """Finds optimal parameters of circuit by maximising success probability over provided formulas.

        Args:
            formulas (List[Formula]): Formulas to maximise success probability over.
        """

        # extract clause counts
        counts = [
            (torch.from_numpy(f.naive_counts), torch.from_numpy(f.naive_sats))
            for f in formulas
        ]

        # optimise
        for i in range(self.epochs + 1):
            self.optimiser.zero_grad()
            p_succs = torch.stack([self.circuit(h, hS) for (h, hS) in counts])
            p_succ = torch.mean(p_succs)
            p_succ.backward()
            self.optimiser.step()
            if i % 10 == 0:
                print(f"Epoch {i}, p_succ: {p_succ.item()}")
