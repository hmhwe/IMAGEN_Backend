import os
import sys
from rclone_python import rclone
from rclone_python.remote_types import RemoteTypes

def transfer_data_source_to_destination(source_path, destination_path):
    print("Starting data transfer from source to destination")

    
    rclone.copy(source_path, destination_path)
    
    print("Data transfer completed successfully")
    
    

if __name__ == "__main__":
    if len(sys.argv) !=3:
        print("Usage: python data_transfer.py <source_path> <destination_path>")
        sys.exit(1)
    
    source_path = sys.argv[1]
    destination_path = sys.argv[2]
    
    print(source_path, destination_path)
    
    transfer_data_source_to_destination(source_path, destination_path)