# REDMANE-metadata-generator
*Created by REDMANE Data Ingestion Team Summer 2025*  
*Updated by REDMANE Data Ingestion Team 2025 sem1*  
*Updated by REDMANE Data Ingestion Team Summer 2026*

A Python tool for finding files with certain extensions (specified in config file) and extracting metadata such as file name, file size and path. It also maps sampleID and patientID to the file if the mapping is supplied in the config file. It structures the summarised metadata into an output json and html preview. The output json can be uploaded to the data registry to update metadata for the associated dataset. 

## Overview

This project helps automate the ingestion of metadata associated with research datasets into the REDMANE data registry website. Just as a library catalogue tracks books across multiple physical locations without storing the books themselves, REDMANE tracks research data files across different organisations using the metadata while the actual files remain in their original locations. 
- The Data Registry stores only metadata (information about files such as size and location) while the data itself is stored locally with each organisation. 
- As new data is generated, from raw to processed to summarised versions, the metadata is updated in the registry so that researchers from different organisations that are collaborating can see the status and location of files. 
- There will be links from the registry to visualisation portals for easy viewing of summarised data once projects have been completed e.g. cBioPortal for genomics data and OMERO for imaging data. 
- There will also be links from the local directories to the data registry as well as links back from the portals to the registry so that the data is connected across all platforms and can be found regardless of where you start. 

## Related Repositories
- Data Registry Backend: https://github.com/WEHI-RCPStudentInternship/REDMANE_fastapi
- Data Registry Frontend: https://github.com/WEHI-RCPStudentInternship/REDMANE_react.js
- Docker Orchestration: https://github.com/WEHI-RCPStudentInternship/REDMANE_Docker

## Project Structure
```text
REDMANE-metadata-generator-with-RO-Crate/
├── .github/workflows/ci.yml   # GitHub Actions workflow for automated testing
├── test_counts/               # Synthetic test dataset containing raw, processed, and summarised files
├── test_imaging/              # Synthetic imaging test dataset containing raw, processed, and summarised files
├── test_WGS/                  # Synthetic whole genome sequencing (WGS) test dataset
├── tests/                     # Unit tests validating core functionality
├── generate_html.py           # Generates an HTML report from structured JSON summaries
├── pytest.ini                 # Pytest configuration and test discovery settings
├── update_local_v1.py         # Main metadata extraction and organisation pipeline
└── README.md
```


## Usage

To run the script, use the following command:

```bash
python update_local_v1.py /path/to/files
```

This will:
- Scan the specified directory for raw, processed, and summarized files.
- Extract metadata and associate it with the respective files.
- Create a HTML report that previews the summarised metadata.
- Create an output.json containing the metadata that is for uploading to the data registry to update the metadata associated with a dataset.

Required to run:
- Files in target directory
- config.json in target directory (see README in test_imaging or test_WGS for more details on config structure)
- target directory as CLI input

Output: (see test_imaging or test_WGS for examples)
- output.json (to be uploaded to data registry)
- output.html

E.g. to run with an included synthetic test data:
```bash
python update_local_v1.py ./test_imaging
```

## Requirements

- Python 3.x
- JSON, OS, RE, PATHLIB, CSV modules (included in Python standard library)

## Development Requirements
- PYTEST for automated unit testing and continuous integration validation

## Future Improvements

- Implement logging for better debugging and error tracking.
- Enable parallel processing to handle large datasets efficiently.
- Expand file handling to support additional research data formats.
- Create Python and R packages for easy install. 
- Rename repository to remove RO-CRATE which has been discontinued. 

### Notes
Repository was filtered and commit history rewritten to remove tracking of large files, if you have cloned the repository before you may need to reclone. 