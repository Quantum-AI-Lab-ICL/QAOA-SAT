from formula.wcnf import WCNF
from itertools import combinations
from functools import reduce
from qiskit import QuantumCircuit, Aer
from qiskit.utils import QuantumInstance
from qiskit.circuit import Parameter
from typing import List, Dict
from qiskit import Aer
from scipy.optimize import minimize
from max_3_sat.solver import Solver
import math


class QuantumSolver(Solver):
    """Quantum solver for Max-3-SAT problems using QAOA."""

    def __init__(
        self, 
        wcnf: WCNF,
        layers: int = 1,
        init_params: List[float] = None,
        quantum_instance: QuantumInstance = None,
        top_avg: float = 1) -> None:
        """Intialise Quantum Solver for maxsat.

        Args:
            wcnf (WCNF): Weighted CNF formula to find maximum satisfiability of.
            layers (int, optional): Number of layers in ansatz. Defaults to 1.
            init_params (List[float], optional): Initial value of parameters for ansatz. Defaults to a list of 1s.
            quantum_instance (QuantumInstace, optional): Backend to run quantum solver on. Defaults to Aer qasm simulator.
            top_avg (float, optional): Proportion of assignments to consider in expectation calculation. Defaults to 1.

        Raises:
            RuntimeError: Invalid 3SAT formula
            RuntimeError: Invalid number of initial parameters
        """
        if any([c.num_vars > 3 for c in wcnf.clauses]):
            raise RuntimeError("Instance of non-3-SAT passed to 3SAT solver")

        if init_params is not None and len(init_params) != 2 * layers:
            raise RuntimeError(
                f"Invalid number of initial parameters supplied, expected {2 * layers}, received {len(init_params)})"
            )

        if init_params is None:
            init_params = [1.0 for _ in range(2 * layers)]

        if quantum_instance is None:
            quantum_instance = Aer.get_backend("qasm_simulator")

        self.wcnf = wcnf
        self.layers = layers
        self.init_params = init_params
        self.quantum_instance = quantum_instance
        self.top_avg = top_avg

    def assignment_weighted_average(
        self, wcnf: WCNF, assignments: Dict[str, float], alpha: float
    ) -> float:
        """Find weighted average of top alpha proportion of assignment weights.

        Args:
                        wcnf (WCNF): Formula assignments are for
                        assignments (Dict[str, float]): Dictionary of assignments and their counts
                        alpha (float): Proportion of assignments to consider

        Returns:
                        float: Weighted average of assignment weights
        """
        assert alpha <= 1 and alpha > 0
        num_assignments = math.ceil(alpha * len(assignments))

        weighted_sum = 0
        total_count = 0
        for (ass, count) in sorted(assignments.items(), key=lambda item: item[1], reverse=True)[:num_assignments]:
            weighted_sum += count * wcnf.assignment_weight(ass)
            total_count += count

        return weighted_sum / total_count

    def cost_gates(
        self, circuit: QuantumCircuit, wcnf: WCNF, gamma: Parameter
    ) -> QuantumCircuit:
        """Appends gates representing cost function to quantum circuit.

        Args:
                        circuit (QuantumCircuit): Quantum circuit to append gates to.
                        wcnf (WCNF): Weighted CNF formula to encode
                        gamma (Parameter): Parameter paramerising cost gates

        Returns:
                        QuantumCircuit: Quantum circuit with appended cost gates.
        """
        for (clause, weight) in wcnf.weighted_clauses:
            # Clause satisfied in any assignment
            if clause.always_sat:
                continue
            elif clause.num_vars == 1:
                # RZ gate
                angle_z = weight * clause.parity() * gamma
                v = clause.get_variable(0)
                circuit.rz(angle_z, v.id)
            elif clause.num_vars == 2:
                # RZ gates
                for v in clause.variables:
                    angle_z = 0.5 * weight * clause.parity([v]) * gamma
                    circuit.rz(angle_z, v.id)

                # RZZ gate
                angle_zz = -0.5 * weight * clause.parity() * gamma
                v1, v2 = clause.get_variable(0), clause.get_variable(1)
                circuit.rzz(angle_zz, v1.id, v2.id)

            else:
                for j, v1 in enumerate(clause.variables):
                    for v2 in clause.variables[j + 1 :]:
                        # RZZ gate
                        angle_zz = -0.25 * weight * clause.parity([v1, v2]) * gamma
                        circuit.rzz(angle_zz, v1.id, v2.id)
                    # RZ gate
                    angle_z = 0.25 * weight * clause.parity([v1]) * gamma
                    circuit.rz(angle_z, v1.id)
                # RZZZ gate
                angle_zzz = 0.25 * weight * clause.parity() * gamma
                circuit.cx(clause.get_variable(0).id, clause.get_variable(1).id)
                circuit.cx(clause.get_variable(1).id, clause.get_variable(2).id)
                circuit.rz(angle_zzz, clause.get_variable(2).id)
                circuit.cx(clause.get_variable(1).id, clause.get_variable(2).id)
                circuit.cx(clause.get_variable(0).id, clause.get_variable(1).id)
            circuit.barrier()
        return circuit

    def circuit(self, wcnf: WCNF, p: int) -> QuantumCircuit:
        """Constructs QAOA circuit to find maximum satisfying assignment.

        Args:
                        wcnf (WCNF): Formula to find maximum satisyfing assignment of.
                        p (int): Number of layers to use in QAOA circuit ansatz

        Returns:
                        QuantumCircuit: QAOA circuit to optimise parameters across.
        """
        n = wcnf.num_vars
        qc = QuantumCircuit(n)

        # Prepare initial state with Hadamard gates
        for qubit in qc.qubits:
            qc.h(qubit)

        # Create alternating mixer and cost gates
        for i in range(p):

            # Cost gates
            gamma = Parameter(f"y_{i}")
            qc = self.cost_gates(qc, wcnf, gamma)

            # Mixer gates
            beta = Parameter(f"β_{i}")
            for qubit in qc.qubits:
                qc.rx(2 * beta, qubit)

        qc.measure_all()
        return qc

    def optimal_params(
        self, wcnf: WCNF, p: int, init_params: List[float]
    ) -> List[float]:
        """Finds parameters that minimise expectation of cost hamiltonian on circuit output.

        Args:
                        wcnf (WCNF): Formula that hamiltonian encodes
                        p (int): Layers in QAOA circuit
                        init_params (List[float]): Initial parameter values

        Returns:
                        List[float]: Optimial parameters
        """
        circuit = self.circuit(wcnf, p)

        def execute_average(param_values: List[float]) -> float:
            bound_circuit = circuit.bind_parameters(param_values)
            counts = self.quantum_instance.run(bound_circuit, shots=1024).result().get_counts()
            # Reverse bitstrings due to qiskit ordering
            rev_counts = {s[::-1] : c for (s, c) in counts.items()}
            # -1 * average because we want to maximise but are using scipy minimise
            return -1 * self.assignment_weighted_average(wcnf, rev_counts, self.top_avg)

        result = minimize(execute_average, init_params, method="COBYLA")

        return result.x

    def max_sat(
        self,
        ret_num: int = None,
    ) -> Dict[str, float]:
        """Finds assigment(s) that corresponds to maximum satisfiability.

        Args:
            ret_num (int): Number of assignments to return (sorted by satisfying weight). Defaults to None, i.e. assignments ordered by weight.

        Returns:
            str: Assigment(s) that corresponds to maximum satisfiability.
        """

        # Find optimal parameters
        optimal_params = self.optimal_params(self.wcnf, self.layers, self.init_params)

        # Construct circuit with optimal parameters and measure
        final_circuit = self.circuit(self.wcnf, self.layers).bind_parameters(optimal_params)
        counts = self.quantum_instance.run(final_circuit, shots=10000).result().get_counts()

        # Order assignments by satisfying weights
        ordered = {}
        ordered_weight = {}
        # Sort and reverse bitstrings to deal with Qiskit qubit ordering
        for (bs, count) in sorted(counts.items(), key=lambda item: item[1], reverse=True):
            rev_string = bs[::-1]
            ordered[rev_string] = count
            ordered_weight[rev_string] = self.wcnf.assignment_weight(rev_string)

        # Store results
        self.circuit_result = ordered
        self.result = ordered_weight

        # If no return number of assignments specified, return all
        if ret_num is None:
            return ordered_weight
        return dict(list(ordered_weight.items())[:ret_num])
