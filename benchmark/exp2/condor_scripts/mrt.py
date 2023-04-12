import argparse
import os
import h5py
import torch
import pathos
from torch.distributions.categorical import Categorical
from functools import partial

from benchmark.random_k_sat import RandomKSAT
from k_sat.pytorch_solver.pytorch_circuit import PytorchCircuit

def main(n, k, index, instances, timeout):

    timeout = timeout * n
    
    # Consider batch size
    index = index * instances

    print('Loading instances')

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

        def rt(formula, pc):
            # Emulate sampling
            counts = formula.naive_counts
            final_state = pc.evolve(counts)
            ps = (final_state * final_state.conj()).real
            m = Categorical(ps)

            # Timeout flag
            tf = False

            # Sample until satisfying assignment found or timeout reached
            runtime = 0
            while True:
                if runtime > timeout:
                    tf = True
                    break
                runtime += 1
                # Sample and check if satisfies
                sample = m.sample()
                if counts[sample] == 0:
                    break

            if tf:
                print('TIMEOUT')

            print(runtime)
            return runtime

        times = torch.tensor([rt(f, circuit) for f in formulas])
        #with pathos.multiprocessing.Pool(os.cpu_count() - 1) as executor:
        #    times = torch.tensor(executor.map(partial(rt, pc=circuit), formulas))

        # Save to file
        with h5py.File(f'res/rt_{n}_{k}_{p}_{index}.hdf5', 'w') as file:
            file.create_dataset(f'times', data=times)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('n', help='number of variables', type=int)
    parser.add_argument('k', help='variables per clause', type=int)
    parser.add_argument('index', help='file index', type=int)
    parser.add_argument('instances', help='number of files', type=int)
    parser.add_argument('timeout', help='timeout for sampling', type=int)
    args = parser.parse_args()
    main(args.n, args.k, args.index, args.instances, args.timeout)
