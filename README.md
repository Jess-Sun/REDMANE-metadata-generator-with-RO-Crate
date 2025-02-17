# REDMANE-metadata-generator-with-RO-Crate
By REDMANE Data Injestion Team Summer 2025

## Overview

This project automates the organization and metadata enrichment of research files using RO-Crate, ensuring standardized, machine-readable data management. The script `update_local.py` scans files, associates metadata, and generates customised, structured outputs in JSON and HTML formats for easy access and visualization.

## Project Structure

- `files/` – Directory containing research data categorized as raw, processed, or summarized.
- `generate_html.py` – Converts the structured JSON summary into an HTML report.
- `params.py` – Stores configurable parameters such as metadata paths and file types.
- `sample_metadata.py` – Manages metadata for research files.
- `update_local.py` – Main script responsible for scanning, processing, and organizing files into an RO-Crate package.

## Usage

To run the script, use the following command:

```bash
python update_local.py /path/to/files
```

This will:
Scan the specified directory for raw, processed, and summarized files.
Extract metadata and associate it with the respective files.
Generate an RO-Crate package for structured data storage.
Create JSON and HTML reports summarizing the processed data.

## Requirements

Python 3.x
RO-Crate Python library
JSON and OS modules (included in Python standard library)

## Future Improvements

Implement logging for better debugging and error tracking.
Add a configuration file to customize parameters dynamically.
Enable parallel processing to handle large datasets efficiently.
Expand metadata handling to support additional research data formats.
