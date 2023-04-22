import os

for k in range(3, 11):
    for p in [1, 2, 4, 8, 16]:
        cmd = f"condor_submit -a 'n={12}' -a 'k={k}' -a 'p={p}' conjob_train.cmd --terse"
        os.system(cmd)

