from torch.distributions.categorical import Categorical
from typing import List, Tuple

from k_sat.solver import Solver
from k_sat.pytorch_solver.pytorch_circuit import PytorchCircuit
from k_sat.pytorch_solver.pytorch_optimiser import PytorchOptimiser
from formula.cnf.cnf import CNF


class PytorchSolver(Solver):
    def __init__(
        self, training_formulas: List[CNF] = None, layers: int = 1
    ) -> None:
        """Pytorch implementation of QAOA for satisfiability.

        Args:
            training_formulas (List[Formula], optional): Formulas to train parameters on. Defaults to formula being solved for.
            layers (int, optional): Layers in QAOA circuit. Defaults to 1.
        """
        self.training_formulas = training_formulas
        self.layers = layers

    def sat(self, formula: CNF, timeout: int = None) -> Tuple[str, int]:
        """Finds statisfying assignment of formula.

        Args:
            formula (CNF): Formula to find satisfying assignment for.
            timeout (int, optional): Timeout for algorithm if no satisfying assignment found yet. Defaults to None (keep going until solution found).

        Returns:
            Tuple[str, int]: Tuple of satisfying assignment and runtime to find it. String set to "-1" formula unsatisfiable/solver timed out.
        """

        # QAOA circuit
        print("Initialising network")
        circuit = PytorchCircuit(formula.num_vars, self.layers)

        optimiser = PytorchOptimiser(circuit)
        # find optimal parameters (use formula itself if no training formulas specified)
        formulas = (
            [formula] if self.training_formulas is None else self.training_formulas
        )
        print("Finding optimal params")
        optimiser.find_optimal_params(formulas)

        # Emulate sampling
        final_state = circuit.evolve(formula.naive_counts)
        ps = (final_state * final_state.conj()).real
        m = Categorical(ps)

        # Timeout flag
        tf = False

        # Sample until satisfying assignment found or timeout reached
        runtime = 0
        while True:
            if timeout is not None and runtime > timeout:
                tf = True
                break
            runtime += 1
            bs = bin(m.sample())[2:].zfill(formula.num_vars)
            if formula.is_satisfied(bs):
                break
            if runtime % 10 == 0:
                print(f"Samples drawn: {runtime}")

        # Set bitstring to -1 if timeout
        bs = "-1" if tf else bs

        return bs, runtime
