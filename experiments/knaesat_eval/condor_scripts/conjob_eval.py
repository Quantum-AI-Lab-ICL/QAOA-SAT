import os

for n in [20]:
    for k in range(3, 11):
        for p in [18, 20, 22, 24, 30]:
            cmd = f"condor_submit -a 'n={n}' -a 'k={k}' -a 'p={p}' conjob_eval.cmd --terse"
            os.system(cmd)

