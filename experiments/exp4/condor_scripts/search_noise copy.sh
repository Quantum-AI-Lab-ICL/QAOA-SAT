#!/bin/bash

export MACHINE="LAB"

export PATH=/vol/bitbucket/ae719/venv/bin/:$PATH

source activate

python grid_search.py $1 $2 $3 $4

