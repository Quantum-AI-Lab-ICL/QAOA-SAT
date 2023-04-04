from qiskit import QuantumCircuit, Aer
from qiskit.utils import QuantumInstance
from typing import List, Dict, Tuple
from scipy.optimize import minimize

from formula.formula import Formula
from k_sat.qiskit_solver.optimiser import Optimiser


class AverageOptimiser(Optimiser):
    """Optimiser to find parameters for QAOA circuit."""

    def __init__(self, quantum_instance: QuantumInstance = None) -> None:
        """Intialise QAOA optimiser.

        Args:
            quantum_instance (QuantumInstace, optional): Backend to run optimiser on. Defaults to Aer qasm simulator.

        """
        if quantum_instance is None:
            quantum_instance = Aer.get_backend("aer_simulator")

        self.quantum_instance = quantum_instance

    def assignment_weighted_average(
        self, formula: Formula, assignments: Dict[str, float]
    ) -> float:
        """Find weighted average of assignment weights (unsatisfied clauses).

        Args:
            formula (Formula): Formula assignments are for.
            assignments (Dict[str, float]): Dictionary of assignments and their counts.

        Returns:
            float: Weighted average of assignment weights.
        """
        weighted_sum = 0
        total_count = 0
        for (ass, count) in assignments.items():
            weighted_sum += count * formula.assignment_weight(ass)
            total_count += count

        return weighted_sum / total_count

    def find_optimal_params(
        self, init_params: List[float], circuits: List[Tuple[Formula, QuantumCircuit]]
    ) -> List[float]:
        """Finds parameters that minimise expectation of cost hamiltonian
                        across all circuit outputs.

        Args:
            init_params (List[float]): Initial circuit parameters (applied to all circuits).
            circuits (List[Tuple[Formula, QuantumCircuit]]): Circuits and corresponding formulas to optimise over.

        Returns:
            List[float]: Optimal parameters.
        """

        def execute_average(param_values: List[float]) -> float:

            total_succ_prob = 0

            for (cnf, circuit) in circuits:
                bound_circuit = circuit.bind_parameters(param_values)
                # Calculate success probability exactly
                if self.quantum_instance.options.method == "statevector":
                    bound_circuit.save_statevector()
                    statevector = (
                        self.quantum_instance.run(bound_circuit)
                        .result()
                        .get_statevector()
                    )
                    circ_output = statevector.probabilities_dict()

                else:
                    # Simulate measurements on circuit
                    bound_circuit.measure_all()
                    circ_output = (
                        self.quantum_instance.run(bound_circuit, shots=1024)
                        .result()
                        .get_counts()
                    )

                # Reverse bitstrings due to qiskit ordering
                rev_output = {s[::-1]: c for (s, c) in circ_output.items()}

                total_succ_prob += self.assignment_weighted_average(cnf, rev_output)

            return total_succ_prob / len(circuits)

        # Minimisation formulation of QAOA
        result = minimize(execute_average, init_params, method="COBYLA")

        return result.x
