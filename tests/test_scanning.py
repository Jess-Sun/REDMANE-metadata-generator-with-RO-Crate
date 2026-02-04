import pytest
from file_scanner import identify_files, extract_sample_name

def test_extract_sample_name():
    exts = [".fastq.gz", ".fastq"]
    assert extract_sample_name("sample1.fastq.gz", exts) == "sample1"
    assert extract_sample_name("sample2.fastq", exts) == "sample2"

def test_identify_files_structure(tmp_path):
    (tmp_path / "f.txt").touch()
    conf = {
        "raw_file_extensions": [".txt"],
        "processed_file_extensions": [],
        "summarised_file_extensions": [],
        "sample_to_patient": {"f": "p1"}
    }
    res, _ = identify_files(tmp_path, conf, "test")
    assert len(res["raw"]) == 1
    assert res["raw"][0]["sample_id"] == "f"
    assert res["raw"][0]["patient_id"] == "p1"

def test_identify_files_counts_tsv(tmp_path):
    (tmp_path / "c.tsv").write_text("ID\tS1\nG\t1", encoding="utf-8")
    conf = {
        "raw_file_extensions": [],
        "processed_file_extensions": [],
        "summarised_file_extensions": [".tsv"],
        "sample_to_patient": {"S1": "P1"},
        "counts_format": True
    }
    res, _ = identify_files(tmp_path, conf, "test")
    assert res["summarised"][0]["sample_id"] == "S1"

def test_identify_files_csv_header_logic(tmp_path):
    # Standard CSV, should now also read from header
    (tmp_path / "data.csv").write_text("Gene,S2,S3\nBRCA1,0,1", encoding="utf-8")
    conf = {
        "raw_file_extensions": [],
        "processed_file_extensions": [],
        "summarised_file_extensions": [".csv"],
        "sample_to_patient": {"S2": "P2", "S3": "P3"},
        "counts_format": False # Standard format
    }
    res, _ = identify_files(tmp_path, conf, "test")
    
    # helper to find the summarised file
    f = res["summarised"][0]
    # S2 and S3 should be detected from header
    # and matched to patients P2 and P3
    assert set(f["sample_id"]) == {"S2", "S3"}
    assert set(f["patient_id"]) == {"P2", "P3"}
