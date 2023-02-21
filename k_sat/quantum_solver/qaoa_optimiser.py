from abc import ABC, abstractmethod
from typing import List, Tuple
from qiskit import QuantumCircuit
from qiskit.utils import QuantumInstance

from formula.formula import Formula


class QAOAOptimiser(ABC):

    def __init__(self, quantum_instance: QuantumInstance = None):
        """Abstract optimiser class to be extended.

        Args:
            quantum_instance (QuantumInstace, optional): Backend to run optimiser on. Defaults to Aer qasm simulator.

        Raises:
            NotImplementedError: Attempted initialisation of abstract base optimiser class.
        """

        raise NotImplementedError(
            "Attempted initialisation of abstract base optimiser class"
        )

    @abstractmethod
    def find_optimal_params(self, circuits: List[Tuple[Formula, QuantumCircuit]]) -> List[float]:
        """Encode formula into quantum circuit.

        Args:
            circuits (List[Tuple[Formula, QuantumCircuit]]): Circuits and corresponding formulas to optimise over. 


        Raises:
            NotImplementedError: Attempted invocation of abstract base optimiser class method.

        """
        raise NotImplementedError(
            "Attempted invocation of abstract base optimiser class method"
        )