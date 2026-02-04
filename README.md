# Redmane Metadata Generator

Organise and enrich research files with metadata.

## Features
- **Strict Configuration**: Validates `config.json` against a unified schema.
- **Unified Mapping**: All patient-sample mappings must be defined in `config.json`.
- **Flexible Scanning**: Robust sample ID extraction and categorisation.
- **Summarised Data**: Intelligent header-based parsing for CSV, TSV, and MAF formats.
- **Counts Matrices**: Supports CSV/TSV counts tables (samples in header) via CLI flag.
- **Static Reports**: Generates self-contained HTML reports.

## Usage

1. Create `config.json` in your dataset directory:
   ```json
   {
       "raw_file_extensions": [".fastq", ".fastq.gz"],
       "processed_file_extensions": [".bam"],
       "summarised_file_extensions": [".vcf", ".maf", ".tsv"],
       "sample_to_patient": {"SampleID": "PatientID"}
   }
   ```
   ```
   *(Note: Aliases like `raw_file_types` are supported with warnings.)*

   **Note**: Users can open `config.json` in their dataset directory to see and adjust the lists of `raw_file_extensions`, `processed_file_extensions`, and `summarised_file_extensions`.

2. Run the script:
   ```bash
   python update_local_v1.py /path/to/dataset --verbose
   ```

   **Options**:
   - `--counts-tsv`: Treat CSV/TSV files as counts matrices (Sample IDs in header).

3. Check `output.html` in the dataset directory.

## Requirements
- Python 3
- Pandas
