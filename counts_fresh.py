import argparse
import h5py
import os

from benchmark.random_k_sat import RandomKSAT

def main(n, k, i):
	cnf = RandomKSAT.from_poisson(n, k, calc_naive=True)
	cnf.to_file(RandomKSAT.filename(n, k, i + 1100))
	with h5py.File(RandomKSAT.filename(n, k, i + 1100, 'hdf5'), 'w') as file:
		file.create_dataset('counts', data=cnf.naive_counts)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('n', help='number of variables', type=int)
	parser.add_argument('k', help='variables per clause', type=int)
	parser.add_argument('i', help='file index', type=int)
	args = parser.parse_args()
	main(args.n, args.k, args.i)
