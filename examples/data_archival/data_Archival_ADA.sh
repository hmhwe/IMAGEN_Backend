#!/bin/bash
#SBATCH --nodes=1
#SBATCH --time=04:00:00
#SBATCH --output=ada.log

# Define variables
MACAROON_TOKEN_FILE="$1"
ADA_COMMAND="--whoami"


# Run the Singularity container 
singularity run data_archival_ADA.sif  "$MACAROON_TOKEN_FILE"  "$ADA_COMMAND"
