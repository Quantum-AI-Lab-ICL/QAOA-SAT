import os

for n in range(12, 21):
    for k in range(3, 11):
        for tb in ['m', 'b', 'm2', 'm2b2']:
            cmd = f"condor_submit -a 'n={n}' -a 'k={k}' -a 'tiebreak={tb}' conjob_evaluate.cmd --terse"
            os.system(cmd)

