universe = vanilla
executable = train.sh
output = uname.$(k).out
error = uname.$(k).err
requirements = (OpSysVer == 2204)
arguments = 12 $(k) 16
queue k from seq 3 10|
