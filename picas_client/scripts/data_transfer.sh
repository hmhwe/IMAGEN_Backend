#!/bin/bash
#SBATCH --job-name=data_transfer
#SBATCH --nodes=1
#SBATCH --time=00:30:00

source_path="surfDcache:/rawD/"
destination_path="surfDcache:/cleanD/"


#Execute the container
singularity run data_transfer.sif "$source_path" "$destination_path"