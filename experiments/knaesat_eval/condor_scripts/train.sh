#!/bin/bash

export MACHINE="LAB"

export PATH=/vol/bitbucket/ae719/venv/bin/:$PATH

source activate

python train.py $1 $2 $3

