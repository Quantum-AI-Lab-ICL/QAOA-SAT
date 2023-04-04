from qiskit import QuantumCircuit, Aer
from typing import List, Tuple
from qiskit import transpile, assemble

from formula.formula import Formula


class Evaluator:
    """Evaluates QAOA circuit's ability to find a satisfying
    assignment for a problem instance."""

    def __init__(self) -> None:
        """Initialise evaluator."""

    def success_probability(
        self, circuit: QuantumCircuit, formula: Formula, parameters: List[float] = None
    ) -> float:
        """Calculate success probability of circuit.

        Args:
                circuit (QuantumCircuit): Circuit to be evaluated.
                formula (Formula): Formula to evaluate circuit on.
                parameters (List[float], optional): Parameters to bind to circuit. Defaults to None (if already bound).

        Returns:
                float: p_succ as defined in [BM22].
        """
        # Bind parameters if needed
        if parameters is not None:
            circuit = circuit.bind_parameters(parameters)

        # Initialise statevector simulator
        quantum_instance = Aer.get_backend("aer_simulator_statevector")

        # Calculate output
        circuit = circuit.copy()
        circuit.save_statevector()
        statevector = quantum_instance.run(circuit).result().get_statevector()
        circ_output = statevector.probabilities_dict()

        # Reverse bitstrings due to qiskit ordering
        rev_output = {s[::-1]: c for (s, c) in circ_output.items()}
        return sum([v * formula.is_satisfied(k) for (k, v) in rev_output.items()])

    def running_time(
        self,
        circuit: QuantumCircuit,
        formula: Formula,
        parameters: List[float] = None,
        timeout: int = None,
    ) -> Tuple[str, int]:
        """Measure running time of circuit (time until satisfying bitstring sampled).

        Args:
                circuit (QuantumCircuit): Circuit to be evaluated.
                formula (Formula): Formula to evaluate circuit on.
                parameters (List[float], optional): Parameters to bind to circuit. Defaults to None (if already bound).
                timeout (int, optional): Timeout for algorithm if no satisfying assignment found yet. Defaults to None.

        Returns:
                Tuple[str, int]: Tuple of satisfying assignment and runnning time.

        """
        # Bind parameters if needed
        if parameters is not None:
            circuit = circuit.bind_parameters(parameters)

        # Initialise simulator
        quantum_instance = Aer.get_backend("aer_simulator")

        # Pre-transpile circuit for efficiency
        circuit = circuit.copy()
        circuit.measure_all()
        t_fc = transpile(circuit, quantum_instance)
        qobj = assemble(t_fc, shots=1)

        # Timeout flag
        timeout = False

        # Sample until satisfying assignment found or timeout reached
        runtime = 0
        while True:
            if timeout is not None and runtime > timeout:
                timeout = True
                break
            runtime += 1
            result = quantum_instance.run(qobj, memory=True).result()
            # Extract and reverse bitstring to deal with qiskit ordering
            bs = result.get_memory()[0][::-1]
            if formula.is_satisfied(bs):
                break
            if runtime % 10 == 0:
                print(f"Samples drawn: {runtime}")

        # Set bitstring to -1 if timeout
        bs = "-1" if timeout else bs

        return bs, runtime
