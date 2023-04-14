import argparse
import h5py

from benchmark.random_problem import RandomProblem
from benchmark.generator.ksat_generator import KSATGenerator

def main(n, k, i):
	generator = KSATGenerator()
	rp = RandomProblem(generator=generator)
	cnf = rp.from_poisson(n, k, satisfiable=True, calc_naive=True).formulas[0]
	cnf.to_file(generator.filename(n, k, i))
	with h5py.File(generator.filename(n, k, i, 'hdf5'), 'w') as file:
		file.create_dataset('counts', data=cnf.naive_counts)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('n', help='number of variables', type=int)
	parser.add_argument('k', help='variables per clause', type=int)
	parser.add_argument('i', help='file index', type=int)
	args = parser.parse_args()
	main(args.n, args.k, args.i)
