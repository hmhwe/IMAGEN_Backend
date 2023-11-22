#!/bin/bash
#SBATCH --job-name="pilotJob"
#SBATCH --nodes=1
#SBATCH --time=01:30:00

cd $PWD

# Create and activate a Python virtual environment
python3 -m venv myenv
source myenv/bin/activate


python3 pilotJob.py
