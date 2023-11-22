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



singularity run "$TMPDIR"/myImages/yolov5.sif 


#singularity run library://haftommh/default/yolov5:latest

singularity run library://haftom12/default/data_transfer:latest "$scratch" "$DESTINATION"