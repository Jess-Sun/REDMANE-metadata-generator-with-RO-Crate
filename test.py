import os
import json
from pathlib import Path
from params import * 

with open("config.json", "r") as f:
    config = json.load(f)
with open("sample_metadata\sample_to_patient.json", "r") as f:
    mapping = json.load(f)

def filter_files(directory):
    """   
    Recursively scans the given directory for raw data files whose names end with one of the specified file_types.
    Each found file has the fullpath appended to the relevant list.
    
    Args:
        directory (str): The directory to search.
        raw (list): List of raw file extensions to match.
        processed (list): List of raw file extensions to match.
        summarised (list): List of raw file extensions to match.
    
    Returns:
        tuple: A tuple of lists containing the full paths for raw, processed and summarised files respectively.
    """    
    bucket_by_ext = {}

    for ext in config["raw_file_types"]:
        bucket_by_ext[ext.lower()] = "raw"

    for ext in config["processed_file_types"]:
        bucket_by_ext[ext.lower()] = "processed"

    for ext in config["summarised_file_types"]:
        bucket_by_ext[ext.lower()] = "summarised"

    file_dict = {
        bucket.replace("_file_types", ""): []
        for bucket in config
    }

    # file_dict = {"raw":[], "processed":[], "summarised":[]}

    for root, _, files in os.walk(directory):
        for file in files:
            ext = Path(file).suffix.lower()
            bucket = bucket_by_ext.get(ext)

            if bucket is None:
                continue
            full_path = Path(root) / file
            file_dict[bucket].append(full_path)

    for bucket, files in file_dict.items():
        if not files:
            print(f" | No files found for {bucket} file types")
         
    return file_dict

def process_files(directory, file_dict, file_type, organization, cor_dict):
    print(f"Processing the {file_type} files")
    file_list = []
    total_size = 0
    for full_path in file_dict[file_type]:

        relative_path = full_path.relative_to(directory)
        file_path = f"./{relative_path.as_posix()}"
        file_size = round(os.path.getsize(full_path) / CONVERT_FROM_BYTES)
        total_size += file_size
        file_name = Path(full_path).name
        sample_name = Path(full_path).stem

        # establish file name
        metadata_dict = {
            "file_name": file_name,
            "file_size": file_size, 
            "patient_id": cor_dict.get(sample_name, ""),
            "sample_id": sample_name,
            "directory": file_path,
            "organization": organization
        }

        print(f" | {file_path}  ~{file_size}{FILE_SIZE_UNIT}")

        # check here to prevent duplicates
        if metadata_dict not in file_list:
            file_list.append(metadata_dict)

    print(f" | Total size for these files: {total_size}{FILE_SIZE_UNIT}")
                        
    print(file_list)

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python update_local.py /path/to/files")
        sys.exit(1)
    
    # The target directory should be the 'files' subfolder.
    target_directory = sys.argv[1]
    print(f"\nSearching through {target_directory} .........")
    
    
    try:
        file_dict = filter_files(target_directory)
        process_files(target_directory, file_dict, "raw", ORGANIZATION, mapping)

    except Exception as e:
        print(f"Error: {e}")