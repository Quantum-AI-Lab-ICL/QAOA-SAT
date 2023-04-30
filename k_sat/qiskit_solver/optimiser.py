from abc import ABC, abstractmethod
from typing import List, Tuple
from qiskit import QuantumCircuit
from qiskit.utils import QuantumInstance

from formula.formula import Formula


class Optimiser(ABC):
    @abstractmethod
    def __init__(self, quantum_instance: QuantumInstance = None):
        """Abstract optimiser class to be extended.

        Args:
            quantum_instance (QuantumInstace, optional): Backend to run optimiser on. Defaults to Aer qasm simulator.
        """
        pass

    @abstractmethod
    def find_optimal_params(
        self, circuits: List[Tuple[Formula, QuantumCircuit]]
    ) -> List[float]:
        """Find optimal parameters for circuits.

        Args:
            circuits (List[Tuple[Formula, QuantumCircuit]]): Circuits and corresponding formulas to optimise over.

        Returns:
            List[float]: Optimal parameters.
        """
        pass
