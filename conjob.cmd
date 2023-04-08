universe = vanilla
executable = counts.sh
output = uname.out
error = uname.err
requirements = (OpSysVer == 2204)
arguments = 20 8 $(Process)
queue 1100
