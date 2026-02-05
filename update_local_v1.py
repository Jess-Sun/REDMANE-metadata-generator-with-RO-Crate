#!/usr/bin/env python3
import os
import json
from pathlib import Path
from generate_html import generate_html_from_json
import pandas as pd
import numpy as np



def extract_sample_name(filename, extensions):
    # Strip known extensions (longest first) from filename to get sample name
    name = filename.lower()
    # Sort extensions by length so .fastq.gz is matched before .gz
    for ext in sorted(extensions, key=len, reverse=True):
        if name.endswith(ext.lower()):
            return filename[:-len(ext)]
    return os.path.splitext(filename)[0]


def validate_directory_match(config, target_directory):
    # Ensure config directory matches target directory; warn if missing, fail if mismatched
    expected_dir = config.get("directory") or config.get("expected_directory")
    if not expected_dir:
        print(" | WARNING: config.json missing 'directory' (or 'expected_directory'); skipping directory match validation.")
        return
    if Path(expected_dir).resolve() != Path(target_directory).resolve():
        raise ValueError(
            f"Config directory mismatch: config.json has '{expected_dir}' but target_directory is '{target_directory}'."
        )


def load_json(file_path):
    """
    Load a JSON file from disk.

    This function reads a JSON file and returns its contents as a Python
    dictionary.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        dict: Parsed JSON content as a dictionary.
    """
    with open(file_path, "r") as f:
        data = json.load(f)
    return data


def find_files_via_extensions(directory, config):
    """
    Recursively scan a directory and group files by data stage based on
    file extensions defined in the config.

    Extensions listed under 'raw_file_extensions',
    'processed_file_extensions', and 'summarised_file_extensions' are used
    to categorise files.

    Args:
        directory (str): Root directory to search.
        config (dict): Config dictionary defining file extensions
            for raw, processed, and summarised data.

    Returns:
        dict: Mapping of data stages ('raw', 'processed', 'summarised') to
        lists of matching file paths.
    """
    bucket_by_ext: dict[str, str] = {}
    file_path_dict: dict[str, list[Path]] = {}

    for key, exts in config.items():
        if not key.endswith("_file_extensions"):
            continue

        bucket = key.replace("_file_extensions", "")  # e.g. "raw"
        file_path_dict[bucket] = []

        for ext in exts:
            bucket_by_ext[str(ext).lower()] = bucket

    # Walk and bucket files
    for root, _, files in os.walk(directory):
        for file in files:
            ext = Path(file).suffix.lower()
            bucket = bucket_by_ext.get(ext)
            if bucket is None:
                continue

            full_path = Path(root) / file
            file_path_dict[bucket].append(full_path)

    # Report empty buckets
    for bucket, files in file_path_dict.items():
        if not files:
            print(f" | No files found for {bucket} file types")

    return file_path_dict

def extract_file_metadata(directory, file_path_dict, file_type, organisation, config):
    """
    Extract metadata for files of a given type and return a summary list.

    For each file, this function derives the relative path, file name, file
    size, and sample identifier, and maps samples to patient IDs using the
    config.

    Args:
        directory (str): Root directory used to compute relative file paths.
        file_path_dict (dict): Dictionary containing file types ('raw', 'processed',
            'summarised') as keys and lists of file paths as values.
        file_type (str): File category to process ('raw', 'processed', 'summarised').
        organisation (str): Organisation associated with the data files.
        config (dict): Config dictionary containing 'patient_sample_mapping'.

    Returns:
        list[dict]: List of dictionaries summarising metadata for each file.
    """
    patient_sample_mapping = config["patient_sample_mapping"]
    convert_from_bytes = 1024
    file_size_unit = "KB"
    metadata_dict_by_path = {} # dictionary to prevent duplicates
    total_size = 0
    print(f"Processing the {file_type} files")

    for full_path in file_path_dict[file_type]:

        relative_path = full_path.relative_to(directory)
        file_path = f"./{relative_path.as_posix()}"
        file_size = round(os.path.getsize(full_path) / convert_from_bytes)
        total_size += file_size
        file_name = Path(full_path).name
        # Build a combined list of all known extensions
        all_exts = (
            config.get("raw_file_extensions", []) +
            config.get("processed_file_extensions", []) +
            config.get("summarised_file_extensions", [])
        )
        sample_name = extract_sample_name(file_name, all_exts)

        # establish file name
        metadata_dict_by_path[file_path] = {
            "file_name": file_name,
            "file_size": file_size, 
            "patient_id": patient_sample_mapping.get(sample_name, ""),
            "sample_id": sample_name,
            "directory": file_path,
            "organization": organisation
        }

        print(f" | {file_path}  ~{file_size}{file_size_unit}")

    print(f" | Total size for these files: {total_size}{file_size_unit}")

    file_list = list(metadata_dict_by_path.values())  

    return file_list


def generate_json(directory, output_file, organisation):
    """
    Generate a JSON summary of data files within a directory.

    The directory is recursively scanned for raw, processed, and summarised
    files using extension rules defined in a local configuration file
    ('config.json'). File metadata are collected and written to a structured
    JSON output.

    Args:
        directory (Path): Root directory to analyse.
        output_file (str): Path where the JSON output will be written.
        organisation (str): Organisation associated with the data files.
    """
    if not directory.is_dir():
        raise ValueError(f"The specified path '{directory}' is not a valid directory.")
    
  
    # Load metadata from the provided metadata file.
    config = load_json(directory / "config.json")
    validate_directory_match(config, directory)

    raw_file_extensions = config["raw_file_extensions"]
    processed_file_extensions = config["processed_file_extensions"]
    summarised_file_extensions = config["summarised_file_extensions"]
    file_size_unit = "KB"

    file_path_dict = find_files_via_extensions(directory, config)

    print(f"\nProcessing raw files ({', '.join(raw_file_extensions)})")
    raw_files = extract_file_metadata(directory, file_path_dict, "raw", organisation, config) 

    print(f"\nProcessing processed files ({', '.join(processed_file_extensions)})")
    processed_files = extract_file_metadata(directory, file_path_dict, "processed", organisation, config) 
   
    print(f"\nProcessing summarised files ({', '.join(summarised_file_extensions)})")
    summarised_files = extract_file_metadata(directory, file_path_dict, "summarised", organisation, config)     
    
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
