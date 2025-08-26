import pytest
import json
from pathlib import Path
from managers.resource_manager import ResourceManager


def test_save_and_load_json(tmp_path):
    file_path = tmp_path / "test.json"
    data = {"model": "gpt-5", "tokens": 1234}

    # Save
    ResourceManager.save_json(file_path, data)
    assert file_path.exists()

    # Load
    loaded = ResourceManager.load_json(file_path)
    assert loaded == data


def test_overwrite_existing_json(tmp_path):
    file_path = tmp_path / "test.json"
    data1 = {"a": 1}
    data2 = {"b": 2}

    ResourceManager.save_json(file_path, data1)
    ResourceManager.save_json(file_path, data2)

    loaded = ResourceManager.load_json(file_path)
    assert loaded == data2


def test_load_invalid_json(tmp_path):
    file_path = tmp_path / "invalid.json"
    file_path.write_text("{ invalid json }")  # corrupt file

    with pytest.raises(json.JSONDecodeError):
        ResourceManager.load_json(file_path)


def test_load_nonexistent_file(tmp_path):
    file_path = tmp_path / "does_not_exist.json"
    with pytest.raises(FileNotFoundError):
        ResourceManager.load_json(file_path)
