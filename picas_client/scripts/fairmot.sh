#!/bin/bash
#SBATCH --job-name=data_transfer
#SBATCH --nodes=1
#SBATCH --time=00:30:00


#Execute the container
singularity run fairmot.sif