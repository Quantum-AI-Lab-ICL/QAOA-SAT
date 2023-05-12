import argparse
import torch
import h5py

from benchmark.cnf.random_cnf import RandomCNF
from k_sat.walkSATlm.wslm_solver import WSlmSolver

def main(k, p, w1, w2):

    print('Loading instances')

    # Read in random problems
    rp = RandomCNF(type='knaesat')
    formulas = rp.from_poisson(n=12, k=k, instances=100, from_file=0, parallelise=True)

    # Initialise wslm solver with hyperparameters
    wslmm = WSlmSolver(p=p, makes={1:w1, 2:w2}, breaks={0:w1}) 
    wslmb = WSlmSolver(p=p, makes={1:w1, 2:w2}, breaks={0:w1, -1:w2}) 

    # Evaluate running times
    with h5py.File(f'res/rt_m2_{k}_{p}.hdf5', 'w') as file:
        times = [wslmm.sat(formula)[1] for formula in formulas]
        file.create_dataset(f'times', data=torch.tensor(times))
    with h5py.File(f'res/rt_m2b2_{k}_{p}.hdf5', 'w') as file:
        times = [wslmb.sat(formula)[1] for formula in formulas]
        file.create_dataset(f'times', data=torch.tensor(times))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('k', help='variables per clause', type=int)
    parser.add_argument('p', help='noise', type=float)
    parser.add_argument('w1', help='weight 1', type=float)
    parser.add_argument('w2', help='weight 2', type=float)
    args = parser.parse_args()
    main(args.k, args.p)
