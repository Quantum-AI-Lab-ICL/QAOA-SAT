import argparse
import h5py

from benchmark.generator.ksat_generator import KSATGenerator 
from formula.cnf import CNF

def main(n, k, i):
	generator = KSATGenerator()
	cnf = CNF.from_file(generator.filename(n, k, i))
	counts = cnf.naive_counts
	with h5py.File(generator.filename(n, k, i, 'hdf5'), 'w') as file:
		file.create_dataset('counts', data=counts)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('n', help='number of variables')
	parser.add_argument('k', help='variables per clause')
	parser.add_argument('i', help='file index')
	args = parser.parse_args()
	main(args.n, args.k, args.i)
