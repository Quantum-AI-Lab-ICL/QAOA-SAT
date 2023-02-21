from qiskit import Aer
from qiskit.utils import QuantumInstance
from typing import List, Tuple
from qiskit import Aer

from formula.formula import Formula
from k_sat.solver import Solver
from k_sat.quantum_solver.qaoa_encoder import QAOAEncoder
from k_sat.quantum_solver.qaoa_optimiser import QAOAOptimiser
from k_sat.quantum_solver.pauli_encoder import PauliEncoder
from k_sat.quantum_solver.average_optimiser import AverageOptimiser
from k_sat.quantum_solver.qaoa_evaluator import QAOAEvaluator


class QuantumSolver(Solver):
    """Quantum solver for k-SAT problems using QAOA."""

    def __init__(
        self,
        formula: Formula,
        training_formulas: List[Formula] = None,
        layers: int = 1,
        quantum_instance: QuantumInstance = None,
        init_params: List[float] = None,
        encoder: QAOAEncoder = None,
        optimiser: QAOAOptimiser = None
    ) -> None:
        """Intialise Quantum Solver for k-SAT.

        Args:
            formula (Formula): Formula to find satisfying assignment of.
            training_formulas (List[Formula], optional): Formulas to use for parameter optimisation. Defaults to formula.
            layers (int, optional): Number of layers in ansatzes. Defaults to 1.
            quantum_instance (QuantumInstace, optional): Backend to run quantum solver on. Defaults to Aer qasm simulator.
            encoder (QAOAEncoder, optional): Encoder to encode formula into circuit. Defaults to PauliEncoder.
            init_params (List[float], optional): Initial value of parameters for ansatzes. Defaults to a list of 1s.
            optimiser (QAOAOptimiser, optional): Optimiser to find optimal circuit parameters. Defaults to AverageOptimiser.

        Raises:
            RuntimeError: Invalid number of initial parameters

        """
        self.formula = formula

        # If no training formulas specified, tailor training to formula itself
        if training_formulas is None:
            training_formulas = [formula]
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

    def sat(self) -> Tuple[str, int]:
        """Finds statisfying assignment of formula.

        Returns:
            Tuple[str, int]: Tuple of satisfying assignment and runtime to find it.

        """

        # Train
        print("Encoding training formulas into quantum circuits")
        training_circuits = [(formula, self.encoder.encode_formula(formula, self.layers)) for formula in self.training_formulas]

        print("Finding optimal parameters for training circuits")
        optimal_params = self.optimiser.find_optimal_params(self.init_params, training_circuits)

        # Evaluate
        print("Finding/evaluating satisfying assignment")
        circuit = self.encoder.encode_formula(self.formula, self.layers)

        # Store for later analysis
        self.evaluator = QAOAEvaluator(circuit, self.formula, optimal_params)
        return self.evaluator.running_time()