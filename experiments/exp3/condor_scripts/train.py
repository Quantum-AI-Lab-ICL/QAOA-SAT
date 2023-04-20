import os
import argparse
import h5py
import torch

from k_sat.pytorch_solver.pytorch_circuit import PytorchCircuit
from k_sat.pytorch_solver.pytorch_optimiser import PytorchOptimiser
from benchmark.random_problem import RandomProblem
from benchmark.generator.knaesat_generator import KNAESATGenerator

def main(n, k, p):
	generator = KNAESATGenerator()
	rp = RandomProblem(generator=generator)
	# 100 training instances
	formulas = rp.from_poisson(n, k, satisfiable=True, instances = 100, from_file = 0, calc_naive=True, parallelise=True)

	circuit = PytorchCircuit(num_vars=n, layers=p)
	adam = torch.optim.Adam(circuit.parameters(), lr=0.1, maximize=True)
	epochs = 100
	optimiser = PytorchOptimiser(circuit, adam, epochs=epochs)
	optimiser.find_optimal_params(formulas)

	# Save to file
	dir = generator.directory(n, k)
	with h5py.File(f'{dir}/a_params_{p}.hdf5', 'w') as file:
		file.create_dataset(f'gamma', data=circuit.gamma.detach().clone())
		file.create_dataset(f'beta', data=circuit.beta.detach().clone())

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('n', help='number of variables', type=int)
	parser.add_argument('k', help='variables per clause', type=int)
	parser.add_argument('p', help='number of layers', type=int)
	args = parser.parse_args()
	main(args.n, args.k, args.p)
