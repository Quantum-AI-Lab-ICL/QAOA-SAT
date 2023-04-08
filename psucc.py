import argparse
import h5py
import json
import torch

from benchmark.random_k_sat import RandomKSAT
from k_sat.pytorch_solver.pytorch_circuit import PytorchCircuit

def main(n, k, index, instances):

	# Read in random problems
	formulas = RandomKSAT.from_poisson(n=n, k=k, instances=instances, from_file=index, calc_naive=True, parallelise=True).formulas

	# Read in parameters
	# Params generated for n = 12 regardless of instance size
	dir = RandomKSAT.directory(12, k)
	optimal_params_r = {}
	ps = [1, 2, 4, 8, 16]
	for p in ps:
		with h5py.File(f'{dir}/a_params_{p}.hdf5', 'r') as file:
			gamma = torch.from_numpy(file.get(f'gamma')[:])
			beta = torch.from_numpy(file.get(f'beta')[:])
			optimal_params_r[p] = (gamma, beta)

	for (p, params) in optimal_params_r.items():
		print(f'evaluating p = {p}')

		# Initialise QAOA circuit
		circuit = PytorchCircuit(n, p, params[0], params[1])

		# Evolve each instance and take mean of p_succ
		prob = 0
		for f in formulas:
			h = f.naive_counts
			hS = f.naive_sats
			prob += circuit(h, hS).item()

		# Save to file
		with open(f'p_succ.json', 'r') as f:
			data = json.load(f)
			curr_prob = float(data[str(n)][p])

		data[str(n)][p] = prob + curr_prob

		with open(f'p_succ.json', 'w') as f:
			json.dump(data, f)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('n', help='number of variables', type=int)
	parser.add_argument('k', help='variables per clause', type=int)
	parser.add_argument('index', help='file index', type=int)
	parser.add_argument('instances', help='number of files', type=int)
	args = parser.parse_args()
	main(args.n, args.k, args.index, args.instances)