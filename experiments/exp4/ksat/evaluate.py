import argparse
import h5py
import torch

from benchmark.cnf.generator.knaesat_generator import KSATGenerator
from benchmark.cnf.random_cnf import RandomCNF
from k_sat.walkSATlm.wslm_solver import WSlmSolver

def main(n, k, index, instances, timeout):

    timeout = timeout * n
    
    # Consider batch size
    index = index * instances

    print('Loading instances')

    # Read in random problems
    generator = KSATGenerator()
    rp = RandomCNF(generator=generator)
    formulas = rp.from_poisson(n=n, k=k, instances=instances, from_file=index, calc_naive=True, parallelise=True)

    # Initialise solver with hyperparameters
    wslm = WSlmSolver(p=0.15, makes={1:5, 2:6}) 

    print('Evaluating formulas')

    # Calculate and store results
    results = [wslm.sat(f, timeout=timeout)[1] for f in formulas]
    with h5py.File(f'res/rt_{n}_{k}_{index}.hdf5', 'w') as file:
        file.create_dataset(f'times', data=torch.tensor(results))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('n', help='number of variables', type=int)
    parser.add_argument('k', help='variables per clause', type=int)
    parser.add_argument('index', help='file index', type=int)
    parser.add_argument('instances', help='number of files', type=int)
    parser.add_argument('timeout', help='timeout for sampling', type=int)
    args = parser.parse_args()
    main(args.n, args.k, args.index, args.instances, args.timeout)
