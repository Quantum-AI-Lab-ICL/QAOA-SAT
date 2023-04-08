#!/bin/bash

export PATH=/vol/bitbucket/ae719/venv/bin/:$PATH

source activate

hostname; uname -a; cat /etc/lsb-release

python counts.py $1 $2 $3

