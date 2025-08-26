import os
import json
import pytest
from managers.model_manager import LLMModelManager

def test_add_and_remove_model():
    manager = LLMModelManager()

    # Add a new model
    assert manager.add_model("my-model")
    assert "my-model" in manager.get_models()

    # Prevent duplicate
    assert not manager.add_model("my-model")

    # Remove model
    assert manager.remove_model("my-model")
    assert "my-model" not in manager.get_models()

def test_export_and_load(tmp_path):
    manager = LLMModelManager(["model-a", "model-b"])
    
    # Export to file
    file_path = tmp_path / "models.json"
    manager.export_to_file(file_path)
    assert os.path.exists(file_path)

    # Read raw JSON to verify
    with open(file_path) as f:
        data = json.load(f)
    assert data == ["model-a", "model-b"]

    # Load back into a new manager
    manager2 = LLMModelManager()
    manager2.load_from_file(file_path)
    assert manager2.get_models() == ["model-a", "model-b"]
