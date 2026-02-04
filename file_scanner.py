import os
import json
import pandas as pd
from pathlib import Path

def extract_sample_name(filename, extensions):
    
    name = filename.lower()
    # Sort extensions by length so .fastq.gz is matched before .gz
    for ext in sorted(extensions, key=len, reverse=True):
        if name.endswith(ext.lower()):
            return filename[:-len(ext)]
    return os.path.splitext(filename)[0]

def identify_files(data_dir, config, organization):
    
    files_by_category = {
        "raw": [],
        "processed": [],
        "summarised": []
    }
    
    # Map extensions to category
    ext_map = {}
    
    for ext in config["raw_file_extensions"]:
        ext_map[ext.lower()] = "raw"
    for ext in config["processed_file_extensions"]:
        ext_map[ext.lower()] = "processed"
    for ext in config["summarised_file_extensions"]:
        ext_map[ext.lower()] = "summarised"
        
    all_exts = list(ext_map.keys())
    
    # Mapping: Config only
    sample_map = config.get("sample_to_patient", {})
    
    # Check for legacy mapping file to warn user
    mapping_file = data_dir / "patient_sample_mapping.json"
    if mapping_file.exists():
        print(f" | WARNING: Found 'patient_sample_mapping.json' in {data_dir}. "
              "This file is ignored. Please move mappings to 'config.json'.")

    counts_format = config.get("counts_format", False)
    
    total_size = 0

    print(f" | Scanning {data_dir}...")

    for path in data_dir.rglob("*"):
        if not path.is_file() or path.name.startswith("."):
            continue
            
        name_lower = path.name.lower()
        category = None
        
        # Match extension
        for ext in sorted(all_exts, key=len, reverse=True):
            if name_lower.endswith(ext):
                category = ext_map[ext]
                break
        
        if not category:
            continue
            
        # Metadata extraction
        size_kb = round(path.stat().st_size / 1024)
        total_size += size_kb
        
        sample_id = extract_sample_name(path.name, all_exts)
        patient_id = sample_map.get(sample_id, "")
        
        s_ids = [sample_id]
        p_ids = [patient_id] if patient_id else []

        # Summarised CSV/TSV/MAF handling
        if category == "summarised" and path.suffix in [".csv", ".tsv", ".maf"]:
            try:
                sep = "\t" if path.suffix in [".tsv", ".maf"] else ","
                # MAF comments usually start with #
                extra = {"comment": "#"} if path.suffix == ".maf" else {}

                # Read header only
                df = pd.read_csv(path, sep=sep, index_col=0, nrows=0, **extra)
                
                if counts_format:
                    # Counts format: Samples are columns
                    s_ids = list(df.columns)
                else:
                    # Standard format: Samples are columns after the first one?
                    # "Reads only the header row... and uses the column names after the first column as sample IDs."
                    # If we used index_col=0, df.columns already excludes the first column (the index).
                    if not df.columns.empty:
                        s_ids = list(df.columns)
                    else:
                         # Fallback to index if no columns found (single column file?), or maybe empty
                         pass

                # If we found sample IDs in the file, map them to patients
                # Otherwise, we keep the filename-derived s_ids
                if s_ids:
                    # Map resolved samples to patients
                    p_ids = sorted(list(set(sample_map.get(s, "") for s in s_ids if s in sample_map)))
                
            except Exception:
                pass # Fallback to filename-based ID

        # Format output fields
        final_sample = s_ids if len(s_ids) > 1 else s_ids[0]
        final_patient = p_ids if len(p_ids) > 1 else (p_ids[0] if p_ids else "")
        try:
            rel_path = f"./{path.relative_to(data_dir)}"
        except ValueError:
            rel_path = path.name

        files_by_category[category].append({
            "file_name": path.name,
            "file_size": size_kb,
            "directory": rel_path,
            "organization": organization,
            "sample_id": final_sample,
            "patient_id": final_patient
        })

    return files_by_category, total_size
