import os

for k in range(3, 11):
    for p in [i / 20 for i in range(21)]:
        for (w1, w2) in [(i/10, 1 - (i/10)) for i in range(11)]:
            cmd = f"condor_submit -a 'k={k}' -a 'p={p}' -a 'w1={w1}' -a 'w2={w2}' conjob_search.cmd --terse"
            os.system(cmd)

