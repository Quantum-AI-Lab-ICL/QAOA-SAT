universe = vanilla
executable = counts_fresh.sh
output = uname.out
error = uname.err
requirements = (OpSysVer == 2204)
arguments = $(n) $(k) $(Process)
queue 2500
