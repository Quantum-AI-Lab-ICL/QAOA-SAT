import torch
from torch import Tensor


class PytorchCircuit(torch.nn.Module):
    
	def __init__(self, num_vars: int, layers: int = 1, init_gamma: Tensor = None, init_beta: Tensor = None) -> None:
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
		hg = torch.complex(torch.tensor(0.), h * gamma)
		hg_exp = torch.exp(hg)
		circuit = hg_exp * circuit
		return circuit

	def mix(self, circuit: Tensor, beta: Tensor):
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

	def succ_prob(self, circuit: Tensor, hS: Tensor):
		# Find inner product of each state
		ps = (circuit * circuit.conj()).real
		return torch.dot(ps, hS)

	def evolve(self, h: Tensor) -> Tensor:

		circuit = self.initial

		# QAOA unitary application
		for i in range(self.layers):
			circuit = self.cost(circuit, self.gamma[i], h)
			circuit = self.mix(circuit, self.beta[i])

		return circuit


	def forward(self, h: Tensor, hS: Tensor) -> Tensor:

		# Evolve
		circuit = self.evolve(h)

		# Success probability
		return self.succ_prob(circuit, hS)
		
