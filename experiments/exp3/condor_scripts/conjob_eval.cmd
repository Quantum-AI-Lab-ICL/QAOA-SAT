universe = vanilla
executable = evaluate.sh
output = uname.out
error = uname.err
requirements = (OpSysVer == 2204)
arguments = $(n) $(k) $(Process) 50 10000 $(p)
queue 50
