#!/bin/bash

#SBATCH --job-name="Video_Synchronization"
#SBATCH --nodes=1
#SBATCH --time=00:30:00


source_path="surfDcache:/rawD/"
TESTCASENUMBER=12


#Create directory in scratch (snellius/spider)
scratch_folder="video_synchronization"
scratch_destination="/scratch/$scratch_folder"
mkdir -p "$scratch_destination"

destination_path="surfDcache:/cleanD/"



echo $TESTCASENUMBER


# Run data transfer and synchronization images
singularity run library://haftom12/default/data_transfer:latest "$source_path" "$scratch_destination"

singularity run library://haftom12/default/video_synchronization:latest "$scratch_destination/N861D6_ch2_main_20210531190000_20210531200000.mp4" "${TESTCASENUMBER}"

singularity run library://haftom12/default/data_transfer:latest "$scratch_destination" "$destination_path"

#Remove intermediate result
rm -R ~/framestest"${TESTCASENUMBER}"