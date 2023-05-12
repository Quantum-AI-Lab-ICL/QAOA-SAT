import os

for k in range(3, 11):
    for p in [i / 20 for i in range(21)]:
            cmd = f"condor_submit -a 'k={k}' -a 'p={p}' conjob_search_noise.cmd --terse"
            os.system(cmd)

