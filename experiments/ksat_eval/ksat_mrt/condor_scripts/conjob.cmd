universe = vanilla
executable = mrt.sh
output = uname.out
error = uname.err
requirements = (OpSysVer == 2204)
arguments = 20 4 $(Process) 250 10000
queue 10
