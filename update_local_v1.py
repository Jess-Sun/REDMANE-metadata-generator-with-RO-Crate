#!/usr/bin/env python3
import os
import json
from pathlib import Path
from generate_html import generate_html_from_json
from auxiliary import process_files_for_summarised
import pandas as pd
import numpy as np



def load_json(file_path):
    """
    Loads the JSON file including the pairs of samples and corresponding patients and return a dictionary.
    The keys are sample_id and values are patient_id in this dictionary.

    Args:
        file_path (str): Path to the metadata JSON file.

    Returns:
        dict: Mapping from "Patient ID" to the metadata entry.
    """
    with open(file_path, "r") as f:
        data = json.load(f)
    return data


def find_files_via_extensions(directory, config):
    """   
    Recursively scans the given directory for raw data files whose names end with one of the specified file_types.
    Each found file has the fullpath appended to the relevant list.
    
    Args:
        directory (str): The directory to search.
        raw (list): List of raw file extensions to match.
    
    Returns:
        dictionary: A dictionary of lists containing the full paths for raw, processed and summarised files respectively.
    """    
    bucket_by_ext = {}

    for ext in config["raw_file_extensions"]:
        bucket_by_ext[ext.lower()] = "raw"

    for ext in config["processed_file_extensions"]:
        bucket_by_ext[ext.lower()] = "processed"

    for ext in config["summarised_file_extensions"]:
        bucket_by_ext[ext.lower()] = "summarised"

    file_path_dict = {
        bucket.replace("_file_extensions", ""): []
        for bucket in config
    }

    # file_path_dict = {"raw":[], "processed":[], "summarised":[]}

    for root, _, files in os.walk(directory):
        for file in files:
            ext = Path(file).suffix.lower()
            bucket = bucket_by_ext.get(ext)

            if bucket is None:
                continue
            full_path = Path(root) / file
            file_path_dict[bucket].append(full_path)

    for bucket, files in file_path_dict.items():
        if not files:
            print(f" | No files found for {bucket} file types")
         
    return file_path_dict

def process_files(directory, file_path_dict, file_type, organisation, config):
    """   
    Derives relative path, file size, file name, sample name.
    Maps patient id to sample id.
    Writes above information into dictionary for each file.
    
    Args:
        directory (str): The directory to create relative path with
        file_path_dict (dict): Dictionary containing raw, processed, summarised as keys and file paths as values
        file_type (str): Specifies either raw, processed or summarised
        organization (str): Organization that the data files are from, can be modified in params.py
        cor_dict: The dictionary containing the keys as sample_id and values as patient_id
    
    Returns:
        list: A list of dictionaries summarising the file details.
    """
    patient_sample_mapping = config["patient_sample_mapping"]
    convert_from_bytes = 1024
    file_size_unit = "KB"
    file_list = []
    total_size = 0
    print(f"Processing the {file_type} files")

    for full_path in file_path_dict[file_type]:

        relative_path = full_path.relative_to(directory)
        file_path = f"./{relative_path.as_posix()}"
        file_size = round(os.path.getsize(full_path) / convert_from_bytes)
        total_size += file_size
        file_name = Path(full_path).name
        sample_name = Path(full_path).stem

        # establish file name
        metadata_dict = {
            "file_name": file_name,
            "file_size": file_size, 
            "patient_id": patient_sample_mapping.get(sample_name, ""),
            "sample_id": sample_name,
            "directory": file_path,
            "organization": organisation
        }

        print(f" | {file_path}  ~{file_size}{file_size_unit}")

        # check here to prevent duplicates
        if metadata_dict not in file_list:
            file_list.append(metadata_dict)

    print(f" | Total size for these files: {total_size}{file_size_unit}")
                        
    return file_list


def generate_json(directory, output_file, organisation):
    """
    Generates a JSON summary of files in the specified directory using RO‑Crate.
    The directory is recursively scanned for raw, processed, and summarised files.
    Each file is registered in the RO‑Crate with enriched metadata.
    
    Args:
        directory (str): The directory to analyze.
        output_file (str): The path where the JSON output will be saved.
    """
    if not directory.is_dir():
        raise ValueError(f"The specified path '{directory}' is not a valid directory.")
    
  
    # Load metadata from the provided metadata file.
    config = load_json(directory / "config.json")
    raw_file_extensions = config["raw_file_extensions"]
    processed_file_extensions = config["processed_file_extensions"]
    summarised_file_extensions = config["summarised_file_extensions"]
    file_size_unit = "KB"

    file_path_dict = find_files_via_extensions(directory, config)

    print(f"\nProcessing raw files ({', '.join(raw_file_extensions)})")
    raw_files = process_files(directory, file_path_dict, "raw", organisation, config) 

    print(f"\nProcessing processed files ({', '.join(processed_file_extensions)})")
    processed_files = process_files(directory, file_path_dict, "processed", organisation, config) 
   
    print(f"\nProcessing summarised files ({', '.join(summarised_file_extensions)})")
    summarised_files = process_files(directory, file_path_dict, "summarised", organisation, config)     
    # summarised_files = process_files_for_summarised(directory, SUMMARISED_FILE_TYPES, organization, cor_dict)
    
    # Build the final output structure.
    output_data = {
        "data": {
            "location": directory.as_posix(),
            "file_size_unit": file_size_unit,
            "files": {
                "raw": raw_files,
                "processed": processed_files,
                "summarised": summarised_files
            }
        }
    }
    
    
    # Write the custom JSON summary.
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=4)
    
    print(f"\nJSON file generated at: {output_file}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python update_local.py /path/to/files")
        sys.exit(1)
    
    # The target directory should be the 'files' subfolder.
    target_directory = Path(sys.argv[1])
    print(f"\nSearching through {target_directory} .........")
    
    # Determine output file paths relative to the script's directory.
    script_directory = Path(__file__).parent
    output_file_path = target_directory / "output.json"
    output_html_path = target_directory / "output.html"
    organisation = "WEHI"

    try:
        generate_json(target_directory, output_file_path, organisation)
        generate_html_from_json(output_file_path, output_html_path, organisation)
    except Exception as e:
        print(f"Error: {e}")
