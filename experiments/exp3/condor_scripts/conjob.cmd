universe = vanilla
executable = counts_fresh.sh
output = uname.$(n).out
error = uname.$(n).err
requirements = (OpSysVer == 2204)
arguments = $(n) 10 $(Process)
queue 2500
