import torch
from torch import Tensor


class PytorchCircuit(torch.nn.Module):
    
	def __init__(self, num_vars: int, layers: int = 1, init_gamma: Tensor = None, init_beta: Tensor = None) -> None:
		"""Pytorch implementation of QAOA circuit for satisfiability solving.

		Args:
			num_vars (int): Number of variables in satisfiability problem.
			layers (int, optional): QAOA circuit layers. Defaults to 1.
			init_gamma (Tensor, optional): Initial cost unitary parameter values. Defaults to all -0.01.
			init_beta (Tensor, optional): Initial mixing unitary parameter values. Defaults to all 0.01.
		"""
		super(PytorchCircuit, self).__init__()

		if init_gamma is None:
			init_gamma = torch.full(size=(layers, ), fill_value=-0.01)
		if init_beta is None:
			init_beta = torch.full(size=(layers, ), fill_value=0.01)

		# optimisable parameters
		gamma = torch.nn.Parameter(init_gamma)
		beta = torch.nn.Parameter(init_beta)
		self.gamma = gamma
		self.beta = beta

		self.layers = layers

		# Initial state equal superposition
		self.n = num_vars
		self.N = 2 ** num_vars
		circuit = torch.full((self.N,), self.N, dtype=torch.cfloat)
		circuit = torch.sqrt(circuit)
		circuit = torch.reciprocal(circuit)
		self.initial = circuit

	def cost(self, circuit: Tensor, gamma: Tensor, h: Tensor) -> Tensor:
		"""Apply cost unitary to state.

		Args:
			circuit (Tensor): State cost unitary is being applied to.
			gamma (Tensor): Parameter parameterising cost unitary.
			h (Tensor): Tensor of unsatisfied clauses per bitstring.

		Returns:
			Tensor: Costed state.
		"""
		hg = torch.complex(torch.tensor(0.), h * gamma)
		hg_exp = torch.exp(hg)
		circuit = hg_exp * circuit
		return circuit

	def mix(self, circuit: Tensor, beta: Tensor) -> Tensor:
		"""Apply mixing unitary to state.

		Args:
			circuit (Tensor): State mixing unitary is being applied to.
			beta (Tensor): Parameter parameterising mixing unitary.

		Returns:
			Tensor: Mixed state.
		"""
		cg = torch.complex(torch.cos(beta), torch.tensor(0.))
		sg = torch.complex(torch.tensor(0.), torch.sin(beta))

		for i in range(self.n):
			cz = cg * circuit

			# swap indices
			circuit = circuit.reshape((2,) * self.n)
			circuit = circuit.transpose(0, i)
			fh, sh = circuit.split(1)
			circuit = torch.cat((sh, fh))
			circuit = circuit.transpose(0, i)
			circuit = circuit.reshape(self.N)

			# reduce for iteration to continue
			circuit = cz + sg * circuit
		
		return circuit

	def succ_prob(self, circuit: Tensor, hS: Tensor) -> Tensor:
		"""Success probability on output state.

		Args:
			circuit (Tensor): Output state.
			hS (Tensor): 1 iff bitstring satisfies problem (in bitstring order).

		Returns:
			Tensor: Success probability.
		"""
		# Find inner product of each state
		ps = (circuit * circuit.conj()).real
		return torch.dot(ps, hS)

	def evolve(self, h: Tensor) -> Tensor:
		"""Apply QAOA unitary to initial state.

		Args:
			h (Tensor): Tensor of unsatisfied clauses per bitstring.

		Returns:
			Tensor: Final state.
		"""

		circuit = self.initial

		# QAOA unitary application
		for i in range(self.layers):
			circuit = self.cost(circuit, self.gamma[i], h)
			circuit = self.mix(circuit, self.beta[i])

		return circuit


	def forward(self, h: Tensor, hS: Tensor) -> Tensor:
		"""Application of QAOA circuit to calculate success probability.

		Args:
			h (Tensor): Tensor of unsatisfied clauses per bitstring.
			hS (Tensor): 1 iff bitstring satisfies problem (in bitstring order).

		Returns:
			Tensor: Success probability of evolved initial state with inputs.
		"""

		# Evolve
		circuit = self.evolve(h)

		# Success probability
		return self.succ_prob(circuit, hS)
		
