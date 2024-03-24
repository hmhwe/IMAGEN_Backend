#!/bin/bash

# Obtain job arguments
export WEIGHTS=$1
export IMG=$2
export EPOCHS=$3
export BATCH_SIZE=$4

echo "WEIGHTS: $WEIGHTS"
echo "IMG: $IMG"
echo "EPOCHS: $EPOCHS"
echo "BATCH_SIZE: $BATCH_SIZE"

#Raw_Data in dCache
SOURCE="surfDcache:/Raw_Data/" 

#Directory in scratch
scratch="$TMPDIR"/IMAGEN_TMP

#Training results in dCache
DESTINATION="surfDcache:/Training_Result_Data/" 

#From sylab repo
singularity run library://haftommh/default/yolov5:latest

singularity run library://haftommh/default/data_transfer:latest "$scratch" "$DESTINATION"