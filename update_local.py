#!/usr/bin/env python3
import os
import json
from pathlib import Path
from rocrate.rocrate import ROCrate
from params import *  # Expects definitions for METADATA, RAW_FILE_TYPES, etc.
from generate_html import generate_html_from_json

def load_metadata(file_path):
    """
    Loads metadata from the JSON file and returns a dictionary keyed by the "Patient ID".
    For example, if an entry has "Patient ID": "ICGC_0001", then a file named "ICGC_0001.fastq" 
    will use that record.
    
    Args:
        file_path (str): Path to the metadata JSON file.
    
    Returns:
        dict: Mapping from "Patient ID" to the metadata entry.
    """
    with open(file_path, "r") as f:
        data = json.load(f)
    metadata_dict = {}
    for entry in data:
        key = entry.get("Patient ID")
        if key:
            metadata_dict[key] = entry
    return metadata_dict

def process_files_for_category(directory, file_types, metadata_dict, crate):
    """
    Recursively scans the given directory for files whose names end with one of the specified file_types.
    Each found file is registered in the RO‑Crate with enriched properties.
    The file’s base name (without extension) is used to look up its metadata record.
    
    Args:
        directory (str): The directory to search.
        file_types (list): List of file extensions to match.
        metadata_dict (dict): Dictionary mapping "Patient ID" to metadata entries.
        crate (ROCrate): The RO‑Crate instance in which to register files.
    
    Returns:
        list: A list of dictionaries summarizing the file details.
    """
    file_list = []
    total_size = 0

    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in file_types):
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, directory)
                file_path = f"./{relative_path}"
                file_size = round(os.path.getsize(full_path) / CONVERT_FROM_BYTES)
                total_size += file_size

                # Use the file's base name (without extension) as the key for metadata lookup.
                base_name, _ = os.path.splitext(file)
                metadata_entry = metadata_dict.get(base_name, {})
                patient_id = metadata_entry.get("Patient ID", "")
                sample_id = metadata_entry.get("Sample ID", "")

                # Register the file in the RO‑Crate with enriched properties.
                crate.add_file(full_path, properties={
                    "fileSize": f"{file_size}{FILE_SIZE_UNIT}",
                    "patient_id": patient_id,
                    "sample_id": sample_id,
                })

                file_dict = {
                    "file_name": file,
                    "file_size": file_size,
                    "patient_id": patient_id,
                    "sample_id": sample_id,
                    "directory": file_path
                }
                print(f" | {file_path}  ~{file_size}{FILE_SIZE_UNIT}")
                file_list.append(file_dict)
    
    if not file_list:
        print(" | No files found for file types:", file_types)
    else:
        print(f" | Total size for these files: {total_size}{FILE_SIZE_UNIT}")
    
    return file_list

def generate_json(directory, output_file):
    """
    Generates a JSON summary of files in the specified directory using RO‑Crate.
    The directory is recursively scanned for raw, processed, and summarised files.
    Each file is registered in the RO‑Crate with enriched metadata.
    
    Args:
        directory (str): The directory to analyze.
        output_file (str): The path where the JSON output will be saved.
    """
    if not os.path.isdir(directory):
        raise ValueError(f"The specified path '{directory}' is not a valid directory.")
    
    # Create a new RO‑Crate instance and set top-level metadata.
    crate = ROCrate()
    crate.root_dataset.name = "Research Object"
    crate.root_dataset.description = f"Research object created from files in {directory}"
    
    # Load metadata from the provided metadata file.
    metadata_dict = load_metadata(METADATA)
    
    print(f"\nProcessing raw files ({', '.join(RAW_FILE_TYPES)})")
    raw_files = process_files_for_category(directory, RAW_FILE_TYPES, metadata_dict, crate)
    
    print(f"\nProcessing processed files ({', '.join(PROCESSED_FILE_TYPES)})")
    processed_files = process_files_for_category(directory, PROCESSED_FILE_TYPES, metadata_dict, crate)
    
    print(f"\nProcessing summarised files ({', '.join(SUMMARISED_FILE_TYPES)})")
    summarised_files = process_files_for_category(directory, SUMMARISED_FILE_TYPES, metadata_dict, crate)
    
    # Build the final output structure.
    output_data = {
        "data": {
            "location": directory,
            "file_size_unit": FILE_SIZE_UNIT,
            "files": {
                "raw": raw_files,
                "processed": processed_files,
                "summarised": summarised_files
            }
        }
    }
    
    # Write out the full RO‑Crate package to a folder (e.g. "rocrate").
    rocrate_folder = Path(output_file).parent / "rocrate"
    crate.write(rocrate_folder)
    print(f"RO‑Crate written to {rocrate_folder}")
    
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
    target_directory = sys.argv[1]
    print(f"\nSearching through {target_directory} .........")
    
    # Determine output file paths relative to the script's directory.
    script_directory = Path(__file__).parent
    output_file_path = script_directory / OUTPUT_JSON_FILE_NAME
    output_html_path = script_directory / OUTPUT_HTML_FILE_NAME
    
    try:
        generate_json(target_directory, output_file_path)
        generate_html_from_json(output_file_path, output_html_path)
    except Exception as e:
        print(f"Error: {e}")
