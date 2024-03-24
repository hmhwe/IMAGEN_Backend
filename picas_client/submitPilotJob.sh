#!/bin/bash
#SBATCH --job-name="pilotJob"
#SBATCH --nodes=1
#SBATCH --time=01:30:00

cd $PWD

python3 Job1.py

