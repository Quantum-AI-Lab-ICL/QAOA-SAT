import os

for n in range(19, 21):
    for k in range(3, 10):
        for tb in ['m', 'b', 'm2', 'm2b2']:
            cmd = f"condor_submit -a 'n={n}' -a 'k={k}' -a 'tiebreak={tb}' conjob_eval.cmd --terse"
            os.system(cmd)

