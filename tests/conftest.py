import json
from pathlib import Path
import pytest

@pytest.fixture
def sample_dir(tmp_path: Path) -> Path:
    """
    Creates a fake directory containing:
      - config.json
      - patient_sample_mapping.json
      - some raw/processed/summarised files in nested folders
    """
    # files layout
    (tmp_path / "nested").mkdir()

    config = {
        "raw_file_types": [".fastq", ".fasta"],
        "processed_file_types": [".cram", ".bam"],
        "summarised_file_types": [".vcf", ".maf", ".csv", ".tsv"],
    }
    (tmp_path / "config.json").write_text(json.dumps(config))

    mapping = {
        "SAMPLE_A": "PAT_1",
        "SAMPLE_B": "PAT_2",
        "SAMPLE_C": "PAT_2",
    }
    (tmp_path / "patient_sample_mapping.json").write_text(json.dumps(mapping))

    # raw
    (tmp_path / "SAMPLE_A.fastq").write_bytes(b"a" * 2048)  # 2 KB
    # processed
    (tmp_path / "nested" / "SAMPLE_B.bam").write_bytes(b"b" * 1024)  # 1 KB
    # summarised (note: for update_local_v1.process_files, it uses stem)
    (tmp_path / "nested" / "SAMPLE_C.csv").write_text("idx,val\nSAMPLE_A,1\nSAMPLE_B,2\n")
    (tmp_path / "nested" / "SAMPLE_D.tsv").write_text("idx\tval\nSAMPLE_A\t1\nSAMPLE_X\t2\n")

    # random ignored
    (tmp_path / "ignore.txt").write_text("nope")

    return tmp_path
