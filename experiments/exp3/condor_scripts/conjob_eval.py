import os

for n in range(19, 21):
    for k in range(3, 10):
        cmd = f"condor_submit -a 'n={n}' -a 'k={k}' conjob_eval.cmd --terse"
        os.system(cmd)

