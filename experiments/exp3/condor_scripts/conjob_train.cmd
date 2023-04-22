universe = vanilla
executable = train.sh
output = uname.$(k).$(p).out
error = uname.$(k).$(p).err
requirements = (OpSysVer == 2204)
arguments = $(n) $(k) $(p)
queue
