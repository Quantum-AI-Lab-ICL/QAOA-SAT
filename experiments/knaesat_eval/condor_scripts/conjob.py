import os


for n in range(12, 21):
    for k in range(11, 15):
        cmd = f"condor_submit -a 'n={n}' -a 'k={k}' conjob.cmd --terse"
        os.system(cmd)
