import argparse
import h5py
import os

from formula.cnf import CNF

def main(n, k, i):
	parent_dir = os.path.dirname(os.getcwd())
	dir = f"{parent_dir}/QAOA-SAT/benchmark/instances/n_{n}"
	filename = f"{dir}/f_n{n}_k{k}_{i}"
	cnf = CNF.from_file(f'{filename}.cnf')
	counts = cnf.naive_counts
	with h5py.File(f'{filename}.hdf5', 'w') as file:
		file.create_dataset('counts', data=counts)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('n', help='number of variables')
	parser.add_argument('k', help='variables per clause')
	parser.add_argument('i', help='file index')
	args = parser.parse_args()
	main(args.n, args.k, args.i)