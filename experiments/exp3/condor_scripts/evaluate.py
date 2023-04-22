import argparse
import json
import h5py
import torch
from torch.distributions.categorical import Categorical

from benchmark.generator.knaesat_generator import KNAESATGenerator
from benchmark.random_problem import RandomProblem
from k_sat.pytorch_solver.pytorch_circuit import PytorchCircuit

def main(n, k, index, instances, timeout):

    timeout = timeout * n
    
    # Consider batch size
    index = index * instances

    print('Loading instances')

    # Read in random problems
    generator = KNAESATGenerator()
    rp = RandomProblem(generator=generator)
    formulas = rp.from_poisson(n=n, k=k, instances=instances, from_file=index, calc_naive=True, parallelise=True)

    print('Reading in parameters')
    # Read in parameters
    # Params generated for n = 12 regardless of instance size
    dir = generator.directory(12, k)
    optimal_params_r = {}
    ps = [1, 2, 4, 8, 16]
    for p in ps:
        with h5py.File(f'{dir}/a_params_{p}.hdf5', 'r') as file:
            gamma = torch.from_numpy(file.get(f'gamma')[:])
            beta = torch.from_numpy(file.get(f'beta')[:])
            optimal_params_r[p] = (gamma, beta)

    p_succ = {}
    p_succ[n] = {}

    for (p, params) in optimal_params_r.items():
        print(f'evaluating p = {p}')

        # Initialise QAOA circuit
        circuit = PytorchCircuit(n, p, params[0], params[1])

        # Evolve each instance, take mean of p_succ and store run times
        def eval(formula):

            h = torch.from_numpy(formula.naive_counts)
            hS = torch.from_numpy(formula.naive_sats)
            
            # Evolve
            final_state = circuit.evolve(h).detach().clone()

            # p_succ
            prob = circuit.succ_prob(final_state, hS).item()

            # Emulate sampling
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
                if h[sample] == 0:
                    break

            if tf:
                print('TIMEOUT')

            return runtime, prob 

        print('Evaluating formulas')

        # Calculate and store results
        results = [eval(f) for f in formulas]
        times, prob = zip(*results)
        with h5py.File(f'res/rt_{n}_{k}_{p}_{index}.hdf5', 'w') as file:
            file.create_dataset(f'times', data=torch.tensor(times))
        p_succ[n][p] = sum(prob)

    # Save psucc to file
    with open(f'res/p_succ_{n}_{k}_{index}.json', 'w') as f:
        json.dump(p_succ, f)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('n', help='number of variables', type=int)
    parser.add_argument('k', help='variables per clause', type=int)
    parser.add_argument('index', help='file index', type=int)
    parser.add_argument('instances', help='number of files', type=int)
    parser.add_argument('timeout', help='timeout for sampling', type=int)
    args = parser.parse_args()
    main(args.n, args.k, args.index, args.instances, args.timeout)
