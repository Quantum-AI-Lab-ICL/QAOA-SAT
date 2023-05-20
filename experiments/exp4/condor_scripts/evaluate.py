import argparse
import pandas as pd
import h5py
import torch

from benchmark.cnf.generator.knaesat_generator import KNAESATGenerator
from benchmark.cnf.random_cnf import RandomCNF
from k_sat.walkSATlm.wslm_solver import WSlmSolver
from k_sat.walkSATlm.wslm_balance_solver import WSlmBalanceSolver

def main(n, k, index, instances, timeout, tiebreak):

    timeout = timeout * n
    
    # Consider batch size
    index = index * instances

    print('Loading instances')

    # Read in random problems
    generator = KNAESATGenerator()
    rp = RandomCNF(generator=generator)
    formulas = rp.from_poisson(n=n, k=k, instances=instances, from_file=index, calc_naive=True, parallelise=True)

    print('Reading in parameters')
    # Read in parameters
    # Params generated for n = 12 regardless of instance size
    # Hardcode k=3 because all k in same dataframe
    dir = generator.directory(12, 3)
    params = pd.read_pickle(f'{dir}/params')
    params = params[(params.k == k) & (params.tiebreak == tiebreak)] 

    def eval(f):

        # Randomly choose params
        pr = params.sample()
        p = pr.p

        # Initialise solver with hyperparameters
        if tiebreak == 'm':
            wslm = WSlmSolver(p=p, makes={1:1}, breaks={0:1}) 
        elif tiebreak == 'b':
            wslm = WSlmBalanceSolver(p=p)
        else:
            w1 = float(pr.w1)
            w2 = float(pr.w2)
            if tiebreak == 'm2':
                wslm = WSlmSolver(p=p, makes={1:w1, 2:w2}, breaks={0:w1}) 
            elif tiebreak == 'm2b2':
                wslm = WSlmSolver(p=p, makes={1:w1, 2:w2}, breaks={0:w1, -1:w2}) 
            else:
                raise RuntimeError('Invalid tiebreak')

        # Evaluate
        _, rt = wslm.sat(f, timeout=timeout)
        return rt

    print('Evaluating formulas')

    # Calculate and store results
    results = [eval(f) for f in formulas]
    with h5py.File(f'res/rt_{n}_{k}_{tiebreak}_{index}.hdf5', 'w') as file:
        file.create_dataset(f'times', data=torch.tensor(results))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('n', help='number of variables', type=int)
    parser.add_argument('k', help='variables per clause', type=int)
    parser.add_argument('index', help='file index', type=int)
    parser.add_argument('instances', help='number of files', type=int)
    parser.add_argument('timeout', help='timeout for sampling', type=int)
    parser.add_argument('tiebreak', help='tiebreak method', type=str)
    args = parser.parse_args()
    main(args.n, args.k, args.index, args.instances, args.timeout, args.tiebreak)