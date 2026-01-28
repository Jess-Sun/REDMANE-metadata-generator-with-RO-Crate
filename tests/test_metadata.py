import json
from pathlib import Path

from update_local_v1 import load_metadata, load_sample_tb

    """
    Verifies that load_metadata():
    - correctly loads a JSON list of metadata records
    - uses the "Patient ID" field as the dictionary key
    - preserves the full metadata entry as the value

    This is the test for valid metadata input.
    """
def test_load_metadata_keys_by_patient_id(tmp_path: Path):
    p = tmp_path / "sample_metadata.json"
    p.write_text(json.dumps([
        {"Patient ID": "ICGC_0001", "foo": 1},
        {"Patient ID": "ICGC_0002", "bar": 2},
    ]))

    out = load_metadata(str(p))
    assert set(out.keys()) == {"ICGC_0001", "ICGC_0002"}
    assert out["ICGC_0001"]["foo"] == 1
    assert out["ICGC_0002"]["bar"] == 2

    """
    Verifies that load_metadata():
    - ignores entries that do not contain a valid "Patient ID"
    - does not include empty or missing IDs in the output mapping

    This ensures robustness against malformed or incomplete metadata records.
    """
def test_load_metadata_ignores_missing_patient_id(tmp_path: Path):
    p = tmp_path / "sample_metadata.json"
    p.write_text(json.dumps([
        {"Patient ID": "ICGC_0001"},
        {"foo": "no id"},
        {"Patient ID": ""},  # empty id should be ignored
    ]))

    out = load_metadata(str(p))
    assert set(out.keys()) == {"ICGC_0001"}

    """
    Verifies that load_sample_tb():
    - loads the sample-to-patient JSON file correctly
    - returns the data unchanged as a dictionary

    This function is intentionally thin, so the test focuses on correctness
    rather than transformation.
    """
def test_load_sample_tb_returns_mapping(tmp_path: Path):
    p = tmp_path / "sample_to_patient.json"
    p.write_text(json.dumps({"S1": "P1", "S2": "P2"}))

    out = load_sample_tb(str(p))
    assert out == {"S1": "P1", "S2": "P2"}
