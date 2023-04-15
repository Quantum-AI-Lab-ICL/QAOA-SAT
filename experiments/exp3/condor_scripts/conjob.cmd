universe = vanilla
executable = counts_fresh.sh
output = uname.out
error = uname.err
requirements = (OpSysVer == 2204)
arguments = $(n) 10 $(Process)
queue 2500 n from seq 17 20|
