import json
from pathlib import Path

import pytest

import update_local_v1 as ul


def test_find_files_via_extensions_buckets_files(sample_dir: Path):
    config = ul.load_json(sample_dir / "config.json")

    file_path_dict = ul.find_files_via_extensions(sample_dir, config)

    assert set(file_path_dict.keys()) == {"raw", "processed", "summarised"}

    raw_names = {p.name for p in file_path_dict["raw"]}
    processed_names = {p.name for p in file_path_dict["processed"]}
    summarised_names = {p.name for p in file_path_dict["summarised"]}

    assert raw_names == {"XY001_raw.czi"}
    assert processed_names == {"XY002_processed.tif"}
    assert summarised_names == {"XY003_summary.zarr"}


def test_find_files_via_extensions_ignores_unknown_extensions(sample_dir: Path):
    config = ul.load_json(sample_dir / "config.json")
    file_path_dict = ul.find_files_via_extensions(sample_dir, config)

    all_names = {p.name for bucket in file_path_dict.values() for p in bucket}
    assert "ignore.txt" not in all_names


def test_extract_file_metadata_skips_when_sample_id_missing(tmp_path: Path, capsys):
    # Config mapping only contains XY001
    config = {"patient_sample_mapping": {"XY001": "PatientID001_DiseaseX"}}

    # File name does NOT contain XY001 -> should be skipped
    f = tmp_path / "NO_MATCH_raw.czi"
    f.write_bytes(b"x" * 1024)

    file_path_dict = {"raw": [f]}
    out = ul.extract_file_metadata(tmp_path, file_path_dict, "raw", config)

    captured = capsys.readouterr().out
    assert "SampleID NOT FOUND" in captured
    assert out == []


def test_extract_file_metadata_fields_and_relative_path(sample_dir: Path):
    config = ul.load_json(sample_dir / "config.json")
    file_path_dict = ul.find_files_via_extensions(sample_dir, config)

    raw_list = ul.extract_file_metadata(sample_dir, file_path_dict, "raw", config)

    assert len(raw_list) == 1
    item = raw_list[0]

    assert item["file_name"] == "XY001_raw.czi"
    assert item["sample_id"] == "XY001"
    assert item["patient_id"] == "PatientID001_DiseaseX"
    assert item["directory"] == "./XY001_raw.czi"
    # size is in KB, rounded
    assert isinstance(item["file_size"], int)


def test_generate_json_writes_expected_schema(sample_dir: Path):
    out_path = sample_dir / "output.json"
    ul.generate_json(sample_dir, out_path)

    assert out_path.exists()

    data = json.loads(out_path.read_text())
    assert "data" in data
    assert data["data"]["location"] == sample_dir.as_posix()
    assert data["data"]["file_size_unit"] == "KB"
    assert set(data["data"]["files"].keys()) == {"raw", "processed", "summarised"}

    # sanity check file counts from our fixture
    assert len(data["data"]["files"]["raw"]) == 1
    assert len(data["data"]["files"]["processed"]) == 1
    assert len(data["data"]["files"]["summarised"]) == 1
