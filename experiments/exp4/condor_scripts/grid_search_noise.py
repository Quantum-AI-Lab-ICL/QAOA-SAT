import argparse
import torch
import h5py

from benchmark.cnf.random_cnf import RandomCNF
from k_sat.walkSATlm.wslm_solver import WSlmSolver
from k_sat.walkSATlm.wslm_balance_solver import WSlmBalanceSolver

# Grid search for problems where only hyperparameter is noise
def main(k, p):

    print('Loading instances')

    # Read in random problems
    rp = RandomCNF(type='knaesat')
    formulas = rp.from_poisson(n=12, k=k, instances=100, from_file=0, parallelise=True)

    # Initialise wslm solver with hyperparameters
    wslmm = WSlmSolver(p=p, makes={1:1}, breaks={0:1}) 
    wslmb = WSlmBalanceSolver(p=p)

    # Evaluate running times
    with h5py.File(f'res/rt_m_{k}_{p}.hdf5', 'w') as file:
        times = [wslmm.sat(formula)[1] for formula in formulas]
        file.create_dataset(f'times', data=torch.tensor(times))
    with h5py.File(f'res/rt_b_{k}_{p}.hdf5', 'w') as file:
        times = [wslmb.sat(formula)[1] for formula in formulas]
        file.create_dataset(f'times', data=torch.tensor(times))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('k', help='variables per clause', type=int)
    parser.add_argument('p', help='noise', type=float)
    args = parser.parse_args()
    main(args.k, args.p)
