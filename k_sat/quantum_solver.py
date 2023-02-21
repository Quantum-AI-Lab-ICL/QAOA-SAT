import numpy as np
import math

from qiskit import QuantumCircuit, Aer
from qiskit.visualization import plot_histogram
from qiskit.utils import QuantumInstance
from qiskit.circuit import Parameter
from typing import List, Dict
from qiskit import Aer, transpile, assemble
from scipy.optimize import minimize
from itertools import combinations
from matplotlib.figure import Figure

from formula.cnf import CNF
from formula.clause import Clause
from k_sat.solver import Solver



class QuantumSolver(Solver):
    """Quantum solver for k-SAT problems using QAOA."""

    def __init__(
        self,
        cnfs: List[CNF],
        layers: int = 1,
        init_params: List[float] = None,
        quantum_instance: QuantumInstance = None,
        top_avg: float = 1,
    ) -> None:
        """Intialise Quantum Solver for maxsat.
            If multiple CNF formulas are provided, the solver optimises
            one set of parameters using the average of success probabilities
            over all instances.

        Args:
            cnfs (List[CNF]): CNF formulas to find satisfying assignments of.
            layers (int, optional): Number of layers in ansatzes. Defaults to 1.
            init_params (List[float], optional): Initial value of parameters for ansatzes. Defaults to a list of 1s.
            quantum_instance (QuantumInstace, optional): Backend to run quantum solver on. Defaults to Aer qasm simulator.
            top_avg (float, optional): Proportion of assignments to consider in expectation calculation. Defaults to 1.

        Raises:
            RuntimeError: Invalid number of initial parameters
        """

        if init_params is not None and len(init_params) != 2 * layers:
            raise RuntimeError(
                f"Invalid number of initial parameters supplied, expected {2 * layers}, received {len(init_params)})"
            )

        # If not specified, initialise gamma_i = -0.01, beta_i = 0.01 [BM22] 
        if init_params is None:
            init_params = [-0.01, 0.01] * layers 

        if quantum_instance is None:
            quantum_instance = Aer.get_backend("aer_simulator")

        self.cnfs = cnfs
        self.layers = layers
        self.init_params = init_params
        self.quantum_instance = quantum_instance
        self.top_avg = top_avg

    def assignment_weighted_average(
        self, cnf: CNF, assignments: Dict[str, float], alpha: float
    ) -> float:
        """Find weighted average of top alpha proportion of assignment weights (unsatisfied clauses).

        Args:
            cnf (CNF): Formula assignments are for.
            assignments (Dict[str, float]): Dictionary of assignments and their counts.
            alpha (float): Proportion of assignments to consider.

        Returns:
            float: Weighted average of assignment weights.
        """
        assert alpha <= 1 and alpha > 0

        # Assignments to consider
        considered = sorted(
            assignments.items(), key=lambda item: item[1], reverse=True
        )[:math.ceil(alpha * len(assignments))]


        # Find average of assignment weights (number of satisfied clauses)
        weighted_sum = 0
        total_count = 0
        for (ass, count) in considered:
            weighted_sum += count * cnf.assignment_weight(ass)
            total_count += count

        return weighted_sum / total_count

    def encode_clause(self, clause: Clause, gamma: Parameter, circuit: QuantumCircuit) -> QuantumCircuit:
        """ Append unitary gates encoding clause to provided quantum circuit.

        Args:
            clause (CNF): Clause to be encoded.
            gamma (Parameter): Parameter to parameterise gates with.
            circuit (QuantumCircuit): Circuit to append gates to.

        Returns:
            QuantumCircuit: Circuit with appended gates encoding clause.
        """

        if clause.always_sat:

            # No application of gates in cases where clause is un-unsatisfiable
            return circuit

        else:

            for i in range(0, clause.num_vars):

                # Fourier term
                ft = i + 1

                # Generate combinations
                combs = combinations(clause.variables, ft)

                # Negative angle for odd fourier term
                angle = ((-1) ** (ft % 2)) * gamma / (2 ** (clause.num_vars - 1))

                for comb in combs:

                    # Combined parity of terms
                    parity = np.prod([1 if x.is_negation else -1 for x in comb]) 

                    # Apply CNOT gates
                    for j in range(0, i):
                        circuit.cx(comb[j].id, comb[j + 1].id)

                    # Apply RZ gate
                    circuit.rz(angle * parity, comb[i].id)

                    # Apply CNOT gates
                    for j in range(0, i):
                        circuit.cx(comb[i - j - 1].id, comb[i - j].id)

            return circuit

    def construct_circuit(self, cnf: CNF, p: int) -> QuantumCircuit:
        """Constructs QAOA circuit to find maximum satisfying assignment.

        Args:
            cnf (CNF): Formula to find maximum satisyfing assignment of.
            p (int): Number of layers to use in QAOA circuit ansatz

        Returns:
            QuantumCircuit: QAOA circuit to optimise parameters across.
        """
        n = cnf.num_vars
        qc = QuantumCircuit(n)

        # Prepare initial state with Hadamard gates
        for qubit in qc.qubits:
            qc.h(qubit)

        # Create alternating mixer and cost gates
        for i in range(p):

            # Cost gates
            gamma = Parameter(f"y_{i}")
            for clause in cnf.clauses:
                qc = self.encode_clause(clause, gamma, qc)

            # Mixer gates
            beta = Parameter(f"β_{i}")
            for qubit in qc.qubits:
                qc.rx(-2 * beta, qubit)

        return qc

    def find_optimal_params(self) -> List[float]:
        """Finds parameters that minimise expectation of cost hamiltonian across all circuit outputs.

        Returns:
            List[float]: Optimial parameters.
        """
        # Construct circuit for each formula
        circuits = [self.construct_circuit(cnf, self.layers) for cnf in self.cnfs]

        def execute_average(param_values: List[float]) -> float:
            # Bind current set of (same) parameters to each circuit 
            bound_circuits = [circuit.bind_parameters(param_values) for circuit in circuits]

            total_succ_prob = 0

            for (cnf, bound_circuit) in zip(self.cnfs, bound_circuits):
                # Calculate success probability exactly
                if self.quantum_instance.options.method == 'statevector':
                    bound_circuit.save_statevector()
                    statevector = self.quantum_instance.run(bound_circuit).result().get_statevector()
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

                total_succ_prob += self.assignment_weighted_average(cnf, rev_output, self.top_avg)

            return total_succ_prob / len(bound_circuits)

        # Minimisation formulation of QAOA
        result = minimize(execute_average, self.init_params, method="COBYLA")

        return result.x

    def sat(self, timeout: int = None) -> Dict[CNF, int]:
        """Finds statisfying assignments of formulas.

        Args:
            timeout (int, optional): Timeout for algorithm per instance if no satisfying assignment found yet. Defaults to None.

        Returns:
            Dict[str, int]: Dict of satisfying assignments and runtimes to find them.
        """

        print("Finding optimal parameters")
        # Find and store optimal parameters
        self.optimal_params = self.find_optimal_params()
        print("Optimal parameters found")

        assignments = {}

        # Construct circuits with optimal parameters
        for i, cnf in enumerate(self.cnfs):
            final_circuit = self.construct_circuit(cnf, self.layers).bind_parameters(
                self.optimal_params
            )
            final_circuit.measure_all()
            print(f'Sampling assignments for formula {i}')

            # Pre-transpile circuit for efficiency
            t_fc = transpile(final_circuit, self.quantum_instance)
            qobj = assemble(t_fc, shots=1)

            # TODO: investigate if this can be done with a callback method
            # Sample until satisfying assignment found or timeout reached
            runtime = 0
            while True:
                if timeout is not None and runtime > timeout:
                    raise TimeoutError("Bitstring sampling timeout")
                runtime += 1
                result = self.quantum_instance.run(qobj, memory=True).result()
                # Extract and reverse bitstring to deal with qiskit ordering
                bs = result.get_memory()[0][::-1]
                if cnf.is_satisfied(bs):
                    break
                if runtime % 10 == 0:
                    print(f'Samples drawn: {runtime}')

            assignments[cnf] = {"ass" : bs, "runtime" : runtime}

        return assignments

    def visualise_result(self, cnf: CNF, plot_num: int = 10, shots: int = 10000) -> Figure:
        """ Visualise output of final optimised circuit.

        Args:
            CNF (CNF): Formula to visualise result for.
            plot_num (int, optional): Number of bitstrings to plot (sorted in descending order of counts). Defaults to 10.
            shots (int, optional): Samples to draw from circuit. Defaults to 10000.

        Raises:
            RuntimeError: Must run solver before visualising results.

        Returns:
            Figure: Histogram of samples drawn.
        """

        if self.optimal_params is None:
            raise RuntimeError("Must run solver before visualising results")

        # Construct circuit with optimal parameters
        final_circuit = self.construct_circuit(cnf, self.layers).bind_parameters(
            self.optimal_params
        )
        final_circuit.measure_all()

        # Measure and reverse bitstrings for qiskit ordering
        counts = {k[::-1] : v for (k, v) in self.quantum_instance.run(final_circuit, shots=shots).result().get_counts().items()}

        return plot_histogram(counts, sort='value_desc', number_to_keep=plot_num) 