#!/usr/bin/env python3
import os
import json
import re
from pathlib import Path
import csv
from generate_html import generate_html_from_json


def validate_directory_match(config, target_directory):
    """
    Validate that the directory specified in the config matches the
    provided target directory.

    If "directory" does not exists in the config, a warning is printed 
    and validation is skipped. If the paths do not match, a ValueError is raised.

    Args:
        config (dict): Configuration dictionary.
        target_directory (str or Path): Directory being processed.

    Raises:
        ValueError: If the config directory and target_directory differ.
    """
    # Ensure config directory matches target directory; warn if missing, fail if mismatched
    expected_dir = config.get("directory")
    if not expected_dir:
        print(" | WARNING: config.json missing 'directory'; skipping directory match validation.")
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


def check_config(config):
    """
    Validate config.json has required keys and expected types.
    Raises ValueError on any invalid/missing config (fail loudly).
    Returns the normalized config dict.
    """
    required = [
        "raw_file_extensions",
        "processed_file_extensions",
        "summarised_file_extensions",
        "patient_sample_mapping",
    ]
    missing = [req_key for req_key in required if req_key not in config]
    if missing:
        raise ValueError(f"config.json missing required keys: {missing}")

    # Validate extension lists
    for extension_key in ["raw_file_extensions", "processed_file_extensions", "summarised_file_extensions"]:
        extension_list = config[extension_key]
        if not isinstance(extension_list, list) or len(extension_list) == 0:
            raise ValueError(f"config key '{extension_key}' must be a non-empty list")
        # Optional: ensure list entries are strings (still minimal)
        for extension_string in extension_list:
            if not isinstance(extension_string, str):
                raise ValueError(f"config key '{extension_key}' must contain only strings (invalid: {extension_string})")

    # Validate mapping
    mapping_dict = config["patient_sample_mapping"]
    if not isinstance(mapping_dict, dict) or len(mapping_dict) == 0:
        raise ValueError("config key 'patient_sample_mapping' must be a non-empty dictionary")

    return config


def extract_sample_ids_from_counts_file(file_path: Path, sample_id_regex: re.Pattern) -> list[str]:
    """
    Scan a CSV/TSV file for sample IDs in the header row and first column.
    Returns a list of matching sample IDs (deduplicated).
    Only supports .csv and .tsv.
    """
    matches: set[str] = set()
    suffix = file_path.suffix.lower()
    if suffix not in (".csv", ".tsv"):
        return []

    delimiter = "\t" if suffix == ".tsv" else ","

    try:
        with open(file_path, "r", newline="") as f:
            reader = csv.reader(f, delimiter=delimiter)

            header = next(reader, [])
            for cell in header:
                regex_match = sample_id_regex.search(str(cell))
                if regex_match:
                    matches.add(regex_match.group())

            # Scan first column of up to first 100 rows (performance bound)
            for row_index, row in enumerate(reader):
                if row_index >= 100:
                    break
                if not row:
                    continue
                regex_match = sample_id_regex.search(str(row[0]))
                if regex_match:
                    matches.add(regex_match.group())

    except Exception:
        return []

    return list(matches)


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

def extract_file_metadata(directory, file_path_dict, file_type, config):
    """
    Extract metadata for files of a given type and return a summary list.

    For each file, this function derives the relative path, file name, file
    size, and maps files to sample and patient IDs using the config.

    Args:
        directory (str): Root directory used to compute relative file paths.
        file_path_dict (dict): Dictionary containing file types ('raw', 'processed',
            'summarised') as keys and lists of file paths as values.
        file_type (str): File category to process ('raw', 'processed', 'summarised').
        config (dict): Config dictionary containing 'patient_sample_mapping'.

    Returns:
        list[dict]: List of dictionaries summarising metadata for each file.
    """
    patient_sample_mapping = config["patient_sample_mapping"]
    convert_from_bytes = 1024
    file_size_unit = "KB"
    metadata_dict_by_path = {} # Dictionary to prevent duplicates
    total_size = 0
    # Regex pattern for matching sampleID to file name
    all_sample_ids = re.compile("|".join(map(re.escape, patient_sample_mapping.keys())))

    for full_path in file_path_dict[file_type]:

        relative_path = full_path.relative_to(directory)
        file_path = f"./{relative_path.as_posix()}"
        file_size = round(os.path.getsize(full_path) / convert_from_bytes)
        total_size += file_size
        file_name = Path(full_path).name
        
        # Regex matching of sampleID and patientID to file name
        match = all_sample_ids.search(file_name)

        # If no regex match in filename, attempt to detect sample IDs inside counts files
        if not match:
            if file_type == "summarised":
                found_ids = extract_sample_ids_from_counts_file(full_path, all_sample_ids)
                if found_ids:
                    sorted_ids = sorted(found_ids)
                    mapped_patient_ids = [patient_sample_mapping.get(sid, "") for sid in sorted_ids]
                    metadata_dict_by_path[file_path] = {
                        "file_name": file_name,
                        "file_size": file_size,
                        "patient_id": mapped_patient_ids,
                        "sample_id": sorted_ids,
                        "directory": file_path
                    }
                    print(f" | {file_path}  ~{file_size}{file_size_unit}")
                    # We have recorded metadata entries for this file, so skip the default path
                    continue

            print("SampleID NOT FOUND for file:", file_name)
            continue
        sample_id = match.group()
        patient_id = patient_sample_mapping.get(sample_id)

        # Record metadata for each file
        metadata_dict_by_path[file_path] = {
            "file_name": file_name,
            "file_size": file_size, 
            "patient_id": patient_id,
            "sample_id": sample_id,
            "directory": file_path
        }

        print(f" | {file_path}  ~{file_size}{file_size_unit}")

    print(f" | Total size for these files: {total_size}{file_size_unit}")

    file_list = list(metadata_dict_by_path.values())  

    return file_list


def generate_json(directory, output_file):
    """
    Generate a JSON summary of data files within a directory.

    The directory is recursively scanned for raw, processed, and summarised
    files using extension rules defined in a local configuration file
    ('config.json'). File metadata are collected and written to a structured
    JSON output.

    Args:
        directory (Path): Root directory to analyse.
        output_file (str): Path where the JSON output will be written.
    """
    if not directory.is_dir():
        raise ValueError(f"The specified path '{directory}' is not a valid directory.")
    
  
    # Load config information from the provided config file.
    config = load_json(directory / "config.json")
    config = check_config(config)
    validate_directory_match(config, directory)

    raw_file_extensions = config["raw_file_extensions"]
    processed_file_extensions = config["processed_file_extensions"]
    summarised_file_extensions = config["summarised_file_extensions"]
    file_size_unit = "KB"

    # Scan directory for files of interest
    file_path_dict = find_files_via_extensions(directory, config)

    # Generate metadata for each category of files
    print(f"\nProcessing raw files ({', '.join(raw_file_extensions)})")
    raw_files = extract_file_metadata(directory, file_path_dict, "raw", config) 

    print(f"\nProcessing processed files ({', '.join(processed_file_extensions)})")
    processed_files = extract_file_metadata(directory, file_path_dict, "processed", config) 
   
    print(f"\nProcessing summarised files ({', '.join(summarised_file_extensions)})")
    summarised_files = extract_file_metadata(directory, file_path_dict, "summarised", config)     
    
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
    
    target_directory = Path(sys.argv[1])
    print(f"\nSearching through {target_directory} .........")
    
    # Determine output file paths relative to the script's directory.
    script_directory = Path(__file__).parent
    output_file_path = target_directory / "output.json"
    output_html_path = target_directory / "output.html"

    try:
        generate_json(target_directory, output_file_path)
        # Create html preview of json contents
        generate_html_from_json(output_file_path, output_html_path)
    except Exception as e:
        print(f"Error: {e}")
