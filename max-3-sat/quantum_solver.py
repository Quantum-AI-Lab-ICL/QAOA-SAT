from formula.wcnf import WCNF
from itertools import combinations
from functools import reduce
from qiskit import QuantumCircuit, Aer
from qiskit.utils import QuantumInstance
from qiskit.circuit import Parameter
from typing import List, Dict
from qiskit import Aer
from scipy.optimize import minimize


class QuantumSolver:
	"""Quantum solver for Max-3-SAT problems using QAOA."""
	def __init__(self) -> None:
		"""Initialise Quantum solver. """
		pass

	def assignment_weighted_average(self, wcnf: WCNF, assignments: Dict[str, float]) -> float:
		"""Find weighted average of assignment weights.

		Args:
			wcnf (WCNF): Formula assignments are for
			assignments (Dict[str, float]): Dictionary of assignments and their counts

		Returns:
			float: Weighted average of assignment weights
		"""
		weighted_sum = sum([count * wcnf.assignment_weight(ass) for (ass, count) in assignments.items()])
		return weighted_sum / sum(assignments.keys())

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
			for j, v1 in enumerate(clause.variables):
				for v2 in clause.variables[j + 1:]:
					# RZZ gate
					angle_zz = 0.25 * weight * clause.parity([v1, v2]) * gamma
					circuit.rzz(angle_zz, v1.id, v2.id)
				# RZ gate
				angle_z = -0.25 * clause.weight * clause.parity([v1]) * gamma
				circuit.rz(angle_z, v1.id)
			# RZZZ gate
			angle_zzz = -0.25 * weight * clause.parity() * gamma
			circuit.cx(clause.get_variable(0).id, clause.get_variable(1).id)
			circuit.cx(clause.get_variable(1).id, clause.get_variable(2).id)
			circuit.rz(angle_zzz, clause.get_variable(2).id)
			circuit.cx(clause.get_variable(1).id, clause.get_variable(2).id)
			circuit.cx(clause.get_variable(0).id, clause.get_variable(1).id)
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

	def optimal_params(self, wcnf: WCNF, p: int, init_params: List[float]) -> List[float]:
		""" Finds parameters that minimise expectation of cost hamiltonian on circuit output.

		Args:
			wcnf (WCNF): Formula that hamiltonian encodes
			p (int): Layers in QAOA circuit
			init_params (List[float]): Initial parameter values

		Returns:
			List[float]: Optimial parameters
		"""
		circuit = self.circuit(wcnf, p)
		backend = Aer.get_backend('qasm_simulator')

		def execute_average(param_values: List[float]) -> float:
			bound_circuit = circuit.bind_parameters(param_values)
			counts = backend.run(bound_circuit).result().get_counts()
			# -1 * average because we want to maximise but are using scipy minimise
			return -1 * self.assignment_weighted_average(wcnf, counts)

		result = minimize(execute_average, init_params, method='COBYLA')

		print(result)

		return result.x

	def max_sat(self, wcnf: WCNF, layers: int = 1, init_params: List[float] = None, quantum_instance: QuantumInstance = None, ret_num: int = None) -> List[str]:
		""" Finds assigment(s) that corresponds to maximum satisfiability.

		Args:
			wcnf (WCNF): Weighted CNF formula to find maximum satisfiability of.
			layers (int, optional): Number of layers in ansatz. Defaults to 1.
			init_params (List[float], optional): Initial value of parameters for ansatz. Defaults to None.
			ret_num (int): Number of assignments to return (sorted by satisfying weight). 
						   Defaults to None, i.e. assignments ordered by weight.

		Raises:
			RuntimeError: Invalid 3SAT formula
			RuntimeError: Invalid number of initial parameters

		Returns:
			str: Assigment(s) that corresponds to maximum satisfiability.
		"""

		if any([lambda c: c.num_vars != 3]):
			raise RuntimeError("Instance of non-3-SAT passed to 3SAT solver")

		if init_params is not None and len(init_params) != 2 * layers:
			raise RuntimeError(f'Invalid number of initial parameters supplied, expected {2 * layers}, received {len(init_params)})')

		optimal_params = self.optimal_params(wcnf, layers, init_params)

		final_circuit = self.circuit(wcnf, layers).bind_parameters(optimal_params)

		if quantum_instance is None:
			quantum_instance = Aer.get_backend('qasm_simulator')

		counts = quantum_instance.run(final_circuit).result().get_counts()
		counts = dict(sorted(counts.items(), key=lambda item: item[1]))
		
		if ret_num is None:
			return counts.keys()

		return counts.keys()[:ret_num]