import json
from pathlib import Path

from generate_html import generate_table, generate_html_from_json


def test_generate_table_empty_state():
    html = generate_table([], "raw")
    assert "No files found" in html


def test_generate_table_escapes_html():
    files = [{
        "file_name": "<script>alert(1)</script>.czi",
        "file_size": 1,
        "patient_id": "P<1>",
        "sample_id": "S&1",
        "directory": "./<bad>.czi",
    }]

    html = generate_table(files, "raw")

    # The table has legitimate JS <script> tags, so don't assert scripts don't exist.
    # Instead, assert that user-provided content is escaped.

    assert "&lt;script&gt;alert(1)&lt;/script&gt;.czi" in html
    assert "P&lt;1&gt;" in html
    assert "S&amp;1" in html
    assert "./&lt;bad&gt;.czi" in html

    # And ensure the raw unescaped user content is not present
    assert "<script>alert(1)</script>.czi" not in html
    assert "P<1>" not in html
    assert "S&1" not in html
    assert "./<bad>.czi" not in html

def test_generate_html_from_json_writes_file(tmp_path: Path):
    # minimal JSON structure expected by generate_html_from_json
    data = {
        "data": {
            "location": str(tmp_path),
            "files": {
                "raw": [{"file_name": "a.czi", "file_size": 1, "patient_id": "P1", "sample_id": "S1", "directory": "./a.czi"}],
                "processed": [],
                "summarised": [],
            },
        }
    }

    json_path = tmp_path / "output.json"
    html_path = tmp_path / "output.html"
    json_path.write_text(json.dumps(data))

    generate_html_from_json(json_path, html_path)

    assert html_path.exists()
    html = html_path.read_text(encoding="utf-8")
    assert "<title>Dashboard - Data Commons</title>" in html
    assert "Raw Files" in html
    assert "a.czi" in html
