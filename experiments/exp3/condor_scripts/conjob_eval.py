import os

n_values = [i for i in range(12, 21)]

for n in n_values:
    cmd = f"condor_submit -a 'n={n}' -a 'k={3}' conjob_eval.cmd --terse"
    os.system(cmd)

