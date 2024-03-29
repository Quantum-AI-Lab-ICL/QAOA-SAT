from qiskit import Aer
from qiskit.utils import QuantumInstance
from typing import List, Tuple
from qiskit import Aer
from qiskit.visualization import plot_histogram
from matplotlib.figure import Figure

from formula.cnf.cnf import CNF
from k_sat.solver import Solver
from k_sat.qiskit_solver.encoder import Encoder
from k_sat.qiskit_solver.optimiser import Optimiser
from k_sat.qiskit_solver.pauli_encoder import PauliEncoder
from k_sat.qiskit_solver.average_optimiser import AverageOptimiser
from k_sat.qiskit_solver.evaluator import Evaluator


class QiskitSolver(Solver):
    """Quantum solver for k-SAT problems using QAOA."""

    def __init__(
        self,
        training_formulas: List[CNF] = None,
        layers: int = 1,
        quantum_instance: QuantumInstance = None,
        init_params: List[float] = None,
        encoder: Encoder = None,
        optimiser: Optimiser = None,
    ) -> None:
        """Intialise Quantum Solver for k-SAT.

        Args:
            training_formulas (List[CNF], optional): CNFs to use for parameter optimisation. Defaults to formula.
            layers (int, optional): Number of layers in ansatzes. Defaults to 1.
            quantum_instance (QuantumInstace, optional): Backend to run quantum solver on. Defaults to Aer qasm simulator.
            encoder (Encoder, optional): Encoder to encode formula into circuit. Defaults to PauliEncoder.
            init_params (List[float], optional): Initial value of parameters for ansatzes. Defaults to a list of 1s.
            optimiser (Optimiser, optional): Optimiser to find optimal circuit parameters. Defaults to AverageOptimiser.

        Raises:
            RuntimeError: Invalid number of initial parameters

        """

        self.training_formulas = training_formulas

        self.layers = layers

        if quantum_instance is None:
            quantum_instance = Aer.get_backend("aer_simulator")
        self.quantum_instance = quantum_instance

        # If not specified, use Pauli Z encoder
        if encoder is None:
            encoder = PauliEncoder()
        self.encoder = encoder

        if init_params is not None and len(init_params) != 2 * layers:
            raise RuntimeError(
                f"Invalid number of initial parameters supplied, expected {2 * layers}, received {len(init_params)})"
            )
        # If not specified, initialise gamma_i = -0.01, beta_i = 0.01 [BM22]
        if init_params is None:
            init_params = [-0.01, 0.01] * layers

        self.init_params = init_params

        # If not specified use average optimiser (non-CvAR)
        if optimiser is None:
            optimiser = AverageOptimiser(quantum_instance)
        self.optimiser = optimiser

    def sat(self, formula: CNF, timeout: int = None) -> Tuple[str, int]:
        """Finds statisfying assignment of formula.

        Args:
            formula (CNF): CNF to find satisfying assignment of.
            timeout (int, optional): Timeout for algorithm if no satisfying assignment found yet. Defaults to None (keep going until solution found).

        Returns:
            Tuple[str, int]: Tuple of satisfying assignment and runtime to find it. String set to "-1" formula unsatisfiable/solver timed out.
        """
        # If no training formulas specified, tailor training to formula itself
        training_formulas = (
            self.training_formulas if self.training_formulas is not None else [formula]
        )

        # Train
        print("Encoding training formulas into quantum circuits")
        training_circuits = [
            (formula, self.encoder.encode_formula(formula, self.layers))
            for formula in training_formulas
        ]

        print("Finding optimal parameters for training circuits")
        optimal_params = self.optimiser.find_optimal_params(
            self.init_params, training_circuits
        )

        # Evaluate
        print("Finding/evaluating satisfying assignment")
        circuit = self.encoder.encode_formula(formula, self.layers)

        # Store for later analysis
        self.evaluator = Evaluator()
        self.optimal_params = optimal_params
        return self.evaluator.running_time(circuit, formula, optimal_params, timeout)

    def visualise_result(
        self,
        formula: CNF,
        plot_num: int = 10,
        shots: int = 10000,
    ) -> Figure:
        """Visualise output of solving circuit for given formula.

        Args
                formula (CNF): CNF to visualise encoded circuit of.
                plot_num (int, optional): Number of bitstrings to plot (sorted in descending order of counts). Defaults to 10.
                shots (int, optional): Samples to draw from circuit. Defaults to 10000.

        Raises:
                RuntimeError: Must run solver before visualising results.

        Returns:
                Figure: Histogram of samples drawn.
        """

        if self.optimal_params is None:
            raise RuntimeError("Must run solver before visualising results")

        # Initialise simulator
        quantum_instance = Aer.get_backend("aer_simulator")

        # Add measurement operation to circuit
        circuit = self.encoder.encode_formula(formula).bind_parameters(
            self.optimal_params
        )
        circuit.measure_all()

        # Measure and reverse bitstrings for qiskit ordering
        counts = {
            k[::-1]: v
            for (k, v) in quantum_instance.run(circuit, shots=shots)
            .result()
            .get_counts()
            .items()
        }

        return plot_histogram(counts, sort="value_desc", number_to_keep=plot_num)
