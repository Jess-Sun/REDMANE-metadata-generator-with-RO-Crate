import json
from pathlib import Path
import update_local_v1 as ul


def patch_params(monkeypatch):
    # size conversion used in process_files
    monkeypatch.setattr(ul, "CONVERT_FROM_BYTES", 1024)
    monkeypatch.setattr(ul, "FILE_SIZE_UNIT", "KB")

    # used in generate_json
    monkeypatch.setattr(ul, "ORGANIZATION", "WEHI")
    monkeypatch.setattr(ul, "RAW_FILE_TYPES", [".fastq", ".fasta"])
    monkeypatch.setattr(ul, "PROCESSED_FILE_TYPES", [".cram", ".bam"])
    monkeypatch.setattr(ul, "SUMMARISED_FILE_TYPES", [".cvf", ".maf", ".csv", ".tsv"])


def test_filter_files_buckets_existing_files(sample_dir, monkeypatch):
    """
    Ensures filter_files() puts files into the correct bucket based on config.json.
    Uses:
      - SAMPLE_A.fastq -> raw
      - nested/SAMPLE_B.bam -> processed
      - nested/SAMPLE_C.csv + nested/SAMPLE_D.tsv -> summarised
    """
    patch_params(monkeypatch)

    config = ul.load_json(sample_dir / "config.json")

    # This is where we call filter_files() and pass in the fake files
    file_path_dict = ul.filter_files(sample_dir, config)

    assert set(file_path_dict.keys()) == {"raw", "processed", "summarised"}

    raw_names = {p.name for p in file_path_dict["raw"]}
    processed_names = {p.name for p in file_path_dict["processed"]}
    summarised_names = {p.name for p in file_path_dict["summarised"]}

    assert raw_names == {"SAMPLE_A.fastq"}
    assert processed_names == {"SAMPLE_B.bam"}
    assert summarised_names == {"SAMPLE_C.csv", "SAMPLE_D.tsv"}


def test_filter_files_ignores_unknown_extensions(sample_dir, monkeypatch):
    """
    This function is just making sure that we do not accept file extensions that we should not
    be accepting.
    """
    patch_params(monkeypatch)

    config = ul.load_json(sample_dir / "config.json")
    file_path_dict = ul.filter_files(sample_dir, config)

    all_names = {p.name for bucket in file_path_dict.values() for p in bucket}
    assert "ignore.txt" not in all_names


def test_filter_files_finds_nested_processed_file(sample_dir, monkeypatch):
    """
    Makes sure we are able to handle nested files
    """
    patch_params(monkeypatch)

    config = ul.load_json(sample_dir / "config.json")
    file_path_dict = ul.filter_files(sample_dir, config)

    # should find nested/SAMPLE_B.bam specifically
    processed_paths = {p.as_posix() for p in file_path_dict["processed"]}
    assert any(path.endswith("/nested/SAMPLE_B.bam") or path.endswith("\\nested\\SAMPLE_B.bam") for path in processed_paths)
