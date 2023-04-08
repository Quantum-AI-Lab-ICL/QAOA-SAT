#!/bin/bash

export PATH=/vol/bitbucket/ae719/venv/bin/:$PATH

source activate

python counts_fresh.py $1 $2 $3

