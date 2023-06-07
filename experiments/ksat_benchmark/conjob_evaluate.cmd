universe = vanilla
executable = evaluate.sh
output = uname.out
error = uname.err
requirements = (OpSysVer == 2204)
arguments = $(n) $(k) $(Process) 250 25
queue 10
