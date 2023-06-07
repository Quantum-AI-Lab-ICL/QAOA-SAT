#!/bin/bash

export PATH=/vol/bitbucket/ae719/venv/bin/:$PATH

source activate

export MACHINE="LAB"

python evaluate.py $1 $2 $3 $4 $5 $6
