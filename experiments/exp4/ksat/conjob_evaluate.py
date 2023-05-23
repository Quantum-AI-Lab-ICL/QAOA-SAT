import os

for n in range(12, 21):
    for k in [4, 8]:
        cmd = f"condor_submit -a 'n={n}' -a 'k={k}' conjob_evaluate.cmd --terse"
        os.system(cmd)

