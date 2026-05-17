# conftest.py (configuration test, called to mock up test data, must be called conftest for pytest)
import json
from pathlib import Path
import pytest


@pytest.fixture
def sample_dir(tmp_path: Path) -> Path:
    """
    Creates a fake directory containing:
      - config.json (new schema: *_file_extensions + patient_sample_mapping)
      - some raw/processed/summarised files in nested folders

    Matches update_local_v1.py expectations.
    """
    # Create nested structure
    (tmp_path / "nested").mkdir()

    config = {
        # This is used by validate_directory_match(). Run tests from a cwd
        # where this resolves to tmp_path / "test_imaging" if needed.
        "directory": tmp_path.as_posix(),

        "raw_file_extensions": [".czi"],
        "processed_file_extensions": [".tif"],
        "summarised_file_extensions": [".zarr"],

        "patient_sample_mapping": {
            "XY001": "PatientID001_DiseaseX",
            "XY002": "PatientID002_DiseaseX",
            "XY003": "PatientID003_DiseaseX",
        },
    }

    (tmp_path / "config.json").write_text(json.dumps(config))

    # raw file (contains XY001 in name)
    (tmp_path / "XY001_raw.czi").write_bytes(b"a" * 2048)  # 2 KB

    # processed file nested (contains XY002 in name)
    (tmp_path / "nested" / "XY002_processed.tif").write_bytes(b"b" * 1024)  # 1 KB

    # summarised files nested (contains XY003 in name)
    (tmp_path / "nested" / "XY003_summary.zarr").write_bytes(b"c" * 3072)  # 3 KB

    # Unknown extension should be ignored by find_files_via_extensions()
    (tmp_path / "ignore.txt").write_text("nope")

    return tmp_path
