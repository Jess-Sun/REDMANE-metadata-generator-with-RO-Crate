# Metadata Generator

A Python tool for extracting structured file metadata from dataset directories and mapping sample IDs to patient IDs using a configurable JSON mapping.

Designed for testing, ingestion pipelines, and structured research data workflows.

## Overview

This tool scans structured directories (e.g. Raw/, Processed/, Summarised/), extracts sample identifiers from filenames using compiled regular expressions, maps them to patient identifiers via a JSON configuration file, and returns structured metadata dictionaries suitable for downstream processing or ingestion.

It is particularly useful for:

Dataset validation

File inventory generation

Sample-to-patient mapping

Pre-ingestion metadata preparation

Testing data pipelines with synthetic datasets

## Features

Regex-based sample ID extraction from filenames

Config-driven patient–sample mapping

Duplicate file prevention

File size calculation

Structured metadata output

Robust handling of unmatched filenames

## Installation

Clone the repository:

git clone https://github.com/username/repo.git
cd repo

Create virtual environment:

python -m venv venv
source venv/bin/activate



## Expected Directory Structure
```
dataset/
├── Raw/
│   ├── XY001-CDI.czi
│   ├── XY077-CDI.czi
│   └── ...
├── Processed/
├── Summarised/
└── patient_sample_mapping.json
```

## Usage
Import in Python
from metadata_generator import extract_file_metadata

file_list = extract_file_metadata(
    directory=dataset_path,
    file_path_dict=file_path_dict,
    file_type="raw",
    config=config
)

Command Line (if applicable)
python main.py --directory ./dataset --config config.json

## Example Output
{
  "file_name": "XY077-CDI.czi",
  "file_size": 5241,
  "patient_id": "PatientID077_DiseaseX",
  "sample_id": "XY077",
  "directory": "./Raw/XY077-CDI.czi"
}

## Error Handling

Files without valid sample IDs are skipped and reported.

Missing mappings return None unless explicitly enforced.

Duplicate file paths are prevented via dictionary indexing.

Regex patterns are compiled once for efficient matching.

## Design Principles

No assumptions are made about biological content — only file structure and naming conventions.

Deterministic sample ID extraction

Explicit configuration-driven mapping

Early failure detection for missing IDs

Clear separation between file discovery and metadata extraction

Readable, maintainable logic

## Requirements

Python 3.9+

Standard library only (re, pathlib, json, os)

(No external dependencies required.)

## License

MIT License