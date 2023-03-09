import numpy as np

from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from itertools import combinations

from formula.formula import Formula
from formula.clause import Clause
from k_sat.quantum_solver.qaoa_encoder import QAOAEncoder


class PauliEncoder(QAOAEncoder):
    """Encoder of Boolean formula into Quantum circuit."""

    def __init__(self) -> None:
        """Initialise Pauli encoder"""

    def encode_clause(
        self, clause: Clause, gamma: Parameter, circuit: QuantumCircuit
    ) -> QuantumCircuit:
        """Append unitary gates encoding clause to provided quantum circuit.

        Args:
                clause (Clause): Clause to be encoded.
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

    def encode_formula(self, formula: Formula, p: int = 1) -> QuantumCircuit:
        """Encodes formula into circuit using (decomposed) Z-Pauli gates.

        Args:
                        formula (Formula): Boolean formula to be encoded.
                        p (int, optional): Number of repeated layers in circuit. Defaults to 1.

                Returns:
                        QuantumCircuit: Circuit encoding formula.
        """
        n = formula.num_vars
        qc = QuantumCircuit(n)

        # Prepare initial state with Hadamard gates
        for qubit in qc.qubits:
            qc.h(qubit)

        # Create alternating mixer and cost gates
        for i in range(p):

            # TODO: optimise to not re-encode clause each time for p > 1
            # Cost gates
            gamma = Parameter(f"y_{i}")
            for clause in formula.clauses:
                qc = self.encode_clause(clause, gamma, qc)

            # Mixer gates
            beta = Parameter(f"β_{i}")
            for qubit in qc.qubits:
                qc.rx(-2 * beta, qubit)

        return qc
