import argparse
import h5py
import os

from benchmark.random_k_sat import RandomKSAT

def main(n, k, i):
	parent_dir = os.path.dirname(os.getcwd())
	dir = f"{parent_dir}/QAOA-SAT/benchmark/instances/n_{n}"
	filename = f"{dir}/f_n{n}_k{k}_{i + 1100}"
	cnf = RandomKSAT.from_poisson(n, k, calc_naive=True).formulas[0]
	cnf.to_file(f'{filename}.cnf')
	with h5py.File(f'{filename}.hdf5', 'w') as file:
		file.create_dataset('counts', data=cnf.naive_counts)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('n', help='number of variables', type=int)
	parser.add_argument('k', help='variables per clause', type=int)
	parser.add_argument('i', help='file index', type=int)
	args = parser.parse_args()
	main(args.n, args.k, args.i)
