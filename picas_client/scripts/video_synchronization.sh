#!/bin/bash

source_path="surfDcache:/Raw_Data/"
export TESTCASENUMBER=$1

#Create directory in scratch (snellius/spider)
scratch_destination="$TMPDIR"/IMAGEN_TMP

destination_path="surfDcache:/Cleaned_Data/"

echo $TESTCASENUMBER

# Transfer data from dCache Raw_Data Section to the Scratch
singularity run library://haftom12/default/data_transfer:latest "$source_path" "$scratch_destination"

# Run the video synchronization script
singularity run library://haftom12/default/video_synchronization:latest "$scratch_destination/N861D6_ch2_main_20210531190000_20210531200000.mp4" "${TESTCASENUMBER}"

# Transfer data from scratch to the Cleaned_Data Section in dCache
singularity run library://haftom12/default/data_transfer:latest "$scratch_destination" "$destination_path"

#Remove intermediate result
rm -R ~/framestest"${TESTCASENUMBER}"