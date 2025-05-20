# REDMANE-metadata-generator-with-RO-Crate
*Created by REDMANE Data Ingestion Team Summer 2025*\n
*Updated by REDMANE Data Ingestion Team 2025 sem1*

## Overview

This project automates the organization and metadata enrichment of research files using RO-Crate, ensuring standardized, machine-readable data management. The script `update_local.py` scans files, associates metadata, and generates customised, structured outputs in JSON and HTML formats for easy access and visualization.

## Project Structure

- `files/` – Directory containing research data categorized as raw, processed, or summarized.
- `generate_html.py` – Converts the structured JSON summary into an HTML report.
- `params.py` – Stores configurable parameters such as metadata paths and file types.
- `sample_metadata/` – All of the metadata and relevant necessary files are stored in this folder.
- `update_local_v1.py` – Main script responsible for scanning, processing, and organizing files into an RO-Crate package.

## Usage

To run the script, use the following command:

```bash
python update_local_v1.py /path/to/files
```

This will:
- Scan the specified directory for raw, processed, and summarized files.
- Extract metadata and associate it with the respective files.
- Generate an RO-Crate package for structured data storage.
- Create JSON and HTML reports summarizing the processed data.

## Requirements

- Python 3.x
- RO-Crate Python library
- JSON and OS modules (included in Python standard library)
- Pandas
- Numpy

## Pros & Cons of the Implementation

### ✅ Pros:

1. **Better Metadata Integration**  
   - The script loads metadata once using `load_metadata(file_path)` and stores it in a dictionary (`metadata_dict`) with **Patient ID** as the key.  
   - This approach allows for efficient lookups when processing files, reducing redundant operations.
   - The script also loads the mapping information between samples and patients `load_sample_tb(file_path)` and stores it in a dictionary.

2. **RO-Crate Support**  
   - The integration of **RO-Crate** ensures that the dataset is well-structured and adheres to **FAIR principles** (Findable, Accessible, Interoperable, Reusable).  
   - This standardization enhances data discoverability and facilitates better research data management.

3. **More Efficient File Processing**  
   - The function `process_files_for_raw()`, `process_files_for_summarized()`, `process_files_for_processed()` streamlines file processing by:  
     - Scanning for files  
     - Retrieving metadata  
     - Registering files in the **RO-Crate**
     - Tailored function for different data types
   - Performing these tasks in a single step improves efficiency.

4. **More Robust Error Handling**  
   - The script includes checks for missing metadata, incorrect file formats, and unexpected directory structures.  
   - Future improvements may incorporate logging for better debugging.

5. **Easier Extensibility**  
   - The modular design allows for future enhancements, such as:  
     - Adding new file properties (e.g., **timestamps**, **data types**, **metadata categories**)  
     - Expanding metadata handling to support additional research data formats  

### ❌ Cons:

1. **Dependency on RO-Crate**  
   - Using RO-Crate introduces external dependencies, requiring installation and configuration.  
   - This may add complexity for users unfamiliar with the framework.

2. **Harder to Debug**  
   - RO-Crate's internal mechanisms can obscure debugging, making it challenging to trace errors in metadata handling.  
   - Improved logging and debugging tools may help mitigate this issue.

3. **Alternative Simplicity (Non-RO-Crate Approach)**  
   - A simpler version of the script (without RO-Crate) would:  
     - Be easier to understand and modify due to its shorter codebase.  
     - Reduce overhead by eliminating the need for additional dependencies.  
     - Use straightforward file-matching logic to append `patient_id` and `sample_id` without requiring a structured metadata format.  

While **RO-Crate provides powerful metadata management and standardization**, a simpler approach may be preferable for smaller projects with fewer constraints on structured data handling.

## Future Improvements

- Implement logging for better debugging and error tracking.
- Add a configuration file to customize parameters dynamically.
- Enable parallel processing to handle large datasets efficiently.
- Expand metadata handling to support additional research data formats.
