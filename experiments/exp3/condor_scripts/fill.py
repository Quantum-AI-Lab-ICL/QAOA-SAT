import argparse
import h5py
from os.path import exists

from benchmark.random_problem import RandomProblem
from benchmark.generator.knaesat_generator import KNAESATGenerator

generator = KNAESATGenerator()
rp = RandomProblem(generator=generator)
k = 10
for n in range(12, 21):
    print(n)
    for i in range(0, 2500):
        fn = generator.filename(n, k, i, 'hdf5')
        if not exists(fn):
            print(fn)
            """
            cnf = rp.from_poisson(n, k, satisfiable=True, calc_naive=True)[0]
            cnf.to_file(generator.filename(n, k, i))
            if len(cnf.naive_counts) != 2 ** n:
                raise RuntimeError("Issue with naive counts")
            with h5py.File(generator.filename(n, k, i, 'hdf5'), 'w') as file:
                file.create_dataset('counts', data=cnf.naive_counts)
            """
