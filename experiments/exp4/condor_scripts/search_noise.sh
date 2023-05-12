#!/bin/bash

export MACHINE="LAB"

export PATH=/vol/bitbucket/ae719/venv/bin/:$PATH

source activate

python grid_search_noise.py $1 $2

