#!/bin/bash
#SBATCH --job-name="pilotP"
#SBATCH --nodes=1
#SBATCH --time=00:30:00


cd $PWD

python3 -m venv myenv
source myenv/bin/activate

python3 pilotJobPriority.py