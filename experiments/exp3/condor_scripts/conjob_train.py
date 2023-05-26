import os

for k in range(3, 11):
    for p in [30, 60]:
        cmd = f"condor_submit -a 'n={12}' -a 'k={k}' -a 'p={p}' conjob_train.cmd --terse"
        os.system(cmd)

