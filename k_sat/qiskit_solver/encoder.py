from abc import ABC, abstractmethod
from qiskit import QuantumCircuit

from formula.formula import Formula


class Encoder(ABC):
    def __init__(self):
        """Abstract encoder class to be extended.

        Raises:
            NotImplementedError: Attempted initialisation of abstract base encoder class.
        """
        pass

    @abstractmethod
    def encode_formula(self, formula: Formula, p: int = 1) -> QuantumCircuit:
        """Encode formula into quantum circuit.

        Args:
            formula (Formula): Boolean formula to be encoded.
            p (int, optional): Number of repeated layers in circuit. Defaults to 1.

        Returns:
            QuantumCircuit: Circuit encoding formula.
        """
        pass

