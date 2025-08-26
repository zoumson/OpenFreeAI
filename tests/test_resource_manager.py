import pytest
from managers.resource_manager import ResourceManager
import json

def test_save_and_load_json(tmp_path):
    file_path = tmp_path / "data.json"
    data = {"a": 1, "b": [1, 2, 3]}
    ResourceManager.save_json(file_path, data)
    
    loaded = ResourceManager.load_json(file_path)
    assert loaded == data
