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


#Directory in scratch
scratch="$TMPDIR"/train_result

#Training results in dCache
DESTINATION="surfDcache:/yolo_train_result/" 


#From local
#singularity run ./definition_files/yolov5.sif 

#From sylab repo
singularity run library://haftommh/default/yolov5:latest


singularity run library://haftommh/default/data_transfer:latest "$scratch" "$DESTINATION"