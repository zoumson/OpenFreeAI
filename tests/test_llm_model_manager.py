import pytest
from managers.llm_model_manager import LLMModelManager

@pytest.fixture
def temp_model_file(tmp_path):
    return tmp_path / "models.json"

def test_initial_models_load(temp_model_file):
    manager = LLMModelManager(file_path=temp_model_file)
    models = manager.get_models()
    # Check default providers exist
    assert "google" in models
    assert "openai" in models

def test_add_and_remove_model(temp_model_file):
    manager = LLMModelManager(file_path=temp_model_file)
    
    # Add a new model with full info
    provider = "custom"
    model_name = "model-1"
    tag = "free"
    full_model = f"{provider}/{model_name}:{tag}"
    
    # Add model
    assert manager.add_model(full_model=full_model, provider=provider, model_name=model_name, tag=tag) is True
    # Duplicate add returns False
    assert manager.add_model(full_model=full_model, provider=provider, model_name=model_name, tag=tag) is False

    # Check it exists
    models = manager.get_models()
    assert provider in models
    assert {"model": model_name, "tag": tag} in models[provider]

    # Remove model
    assert manager.remove_model(full_model=full_model) is True
    assert {"model": model_name, "tag": tag} not in manager.get_models().get(provider, [])
